"""
Unit Tests for the Medicine Scanner Pipeline.

Tests cover:
- Image preprocessing (OpenCV operations)
- OCR text parsing (regex extraction)
- OpenFDA service (API response handling)
- Drug interaction checking (local DB + AI)
- Full pipeline orchestration
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from m5_features.scanner.image_preprocessor import ImagePreprocessor
from m5_features.scanner.ocr_extractor import OCRExtractor, OCRResult
from m5_features.scanner.drug_interaction_checker import (
    DrugInteractionChecker,
    KNOWN_INTERACTIONS,
)


class TestImagePreprocessor:
    """Tests for OpenCV image preprocessing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = ImagePreprocessor()

    def test_to_grayscale(self):
        """Test BGR to grayscale conversion."""
        # Create a simple 10x10 BGR image
        bgr_image = np.zeros((10, 10, 3), dtype=np.uint8)
        bgr_image[:, :, 0] = 100  # Blue channel
        bgr_image[:, :, 1] = 150  # Green channel
        bgr_image[:, :, 2] = 200  # Red channel

        gray = self.preprocessor.to_grayscale(bgr_image)
        assert gray.ndim == 2  # Should be 2D
        assert gray.shape == (10, 10)

    def test_sharpen(self):
        """Test image sharpening."""
        gray_image = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        sharpened = self.preprocessor.sharpen(gray_image)
        assert sharpened.shape == gray_image.shape
        assert sharpened.dtype == gray_image.dtype

    def test_adaptive_threshold(self):
        """Test adaptive thresholding output is binary."""
        gray_image = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        thresholded = self.preprocessor.adaptive_threshold(gray_image)
        assert thresholded.shape == gray_image.shape
        unique_values = np.unique(thresholded)
        # Adaptive threshold should produce binary (0, 255)
        assert all(v in [0, 255] for v in unique_values)

    def test_enhance_contrast(self):
        """Test CLAHE contrast enhancement."""
        gray_image = np.random.randint(50, 200, (50, 50), dtype=np.uint8)
        enhanced = self.preprocessor.enhance_contrast(gray_image)
        assert enhanced.shape == gray_image.shape
        # CLAHE should increase dynamic range
        assert np.std(enhanced) >= np.std(gray_image) * 0.5

    def test_resize_for_ocr(self):
        """Test resize maintains aspect ratio."""
        image = np.zeros((100, 200), dtype=np.uint8)
        resized = self.preprocessor.resize_for_ocr(image, target_width=400)
        assert resized.shape[1] == 400
        assert resized.shape[0] == 200  # Should maintain 1:2 aspect ratio

    def test_decode_invalid_base64(self):
        """Test graceful handling of invalid base64."""
        result = self.preprocessor.decode_base64_image("not-valid-base64!!!")
        assert result is None

    def test_encode_to_base64(self):
        """Test encoding image to base64 string."""
        image = np.zeros((10, 10), dtype=np.uint8)
        b64 = self.preprocessor.encode_to_base64(image)
        assert isinstance(b64, str)
        assert len(b64) > 0


class TestOCRExtractor:
    """Tests for OCR text parsing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = OCRExtractor()

    def test_parse_dosage_mg(self):
        """Test dosage extraction: milligrams."""
        text = "Each tablet contains Paracetamol 500mg"
        dosage = self.extractor.parse_dosage(text)
        assert dosage == "500mg"

    def test_parse_dosage_ml(self):
        """Test dosage extraction: milliliters."""
        text = "DOSAGE: 5ml every 6 hours"
        dosage = self.extractor.parse_dosage(text)
        assert dosage == "5ml"

    def test_parse_dosage_mcg(self):
        """Test dosage extraction: micrograms."""
        text = "Levothyroxine 50mcg tablets"
        dosage = self.extractor.parse_dosage(text)
        assert dosage == "50mcg"

    def test_parse_expiry_slash_format(self):
        """Test expiry date extraction: MM/YYYY."""
        text = "EXP: 12/2027\nBatch: ABC123"
        expiry = self.extractor.parse_expiry(text)
        assert expiry is not None
        assert "2027" in expiry

    def test_parse_expiry_word_format(self):
        """Test expiry date extraction: Month YYYY."""
        text = "Expiry: December 2027"
        expiry = self.extractor.parse_expiry(text)
        assert expiry is not None

    def test_parse_batch_number(self):
        """Test batch number extraction."""
        text = "LOT: BN2024X456\nExp: 01/2026"
        batch = self.extractor.parse_batch(text)
        assert batch is not None
        assert "BN2024X456" in batch

    def test_parse_ndc_code(self):
        """Test NDC code extraction."""
        text = "NDC: 12345-6789-01\nActive ingredient: Aspirin"
        ndc = self.extractor.parse_ndc(text)
        assert ndc == "12345-6789-01"

    def test_parse_manufacturer(self):
        """Test manufacturer extraction."""
        text = "Manufactured by: GlaxoSmithKline\nLondon, UK"
        mfg = self.extractor.parse_manufacturer(text)
        assert "GlaxoSmithKline" in mfg

    def test_parse_no_dosage(self):
        """Test graceful handling when no dosage present."""
        text = "Just some random text without dosage info"
        dosage = self.extractor.parse_dosage(text)
        assert dosage is None


class TestDrugInteractionChecker:
    """Tests for drug interaction checking."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = DrugInteractionChecker()

    @pytest.mark.asyncio
    async def test_aspirin_warfarin_interaction(self):
        """Test known high-severity interaction: aspirin + warfarin."""
        result = await self.checker.check_interactions("aspirin", ["warfarin"])
        assert result.has_interactions is True
        assert len(result.interactions) > 0
        assert any(
            i["severity"] == "high"
            for i in result.interactions
        )

    @pytest.mark.asyncio
    async def test_paracetamol_alcohol_interaction(self):
        """Test known interaction: paracetamol + alcohol."""
        result = await self.checker.check_interactions("paracetamol", ["alcohol"])
        assert result.has_interactions is True

    @pytest.mark.asyncio
    async def test_no_interaction(self):
        """Test drugs with no known interactions in local DB."""
        result = await self.checker.check_interactions(
            "vitamin_c", ["vitamin_d"]
        )
        assert result.has_interactions is False
        assert len(result.interactions) == 0

    @pytest.mark.asyncio
    async def test_empty_medications_list(self):
        """Test with empty medication list."""
        result = await self.checker.check_interactions("aspirin", [])
        assert result.has_interactions is False

    @pytest.mark.asyncio
    async def test_multiple_interactions(self):
        """Test drug with multiple interactions."""
        result = await self.checker.check_interactions(
            "ibuprofen", ["aspirin", "warfarin", "lithium"]
        )
        assert result.has_interactions is True
        assert len(result.interactions) >= 2

    @pytest.mark.asyncio
    async def test_reverse_lookup(self):
        """Test that interaction check works in both directions."""
        result = await self.checker.check_interactions("warfarin", ["aspirin"])
        assert result.has_interactions is True

    def test_known_interactions_dict_populated(self):
        """Verify the KNOWN_INTERACTIONS database has entries."""
        assert len(KNOWN_INTERACTIONS) > 5
        assert "aspirin" in KNOWN_INTERACTIONS
        assert "paracetamol" in KNOWN_INTERACTIONS
        assert "metformin" in KNOWN_INTERACTIONS


class TestOCRResult:
    """Tests for OCRResult dataclass."""

    def test_default_values(self):
        """Test OCRResult initializes with expected defaults."""
        result = OCRResult()
        assert result.raw_text == ""
        assert result.drug_name is None
        assert result.dosage is None
        assert result.confidence == 0.0
        assert result.extracted_lines == []

    def test_populated_result(self):
        """Test OCRResult with populated fields."""
        result = OCRResult(
            raw_text="Paracetamol 500mg",
            drug_name="Paracetamol",
            dosage="500mg",
            confidence=0.85,
        )
        assert result.drug_name == "Paracetamol"
        assert result.dosage == "500mg"
        assert result.confidence == 0.85


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
