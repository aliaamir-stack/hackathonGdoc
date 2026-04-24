"""
Gemini AI Client — Wrapper for Google Gemini Vision and Text APIs.

Provides both synchronous and async-compatible methods for:
- Text generation (protocol matching, drug identification)
- Vision analysis (pill/medicine photo identification)
- Error handling with retry logic
"""

import time
import base64
import logging
from typing import Optional

import google.generativeai as genai

from m5_features.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Google Gemini API client with support for text and vision models.

    Features:
    - Automatic retry on rate limit errors
    - Configurable model selection
    - Image input via base64 or file path
    - Structured prompt templates
    """

    def __init__(self):
        """Initialize the Gemini client with API key from config."""
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._text_model = genai.GenerativeModel(settings.GEMINI_MODEL_TEXT)
            self._vision_model = genai.GenerativeModel(settings.GEMINI_MODEL_VISION)
            self._configured = True
            logger.info("Gemini client configured successfully")
        else:
            self._configured = False
            logger.warning("GEMINI_API_KEY not set — Gemini features disabled")

    @property
    def is_configured(self) -> bool:
        """Check if the Gemini client is properly configured."""
        return self._configured

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """
        Generate text using Gemini text model.

        Args:
            prompt: The text prompt to send to Gemini
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum number of tokens in the response

        Returns:
            Generated text string, or None if generation fails
        """
        if not self._configured:
            logger.error("Gemini client not configured — cannot generate text")
            return None

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        for attempt in range(settings.GEMINI_MAX_RETRIES):
            try:
                response = self._text_model.generate_content(
                    prompt,
                    generation_config=generation_config,
                )
                if response and response.text:
                    return response.text.strip()
                logger.warning("Empty response from Gemini text model")
                return None
            except Exception as e:
                logger.warning(
                    f"Gemini text generation attempt {attempt + 1} failed: {e}"
                )
                if attempt < settings.GEMINI_MAX_RETRIES - 1:
                    time.sleep(settings.GEMINI_RETRY_DELAY * (attempt + 1))

        logger.error("All Gemini text generation attempts exhausted")
        return None

    def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        mime_type: str = "image/jpeg",
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Optional[str]:
        """
        Analyze an image using Gemini Vision model.

        Args:
            image_base64: Base64-encoded image data
            prompt: Text prompt describing what to analyze
            mime_type: MIME type of the image (e.g., "image/jpeg", "image/png")
            temperature: Controls randomness in output
            max_tokens: Maximum response length

        Returns:
            Analysis result text, or None if analysis fails
        """
        if not self._configured:
            logger.error("Gemini client not configured — cannot analyze image")
            return None

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # Decode base64 to bytes for Gemini
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return None

        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }

        for attempt in range(settings.GEMINI_MAX_RETRIES):
            try:
                response = self._vision_model.generate_content(
                    [prompt, image_part],
                    generation_config=generation_config,
                )
                if response and response.text:
                    return response.text.strip()
                logger.warning("Empty response from Gemini vision model")
                return None
            except Exception as e:
                logger.warning(
                    f"Gemini vision analysis attempt {attempt + 1} failed: {e}"
                )
                if attempt < settings.GEMINI_MAX_RETRIES - 1:
                    time.sleep(settings.GEMINI_RETRY_DELAY * (attempt + 1))

        logger.error("All Gemini vision analysis attempts exhausted")
        return None

    def identify_medicine(self, image_base64: str) -> Optional[str]:
        """
        Identify a medicine/pill from an image using Gemini Vision.

        Sends a specialized prompt to identify drug name, dosage,
        form, manufacturer, and any visible expiry information.

        Args:
            image_base64: Base64-encoded image of the medicine/pill

        Returns:
            JSON-formatted string with medicine identification details
        """
        prompt = """Analyze this medicine/pill image and provide identification.
        
Return a JSON object with these fields:
{
    "drug_name": "generic drug name",
    "brand_name": "brand name if visible",
    "dosage": "dosage amount and unit (e.g., 500mg)",
    "form": "tablet/capsule/syrup/injection/etc",
    "manufacturer": "manufacturer if visible",
    "expiry_date": "expiry date if visible, or null",
    "is_expired": true/false or null if unknown,
    "color": "pill color description",
    "shape": "pill shape (round/oval/oblong/etc)",
    "imprint": "any text/numbers imprinted on the pill",
    "confidence": 0.0 to 1.0,
    "warnings": ["any visible warnings from packaging"]
}

If you cannot identify the medicine clearly, set confidence below 0.5
and provide your best guess with a note in warnings.
Return ONLY valid JSON, no markdown formatting."""

        return self.analyze_image(image_base64, prompt)

    def match_emergency_protocol(
        self,
        transcribed_text: str,
        available_protocols: list[str],
    ) -> Optional[str]:
        """
        Match transcribed voice text to the best emergency protocol.

        Args:
            transcribed_text: Voice transcription from Web Speech API
            available_protocols: List of available protocol IDs

        Returns:
            JSON string with matched protocol ID and confidence
        """
        protocols_list = ", ".join(available_protocols)
        prompt = f"""You are an emergency first aid protocol matcher.
The user has described an emergency situation via voice input.

User said: "{transcribed_text}"

Available emergency protocols: [{protocols_list}]

Determine which protocol best matches the described emergency.
Return ONLY a JSON object:
{{
    "matched_protocol": "protocol_id",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of why this protocol matches"
}}

If no protocol seems to match well, set confidence below 0.3.
Return ONLY valid JSON, no markdown formatting."""

        return self.generate_text(prompt, temperature=0.1)


# Singleton instance
gemini_client = GeminiClient()
