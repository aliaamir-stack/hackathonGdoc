"""
PULSE Gemini Client
M3 — AI/ML Engineer

Wraps the Google Generative AI SDK with:
- Standard text generation
- JSON/structured output generation
- Streaming generation (for SSE endpoints)
- Vision generation (for Medicine Scanner)
"""

import json
import os
import re
import base64
import google.generativeai as genai
from typing import Any, Generator
from dotenv import load_dotenv

load_dotenv()

# --- Configure Gemini globally ---
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise EnvironmentError("GEMINI_API_KEY is not set in .env")

genai.configure(api_key=_api_key)


class GeminiClient:
    """
    Centralized Gemini client for the PULSE AI module.
    Free tier: 1M tokens/day, 15 req/min — use flash, not pro.
    """

    TEXT_MODEL = "gemini-2.0-flash-lite"
    VISION_MODEL = "gemini-2.0-flash"  # lite doesn't support vision

    def __init__(self):
        self._text_model = genai.GenerativeModel(self.TEXT_MODEL)
        self._vision_model = genai.GenerativeModel(self.VISION_MODEL)

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        """
        Standard text generation. Returns the raw text response.
        temperature=0.3 is good for factual/medical tasks.
        """
        generation_config = genai.types.GenerationConfig(temperature=temperature)

        if system_prompt:
            model = genai.GenerativeModel(
                self.TEXT_MODEL,
                system_instruction=system_prompt,
                generation_config=generation_config,
            )
        else:
            model = genai.GenerativeModel(
                self.TEXT_MODEL,
                generation_config=generation_config,
            )

        response = model.generate_content(prompt)
        return response.text

    def generate_json(self, prompt: str, system_prompt: str = None, temperature: float = 0.1) -> dict:
        """
        Generates a response and parses it as JSON.
        Retries automatically on 429 rate limit errors (up to 3 times).
        """
        import time as _time
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json",
        )

        if system_prompt:
            model = genai.GenerativeModel(
                self.TEXT_MODEL,
                system_instruction=system_prompt,
                generation_config=generation_config,
            )
        else:
            model = genai.GenerativeModel(
                self.TEXT_MODEL,
                generation_config=generation_config,
            )

        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                raw = response.text.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                return json.loads(raw)
            except Exception as e:
                err = str(e)
                if "429" in err and attempt < 2:
                    wait = 30 * (attempt + 1)
                    print(f"[GeminiClient] Rate limited. Waiting {wait}s before retry {attempt+2}/3...")
                    _time.sleep(wait)
                else:
                    raise

    def generate_stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """
        Streaming generation for SSE endpoints.
        Yields text chunks as they arrive.
        """
        if system_prompt:
            model = genai.GenerativeModel(
                self.TEXT_MODEL,
                system_instruction=system_prompt,
            )
        else:
            model = self._text_model

        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def generate_vision(self, image_bytes: bytes, prompt: str, system_prompt: str = None) -> dict:
        """
        Vision generation for the Medicine Scanner.
        Accepts raw image bytes and returns a parsed JSON dict.
        """
        import PIL.Image
        import io

        image = PIL.Image.open(io.BytesIO(image_bytes))

        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json",
        )

        if system_prompt:
            model = genai.GenerativeModel(
                self.VISION_MODEL,
                system_instruction=system_prompt,
                generation_config=generation_config,
            )
        else:
            model = genai.GenerativeModel(
                self.VISION_MODEL,
                generation_config=generation_config,
            )

        response = model.generate_content([prompt, image])
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        return json.loads(raw)

    def detect_language(self, text: str) -> str:
        """Returns 'urdu' or 'english' for bilingual support."""
        from .prompts import URDU_DETECTION_PROMPT
        result = self.generate(
            URDU_DETECTION_PROMPT.format(text=text),
            temperature=0.0,
        ).strip().lower()
        return result if result in ("urdu", "english") else "english"


# Singleton instance — import this across the codebase
gemini = GeminiClient()
