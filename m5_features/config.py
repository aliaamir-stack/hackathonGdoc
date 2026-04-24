"""
Configuration module for PULSE M5 Features.

Loads environment variables from .env file and provides
centralized configuration for all M5 services.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    # Try parent directory
    load_dotenv(Path(__file__).parent.parent / ".env")


class Settings:
    """
    Centralized configuration for M5 features.
    All values are loaded from environment variables with sensible defaults.
    """

    # --- AI Engine ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL_VISION: str = os.getenv("GEMINI_MODEL_VISION", "gemini-1.5-flash")
    GEMINI_MODEL_TEXT: str = os.getenv("GEMINI_MODEL_TEXT", "gemini-1.5-flash")

    # --- Email Alert (Gmail SMTP) ---
    ALERT_EMAIL: str = os.getenv("ALERT_EMAIL", "")
    ALERT_EMAIL_PASSWORD: str = os.getenv("ALERT_EMAIL_PASSWORD", "")
    ALERT_RECIPIENT_EMAIL: str = os.getenv("ALERT_RECIPIENT_EMAIL", "")

    # --- OCR ---
    TESSERACT_PATH: str = os.getenv(
        "TESSERACT_PATH",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # --- API ---
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # --- Database (Supabase) ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # --- Cache (Redis) ---
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # --- External APIs ---
    OPENFDA_BASE_URL: str = "https://api.fda.gov/drug"
    OPENFDA_NDC_ENDPOINT: str = f"{OPENFDA_BASE_URL}/ndc.json"
    OPENFDA_LABEL_ENDPOINT: str = f"{OPENFDA_BASE_URL}/label.json"

    # --- Protocol Cache ---
    PROTOCOLS_DIR: str = str(Path(__file__).parent / "protocols")

    # --- Rate Limiting ---
    GEMINI_MAX_RETRIES: int = 3
    GEMINI_RETRY_DELAY: float = 1.0

    @classmethod
    def validate(cls) -> list[str]:
        """
        Validate that required environment variables are set.
        Returns a list of missing variable names.
        """
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.ALERT_EMAIL:
            missing.append("ALERT_EMAIL")
        if not cls.ALERT_EMAIL_PASSWORD:
            missing.append("ALERT_EMAIL_PASSWORD")
        return missing

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT == "production"


# Singleton instance
settings = Settings()
