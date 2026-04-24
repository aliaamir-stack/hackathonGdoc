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

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # --- OCR ---
    TESSERACT_PATH: str = os.getenv(
        "TESSERACT_PATH",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # --- API ---
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

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
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.TELEGRAM_CHAT_ID:
            missing.append("TELEGRAM_CHAT_ID")
        return missing

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT == "production"


# Singleton instance
settings = Settings()
