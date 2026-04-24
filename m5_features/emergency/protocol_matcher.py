"""
Emergency Protocol Matcher — Matches voice input to the best emergency protocol.

Uses a combination of:
1. Keyword matching (fast, offline)
2. Gemini AI matching (accurate, comprehensive)
to identify which emergency protocol best fits the described situation.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import redis.asyncio as redis

from m5_features.config import settings
from m5_features.ai.gemini_client import gemini_client

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Result of protocol matching."""

    matched: bool = False
    protocol_id: Optional[str] = None
    protocol_title: Optional[str] = None
    confidence: float = 0.0
    reasoning: Optional[str] = None
    protocol_data: Optional[dict] = None
    method: str = "none"  # "keyword", "ai", or "none"


class ProtocolMatcher:
    """
    Emergency protocol matcher with dual-strategy matching.

    Loads all 15 emergency protocol JSONs and provides methods
    to match voice transcriptions or text descriptions to the
    most appropriate protocol.
    """

    def __init__(self):
        """Initialize and load all protocol files."""
        self.protocols: dict[str, dict] = {}
        self._load_protocols()

    def _load_protocols(self) -> None:
        """
        Load all protocol JSON files from the protocols directory.

        Each file is loaded and indexed by its 'id' field for
        fast lookup during matching.
        """
        protocols_dir = Path(settings.PROTOCOLS_DIR)

        if not protocols_dir.exists():
            logger.warning(f"Protocols directory not found: {protocols_dir}")
            return

        json_files = list(protocols_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} protocol files")

        for filepath in json_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    protocol = json.load(f)
                protocol_id = protocol.get("id", filepath.stem)
                self.protocols[protocol_id] = protocol
                logger.debug(f"Loaded protocol: {protocol_id}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {filepath}: {e}")
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")

        logger.info(f"Loaded {len(self.protocols)} emergency protocols")

    async def sync_with_redis(self) -> None:
        """
        Synchronize loaded protocols with Redis cache.
        
        If Redis has the protocols, load them from Redis (for distributed speed).
        If Redis is empty, push the locally loaded JSON protocols to Redis.
        Fails gracefully if Redis is unavailable.
        """
        if not settings.REDIS_URL:
            logger.info("REDIS_URL not configured. Skipping Redis synchronization.")
            return

        try:
            r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            
            # Check if protocols exist in Redis
            cached_protocols = await r.hgetall("pulse:protocols")
            
            if cached_protocols:
                logger.info(f"Found {len(cached_protocols)} protocols in Redis. Loading from cache.")
                for protocol_id, protocol_json in cached_protocols.items():
                    try:
                        self.protocols[protocol_id] = json.loads(protocol_json)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in Redis cache for protocol {protocol_id}")
            else:
                logger.info("Redis cache empty. Pushing local protocols to Redis.")
                if self.protocols:
                    mapping = {
                        pid: json.dumps(p_data) 
                        for pid, p_data in self.protocols.items()
                    }
                    await r.hset("pulse:protocols", mapping=mapping)
                    logger.info(f"Successfully pushed {len(self.protocols)} protocols to Redis.")
                    
            await r.aclose()
        except Exception as e:
            logger.error(f"Redis synchronization failed: {e}. Falling back to local protocols.")

    def get_all_protocol_ids(self) -> list[str]:
        """Return a list of all available protocol IDs."""
        return list(self.protocols.keys())

    def get_all_protocol_summaries(self) -> list[dict]:
        """Return a summary of all protocols for frontend display."""
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "category": p.get("category", "general"),
                "severity_level": p.get("severity_level", 3),
                "call_ambulance": p.get("call_ambulance", True),
                "trigger_phrases": p.get("trigger_phrases", []),
            }
            for p in self.protocols.values()
        ]

    def get_protocol(self, protocol_id: str) -> Optional[dict]:
        """Get a specific protocol by its ID."""
        return self.protocols.get(protocol_id)

    def match(self, text: str) -> MatchResult:
        """
        Match input text to the best emergency protocol.

        Strategy:
        1. First try keyword matching (fast, works offline)
        2. If keyword match has low confidence, use Gemini AI
        3. Return the best match from either method

        Args:
            text: Transcribed voice text or typed emergency description

        Returns:
            MatchResult with the best matching protocol
        """
        if not text or not text.strip():
            return MatchResult()

        text_lower = text.lower().strip()

        # Strategy 1: Keyword matching
        keyword_result = self._match_keywords(text_lower)

        # If keyword match is strong (>0.7), return immediately
        if keyword_result.confidence >= 0.7:
            keyword_result.protocol_data = self.protocols.get(
                keyword_result.protocol_id
            )
            return keyword_result

        # Strategy 2: AI matching (if available)
        ai_result = self._match_with_ai(text)

        # Return the higher-confidence result
        if ai_result and ai_result.confidence > keyword_result.confidence:
            ai_result.protocol_data = self.protocols.get(
                ai_result.protocol_id
            )
            return ai_result

        # Fall back to keyword match
        if keyword_result.matched:
            keyword_result.protocol_data = self.protocols.get(
                keyword_result.protocol_id
            )
        return keyword_result

    def _match_keywords(self, text: str) -> MatchResult:
        """
        Match using trigger phrases defined in each protocol.

        Scoring:
        - Exact trigger phrase match = high confidence
        - Partial word overlap = proportional confidence
        """
        best_match = MatchResult(method="keyword")
        best_score = 0.0

        for protocol_id, protocol in self.protocols.items():
            trigger_phrases = protocol.get("trigger_phrases", [])
            score = 0.0

            for phrase in trigger_phrases:
                phrase_lower = phrase.lower()

                # Exact phrase match
                if phrase_lower in text:
                    # Score based on phrase length (longer = more specific)
                    phrase_score = min(len(phrase_lower) / 20.0, 1.0)
                    score = max(score, 0.5 + phrase_score * 0.5)

                # Word overlap scoring
                phrase_words = set(phrase_lower.split())
                text_words = set(text.split())
                overlap = phrase_words & text_words
                if overlap and len(phrase_words) > 0:
                    overlap_ratio = len(overlap) / len(phrase_words)
                    word_score = overlap_ratio * 0.6
                    score = max(score, word_score)

            if score > best_score:
                best_score = score
                best_match = MatchResult(
                    matched=True,
                    protocol_id=protocol_id,
                    protocol_title=protocol.get("title", ""),
                    confidence=min(score, 1.0),
                    reasoning=f"Keyword match with score {score:.2f}",
                    method="keyword",
                )

        return best_match

    def _match_with_ai(self, text: str) -> Optional[MatchResult]:
        """
        Use Gemini AI for sophisticated protocol matching.

        Sends the transcribed text and available protocol IDs
        to Gemini for contextual matching.
        """
        if not gemini_client.is_configured:
            logger.debug("Gemini not configured — skipping AI matching")
            return None

        protocol_ids = self.get_all_protocol_ids()
        raw_response = gemini_client.match_emergency_protocol(
            text, protocol_ids
        )

        if not raw_response:
            return None

        try:
            # Parse Gemini response
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)

            matched_id = result.get("matched_protocol", "")
            if matched_id not in self.protocols:
                logger.warning(f"AI matched unknown protocol: {matched_id}")
                return None

            return MatchResult(
                matched=True,
                protocol_id=matched_id,
                protocol_title=self.protocols[matched_id].get("title", ""),
                confidence=float(result.get("confidence", 0.5)),
                reasoning=result.get("reasoning", "AI match"),
                method="ai",
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse AI match response: {e}")
            return None


# Singleton instance
protocol_matcher = ProtocolMatcher()
