"""
OCR Extractor — Tesseract-based text extraction from medicine images.

Extracts structured information from preprocessed medicine images:
- Drug name and active ingredient
- Dosage information
- Expiry date
- Manufacturer
- Batch/lot number
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass, field

import pytesseract
import numpy as np

from m5_features.config import settings

logger = logging.getLogger(__name__)

# Configure Tesseract path
if settings.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH


@dataclass
class OCRResult:
    """Structured result from OCR text extraction."""

    raw_text: str = ""
    drug_name: Optional[str] = None
    dosage: Optional[str] = None
    expiry_date: Optional[str] = None
    manufacturer: Optional[str] = None
    batch_number: Optional[str] = None
    ndc_code: Optional[str] = None
    confidence: float = 0.0
    extracted_lines: list[str] = field(default_factory=list)


class OCRExtractor:
    """
    Tesseract OCR text extraction with medicine-specific parsing.

    Applies pattern matching to extract structured drug information
    from raw OCR text output.
    """

    # Regex patterns for medicine information extraction
    DOSAGE_PATTERN = re.compile(
        r"(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|iu|units?|%)\b",
        re.IGNORECASE,
    )
    EXPIRY_PATTERN = re.compile(
        r"(?:exp(?:iry)?|best\s*before|use\s*before|bb)[:\s]*"
        r"(\d{1,2}[/\-\.](?:\d{1,2}[/\-\.])?\d{2,4}|\w+\s+\d{4})",
        re.IGNORECASE,
    )
    BATCH_PATTERN = re.compile(
        r"(?:batch|lot|b\.?n\.?)[:\s#]*([A-Z0-9]{4,})",
        re.IGNORECASE,
    )
    NDC_PATTERN = re.compile(
        r"(?:NDC)[:\s]*(\d{4,5}-\d{3,4}-\d{1,2})",
        re.IGNORECASE,
    )
    MFG_PATTERN = re.compile(
        r"(?:mfg|manufactured|made)\s*(?:by|:)\s*(.+?)(?:\n|$)",
        re.IGNORECASE,
    )

    def extract_text(
        self,
        image: np.ndarray,
        lang: str = "eng",
        config: str = "--oem 3 --psm 6",
    ) -> str:
        """
        Extract raw text from image using Tesseract OCR.

        Args:
            image: Preprocessed grayscale/threshold image
            lang: Tesseract language code
            config: Tesseract configuration string
                --oem 3: Default LSTM engine
                --psm 6: Assume uniform block of text

        Returns:
            Raw OCR text output
        """
        try:
            text = pytesseract.image_to_string(
                image, lang=lang, config=config
            )
            logger.info(f"OCR extracted {len(text)} characters")
            return text.strip()
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""

    def get_confidence(self, image: np.ndarray) -> float:
        """
        Get OCR confidence score from Tesseract output data.

        Args:
            image: Preprocessed image

        Returns:
            Average confidence score (0.0 to 100.0)
        """
        try:
            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            confidences = [
                int(c) for c in data["conf"] if int(c) > 0
            ]
            if confidences:
                return sum(confidences) / len(confidences)
            return 0.0
        except Exception as e:
            logger.error(f"Confidence extraction failed: {e}")
            return 0.0

    def parse_drug_name(self, text: str) -> Optional[str]:
        """
        Attempt to extract drug name from OCR text.

        Heuristic: the drug name is typically the most prominent
        text, often on the first few lines in uppercase.

        Args:
            text: Raw OCR text

        Returns:
            Extracted drug name or None
        """
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip() and len(line.strip()) > 2
        ]

        for line in lines[:5]:  # Check first 5 meaningful lines
            # Skip lines that are mostly numbers or symbols
            alpha_ratio = sum(c.isalpha() for c in line) / max(len(line), 1)
            if alpha_ratio > 0.5 and not self.DOSAGE_PATTERN.search(line):
                # Skip common non-drug-name patterns
                skip_words = {
                    "tablets", "capsules", "syrup", "each", "contains",
                    "warning", "caution", "store", "keep", "ingredients",
                    "directions", "manufactured", "batch", "lot", "exp",
                }
                line_lower = line.lower()
                if not any(word in line_lower for word in skip_words):
                    return line.strip()

        return None

    def parse_dosage(self, text: str) -> Optional[str]:
        """Extract dosage information (e.g., '500mg', '10ml')."""
        match = self.DOSAGE_PATTERN.search(text)
        if match:
            return f"{match.group(1)}{match.group(2).lower()}"
        return None

    def parse_expiry(self, text: str) -> Optional[str]:
        """Extract expiry date from OCR text."""
        match = self.EXPIRY_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        return None

    def parse_batch(self, text: str) -> Optional[str]:
        """Extract batch/lot number."""
        match = self.BATCH_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        return None

    def parse_ndc(self, text: str) -> Optional[str]:
        """Extract NDC (National Drug Code)."""
        match = self.NDC_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        return None

    def parse_manufacturer(self, text: str) -> Optional[str]:
        """Extract manufacturer name."""
        match = self.MFG_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        return None

    def extract_and_parse(self, image: np.ndarray) -> OCRResult:
        """
        Full extraction pipeline: OCR + structured parsing.

        Runs Tesseract on the image, then applies regex patterns
        to extract structured medicine information.

        Args:
            image: Preprocessed image array

        Returns:
            OCRResult with all extracted fields populated
        """
        raw_text = self.extract_text(image)
        confidence = self.get_confidence(image)

        lines = [
            line.strip()
            for line in raw_text.split("\n")
            if line.strip()
        ]

        result = OCRResult(
            raw_text=raw_text,
            drug_name=self.parse_drug_name(raw_text),
            dosage=self.parse_dosage(raw_text),
            expiry_date=self.parse_expiry(raw_text),
            manufacturer=self.parse_manufacturer(raw_text),
            batch_number=self.parse_batch(raw_text),
            ndc_code=self.parse_ndc(raw_text),
            confidence=confidence / 100.0,  # Normalize to 0-1
            extracted_lines=lines,
        )

        logger.info(
            f"OCR parsing complete — drug: {result.drug_name}, "
            f"dosage: {result.dosage}, confidence: {result.confidence:.2f}"
        )
        return result


# Singleton instance
ocr_extractor = OCRExtractor()
