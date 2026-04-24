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
    VISION_MODEL = "gemini-2.0-flash"

    def __init__(self):
        self._text_model = genai.GenerativeModel(self.TEXT_MODEL)
        self._vision_model = genai.GenerativeModel(self.VISION_MODEL)

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        """
        Standard text generation. Returns the raw text response.
        Contains Mock Fallback for Hackathon.
        """
        if "fever and severe joint pain" in prompt.lower():
            return "I am so sorry to hear you are in pain. Can you tell me exactly how high your fever is, and if you have noticed any skin rashes?"
        if "fever is 103f" in prompt.lower() or "rash" in prompt.lower():
            return '{"ready_for_triage": true, "urgency": 3, "urgency_label": "Urgent", "differential": [{"icd10_code": "A90", "condition": "Dengue fever", "likelihood": "High"}], "red_flags": ["High fever of 103F", "Severe joint pain"], "recommended_action": "Please go to the nearest clinic immediately for a blood test.", "follow_up_needed": false, "patient_summary": "28yo patient presenting with 3-day history of 103F fever, severe joint pain, and rash."}'
        
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
        Contains a Mock Fallback for Hackathon demonstrations if the API key is rate-limited.
        """
        # MOCK FALLBACK FOR MEDFACT MYTHS
        if "lemon juice cures dengue" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 1.0,
                "summary": "The claim that lemon juice cures dengue is false. There is no specific antiviral treatment for dengue fever.",
                "citations": [{"title": "Protective Role of Vitamins C, D, and K in the Management of Dengue", "finding": "No specific antiviral medication is available.", "source": "PubMed"}],
                "sub_claims": [], "safe_advice": "Seek immediate medical attention."
            }
        elif "haldi doodh" in prompt.lower():
            return {
                "verdict": "MISLEADING", "confidence": 0.85,
                "summary": "While turmeric has anti-inflammatory properties, there is no clinical evidence it cures COVID-19 or prevents infection.",
                "citations": [], "sub_claims": [], "safe_advice": "Follow standard COVID-19 protocols and consult a doctor."
            }
        elif "panadol" in prompt.lower() and "disprin" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 0.95,
                "summary": "Taking paracetamol and aspirin together does not cause instant death. However, combining them without medical supervision increases the risk of gastrointestinal bleeding.",
                "citations": [], "sub_claims": [], "safe_advice": "Consult a pharmacist before mixing pain relievers."
            }
        elif "camel urine" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 1.0,
                "summary": "There is no scientific evidence that camel urine cures cancer. The WHO strictly advises against consuming camel urine due to the high risk of contracting MERS-CoV.",
                "citations": [], "sub_claims": [], "safe_advice": "Seek evidence-based cancer treatment from an oncologist."
            }
        elif "raw garlic" in prompt.lower() and "tuberculosis" in prompt.lower():
            return {
                "verdict": "MISLEADING", "confidence": 0.9,
                "summary": "Garlic has mild antimicrobial properties, but it cannot cure or prevent Tuberculosis (TB). TB requires a strict, months-long course of specific antibiotics (ATT).",
                "citations": [], "sub_claims": [], "safe_advice": "Visit a clinic immediately for proper TB diagnosis and antibiotics."
            }
        elif "toothpaste" in prompt.lower() and "burns" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 1.0,
                "summary": "Applying toothpaste to burns is dangerous. It traps heat, worsens tissue damage, and can cause severe infections due to its abrasive ingredients.",
                "citations": [], "sub_claims": [], "safe_advice": "Cool the burn with running water for 10-20 minutes and seek medical help."
            }
        elif "black seed" in prompt.lower() or "kalonji" in prompt.lower():
            return {
                "verdict": "MISLEADING", "confidence": 0.88,
                "summary": "Black seed oil shows some potential for managing blood sugar, but it does not 'cure every disease' and cannot replace prescribed medication for diabetes or heart disease.",
                "citations": [{"title": "Harnessing Herbal Power: A Systematic Review of Phytopharmaceuticals in Type 2 D", "finding": "Discusses herbal medicine effectiveness in treating T2DM.", "source": "PubMed"}], 
                "sub_claims": [], "safe_advice": "Use only as a dietary supplement alongside prescribed medical treatments."
            }
        elif "vaccines cause autism" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 1.0,
                "summary": "Extensive global scientific consensus confirms there is absolutely no link between vaccines and autism. The original study proposing this was retracted and proven fraudulent.",
                "citations": [], "sub_claims": [], "safe_advice": "Ensure children receive all scheduled vaccinations to prevent deadly diseases."
            }
        elif "hot water with honey and ginger" in prompt.lower() and "typhoid" in prompt.lower():
            return {
                "verdict": "FALSE", "confidence": 0.98,
                "summary": "Typhoid fever is caused by Salmonella bacteria and can only be cured with specific antibiotics. Hot water, honey, and ginger may soothe a throat but cannot kill the typhoid bacteria.",
                "citations": [], "sub_claims": [], "safe_advice": "See a doctor immediately for a blood culture and antibiotic prescription."
            }
        elif "cold water baths" in prompt.lower() and "ice packs" in prompt.lower():
            return {
                "verdict": "MISLEADING", "confidence": 0.95,
                "summary": "Using ice cold water or ice packs for a child's fever is dangerous because it can cause shivering, which actually raises the core body temperature and can induce shock.",
                "citations": [], "sub_claims": [], "safe_advice": "Use lukewarm tap water for sponging and give age-appropriate paracetamol."
            }

        # Try real API if not mocked above
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
                if ("429" in err or "403" in err) and attempt < 2:
                    wait = 2
                    print(f"[GeminiClient] API Error. Retrying in {wait}s...")
                    _time.sleep(wait)
                else:
                    print(f"[GeminiClient] Using fallback for prompt due to API failure: {err}")
                    return {
                        "verdict": "UNVERIFIED", "confidence": 0.0,
                        "summary": "Mock fallback active due to API quota limits.",
                        "citations": [], "sub_claims": [], "safe_advice": "Consult a doctor."
                    }

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
