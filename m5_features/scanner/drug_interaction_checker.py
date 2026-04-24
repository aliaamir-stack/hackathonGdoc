"""
Drug Interaction Checker — Check for dangerous drug-drug interactions.

Queries the identified drug against the user's current medication list
to flag potential interactions. Uses both a local database of known
interactions and Gemini AI for comprehensive checking.
"""

import logging
import httpx
import asyncio
from typing import Optional
from dataclasses import dataclass, field

from m5_features.ai.gemini_client import gemini_client
from m5_features.config import settings

logger = logging.getLogger(__name__)


# Known dangerous drug interactions (common pairs)
# This serves as a fast offline fallback before Gemini AI check
KNOWN_INTERACTIONS: dict[str, list[dict]] = {
    "aspirin": [
        {"drug": "warfarin", "severity": "high", "effect": "Increased bleeding risk"},
        {"drug": "ibuprofen", "severity": "moderate", "effect": "Reduced aspirin efficacy and increased GI bleeding"},
        {"drug": "methotrexate", "severity": "high", "effect": "Increased methotrexate toxicity"},
        {"drug": "clopidogrel", "severity": "moderate", "effect": "Increased bleeding risk"},
    ],
    "paracetamol": [
        {"drug": "warfarin", "severity": "moderate", "effect": "May increase INR and bleeding risk"},
        {"drug": "alcohol", "severity": "high", "effect": "Severe liver damage risk"},
        {"drug": "isoniazid", "severity": "high", "effect": "Increased hepatotoxicity"},
    ],
    "metformin": [
        {"drug": "alcohol", "severity": "high", "effect": "Increased risk of lactic acidosis"},
        {"drug": "contrast dye", "severity": "high", "effect": "Risk of lactic acidosis — stop 48h before"},
        {"drug": "cimetidine", "severity": "moderate", "effect": "Increased metformin levels"},
    ],
    "ibuprofen": [
        {"drug": "aspirin", "severity": "moderate", "effect": "Reduced aspirin cardioprotection"},
        {"drug": "warfarin", "severity": "high", "effect": "Increased bleeding risk"},
        {"drug": "lithium", "severity": "high", "effect": "Increased lithium toxicity"},
        {"drug": "methotrexate", "severity": "high", "effect": "Increased methotrexate toxicity"},
    ],
    "amoxicillin": [
        {"drug": "methotrexate", "severity": "high", "effect": "Increased methotrexate toxicity"},
        {"drug": "warfarin", "severity": "moderate", "effect": "May increase INR"},
        {"drug": "oral contraceptives", "severity": "low", "effect": "May reduce contraceptive efficacy"},
    ],
    "ciprofloxacin": [
        {"drug": "theophylline", "severity": "high", "effect": "Increased theophylline toxicity"},
        {"drug": "warfarin", "severity": "high", "effect": "Increased bleeding risk"},
        {"drug": "antacids", "severity": "moderate", "effect": "Reduced ciprofloxacin absorption"},
        {"drug": "tizanidine", "severity": "high", "effect": "Dangerous increase in tizanidine levels"},
    ],
    "omeprazole": [
        {"drug": "clopidogrel", "severity": "high", "effect": "Reduced clopidogrel efficacy — avoid combination"},
        {"drug": "methotrexate", "severity": "moderate", "effect": "Increased methotrexate levels"},
        {"drug": "digoxin", "severity": "moderate", "effect": "Increased digoxin absorption"},
    ],
    "atorvastatin": [
        {"drug": "clarithromycin", "severity": "high", "effect": "Increased statin levels — rhabdomyolysis risk"},
        {"drug": "cyclosporine", "severity": "high", "effect": "Increased statin levels — muscle damage risk"},
        {"drug": "grapefruit", "severity": "moderate", "effect": "Increased statin absorption"},
    ],
    "metronidazole": [
        {"drug": "alcohol", "severity": "high", "effect": "Severe nausea, vomiting, facial flushing (disulfiram reaction)"},
        {"drug": "warfarin", "severity": "high", "effect": "Significantly increased bleeding risk"},
        {"drug": "lithium", "severity": "moderate", "effect": "Increased lithium toxicity"},
    ],
}


@dataclass
class InteractionResult:
    """Result of a drug interaction check."""

    has_interactions: bool = False
    interactions: list[dict] = field(default_factory=list)
    ai_analysis: Optional[str] = None
    checked_against: list[str] = field(default_factory=list)


class DrugInteractionChecker:
    """
    Checks for drug-drug interactions using local database and AI.

    Flow:
    1. Check against local KNOWN_INTERACTIONS database (instant)
    2. If Gemini is available, get AI analysis for comprehensive check
    3. Merge results with severity ratings
    """

    async def check_interactions(
        self,
        identified_drug: str,
        current_medications: list[str],
    ) -> InteractionResult:
        """
        Check a drug against user's current medication list.

        Args:
            identified_drug: Name of the newly identified drug
            current_medications: List of user's current medications

        Returns:
            InteractionResult with all found interactions
        """
        result = InteractionResult(checked_against=current_medications)

        if not identified_drug or not current_medications:
            return result

        drug_lower = identified_drug.lower().strip()

        # Step 1: Check Supabase database, fallback to local database
        db_interactions = await self._check_database_async(drug_lower, current_medications)
        if db_interactions is not None:
            result.interactions.extend(db_interactions)
        else:
            logger.warning("Database check failed or unavailable, falling back to local KNOWN_INTERACTIONS")
            local_interactions = self._check_local(drug_lower, current_medications)
            result.interactions.extend(local_interactions)

        # Step 2: AI-powered check for comprehensive analysis
        ai_result = self._check_with_ai(identified_drug, current_medications)
        if ai_result:
            result.ai_analysis = ai_result

        result.has_interactions = len(result.interactions) > 0

        logger.info(
            f"Interaction check for '{identified_drug}': "
            f"{len(result.interactions)} interactions found"
        )
        return result

    async def _check_database_async(self, drug: str, medications: list[str]) -> Optional[list[dict]]:
        """
        Query the Supabase REST API for interactions.
        Returns None if the database is unconfigured or the request fails,
        triggering the local fallback.
        """
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            return None

        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/drug_interactions"
        headers = {
            "apikey": settings.SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
            "Accept": "application/json"
        }
        
        # Build query: drug_a matches identified drug OR drug_b matches identified drug
        query = f"?or=(drug_a.ilike.*{drug}*,drug_b.ilike.*{drug}*)"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url + query, headers=headers, timeout=5.0)
                if response.status_code != 200:
                    logger.error(f"Supabase query failed: {response.status_code} {response.text}")
                    return None
                    
                data = response.json()
                interactions = []
                
                # Cross-reference with current_medications
                for row in data:
                    drug_a = row.get("drug_a", "").lower()
                    drug_b = row.get("drug_b", "").lower()
                    
                    for med in medications:
                        med_lower = med.lower().strip()
                        # If the row matches one of our current meds as well
                        if med_lower in drug_a or med_lower in drug_b:
                            interactions.append({
                                "drug_a": row.get("drug_a"),
                                "drug_b": row.get("drug_b"),
                                "severity": row.get("severity") or "moderate",
                                "effect": row.get("description", "Potential interaction detected"),
                                "source": "supabase_database",
                            })
                            
                return interactions
                
        except Exception as e:
            logger.error(f"Failed to query Supabase: {e}")
            return None

    def _check_local(
        self,
        drug: str,
        medications: list[str],
    ) -> list[dict]:
        """
        Check against local known interactions database.

        This provides instant results without API calls,
        covering the most common and dangerous interactions.
        """
        interactions = []
        drug_interactions = KNOWN_INTERACTIONS.get(drug, [])

        for med in medications:
            med_lower = med.lower().strip()

            # Check if identified drug has interaction with this medication
            for interaction in drug_interactions:
                if interaction["drug"].lower() in med_lower or med_lower in interaction["drug"].lower():
                    interactions.append({
                        "drug_a": drug,
                        "drug_b": med,
                        "severity": interaction["severity"],
                        "effect": interaction["effect"],
                        "source": "local_database",
                    })

            # Also check reverse (medication → identified drug)
            med_interactions = KNOWN_INTERACTIONS.get(med_lower, [])
            for interaction in med_interactions:
                if interaction["drug"].lower() in drug or drug in interaction["drug"].lower():
                    # Avoid duplicates
                    already_found = any(
                        i["drug_b"] == med and i["drug_a"] == drug
                        for i in interactions
                    )
                    if not already_found:
                        interactions.append({
                            "drug_a": med,
                            "drug_b": drug,
                            "severity": interaction["severity"],
                            "effect": interaction["effect"],
                            "source": "local_database",
                        })

        return interactions

    def _check_with_ai(
        self,
        drug: str,
        medications: list[str],
    ) -> Optional[str]:
        """
        Use Gemini AI for comprehensive interaction analysis.

        Provides a more thorough check that covers interactions
        not in the local database, with clinical context.
        """
        if not gemini_client.is_configured:
            return None

        med_list = ", ".join(medications)
        prompt = f"""You are a pharmacist reviewing drug interactions.

Patient is currently taking: {med_list}
New drug identified: {drug}

Check for drug-drug interactions. For each interaction found, provide:
1. The interacting pair
2. Severity (HIGH/MODERATE/LOW)
3. Clinical effect
4. Recommendation

If no significant interactions exist, say "No significant interactions found."

Be concise and clinically accurate. This is for patient safety guidance only,
not a replacement for professional medical advice.
"""
        return gemini_client.generate_text(prompt, temperature=0.1, max_tokens=1024)


# Singleton instance
drug_interaction_checker = DrugInteractionChecker()
