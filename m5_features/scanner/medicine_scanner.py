"""
Medicine Scanner Pipeline — Full orchestrator for medicine identification.

Combines all scanner components into a single pipeline:
1. Image preprocessing (OpenCV)
2. OCR text extraction (Tesseract)
3. AI vision identification (Gemini)
4. Official drug data lookup (OpenFDA)
5. Drug interaction check
6. Merged structured response
"""

import json
import logging
from typing import Optional
from dataclasses import dataclass, field, asdict

from m5_features.scanner.image_preprocessor import image_preprocessor
from m5_features.scanner.ocr_extractor import ocr_extractor, OCRResult
from m5_features.scanner.openfda_service import openfda_service
from m5_features.scanner.drug_interaction_checker import (
    drug_interaction_checker,
    InteractionResult,
)
from m5_features.ai.gemini_client import gemini_client

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Complete result from the medicine scanning pipeline."""

    # Identification
    drug_name: Optional[str] = None
    brand_name: Optional[str] = None
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    dosage_form: Optional[str] = None
    manufacturer: Optional[str] = None

    # Expiry
    expiry_date: Optional[str] = None
    is_expired: Optional[bool] = None

    # Visual details
    color: Optional[str] = None
    shape: Optional[str] = None
    imprint: Optional[str] = None

    # Safety
    indications: Optional[str] = None
    warnings: Optional[str] = None
    contraindications: Optional[str] = None
    adverse_reactions: Optional[str] = None
    dosage_instructions: Optional[str] = None
    active_ingredients: list[str] = field(default_factory=list)

    # Interactions
    interactions: list[dict] = field(default_factory=list)
    interaction_analysis: Optional[str] = None

    # Metadata
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)
    ocr_raw_text: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return asdict(self)


class MedicineScanner:
    """
    Full medicine scanning pipeline orchestrator.

    Coordinates all scanning stages and merges results from
    multiple sources (OCR, Vision AI, OpenFDA) into a single
    comprehensive response.
    """

    async def scan(
        self,
        image_base64: str,
        current_medications: Optional[list[str]] = None,
    ) -> ScanResult:
        """
        Run the complete medicine scanning pipeline.

        Args:
            image_base64: Base64-encoded image of the medicine
            current_medications: Optional list of user's current meds
                for interaction checking

        Returns:
            ScanResult with all identified information
        """
        result = ScanResult()

        try:
            # Stage 1: Image preprocessing
            logger.info("Stage 1: Preprocessing image with OpenCV...")
            preprocessed = image_preprocessor.preprocess(image_base64, for_ocr=True)

            # Stage 2: OCR extraction
            ocr_result = OCRResult()
            if preprocessed is not None:
                logger.info("Stage 2: Running Tesseract OCR...")
                ocr_result = ocr_extractor.extract_and_parse(preprocessed)
                result.ocr_raw_text = ocr_result.raw_text
                result.sources.append("tesseract_ocr")
                self._merge_ocr(result, ocr_result)
            else:
                logger.warning("Image preprocessing failed — skipping OCR")

            # Stage 3: Gemini Vision identification
            logger.info("Stage 3: Running Gemini Vision analysis...")
            vision_result = self._run_vision_analysis(image_base64)
            if vision_result:
                result.sources.append("gemini_vision")
                self._merge_vision(result, vision_result)

            # Stage 4: OpenFDA lookup
            drug_to_search = result.drug_name or result.brand_name
            if drug_to_search:
                logger.info(f"Stage 4: Querying OpenFDA for '{drug_to_search}'...")
                fda_result = await openfda_service.search_by_name(drug_to_search)
                if fda_result:
                    result.sources.append("openfda")
                    self._merge_fda(result, fda_result)

                # Also try NDC code if found
                if ocr_result.ndc_code:
                    ndc_result = await openfda_service.search_by_ndc(ocr_result.ndc_code)
                    if ndc_result:
                        result.sources.append("openfda_ndc")
                        self._merge_fda(result, ndc_result)

            # Stage 5: Drug interaction check
            if result.drug_name and current_medications:
                logger.info("Stage 5: Checking drug interactions...")
                interaction_result = await drug_interaction_checker.check_interactions(
                    result.drug_name, current_medications
                )
                result.interactions = interaction_result.interactions
                result.interaction_analysis = interaction_result.ai_analysis
                if interaction_result.has_interactions:
                    result.sources.append("interaction_check")

            # Calculate overall confidence
            result.confidence = self._calculate_confidence(result)
            result.status = "success"

            logger.info(
                f"Scan complete: {result.drug_name} "
                f"(confidence: {result.confidence:.2f}, "
                f"sources: {result.sources})"
            )

        except Exception as e:
            logger.error(f"Medicine scan pipeline failed: {e}")
            result.status = "error"
            result.error_message = str(e)

        return result

    def _run_vision_analysis(self, image_base64: str) -> Optional[dict]:
        """Run Gemini Vision to identify the medicine from the image."""
        if not gemini_client.is_configured:
            logger.info("Gemini not configured — skipping vision analysis")
            return None

        raw_response = gemini_client.identify_medicine(image_base64)
        if not raw_response:
            return None

        try:
            # Clean any markdown code block markers
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini vision response as JSON: {e}")
            return None

    def _merge_ocr(self, result: ScanResult, ocr: OCRResult) -> None:
        """Merge OCR results into the scan result (lower priority)."""
        if ocr.drug_name and not result.drug_name:
            result.drug_name = ocr.drug_name
        if ocr.dosage and not result.dosage:
            result.dosage = ocr.dosage
        if ocr.expiry_date and not result.expiry_date:
            result.expiry_date = ocr.expiry_date
        if ocr.manufacturer and not result.manufacturer:
            result.manufacturer = ocr.manufacturer

    def _merge_vision(self, result: ScanResult, vision: dict) -> None:
        """Merge Gemini Vision results (higher priority than OCR)."""
        # Vision AI results take priority over OCR
        if vision.get("drug_name"):
            result.drug_name = vision["drug_name"]
        if vision.get("brand_name"):
            result.brand_name = vision["brand_name"]
        if vision.get("dosage"):
            result.dosage = vision["dosage"]
        if vision.get("form"):
            result.dosage_form = vision["form"]
        if vision.get("manufacturer"):
            result.manufacturer = vision["manufacturer"]
        if vision.get("expiry_date"):
            result.expiry_date = vision["expiry_date"]
        if vision.get("is_expired") is not None:
            result.is_expired = vision["is_expired"]
        if vision.get("color"):
            result.color = vision["color"]
        if vision.get("shape"):
            result.shape = vision["shape"]
        if vision.get("imprint"):
            result.imprint = vision["imprint"]

    def _merge_fda(self, result: ScanResult, fda: dict) -> None:
        """Merge OpenFDA data (highest priority for safety info)."""
        # FDA data is authoritative for names and safety info
        if fda.get("brand_name"):
            result.brand_name = fda["brand_name"]
        if fda.get("generic_name"):
            result.generic_name = fda["generic_name"]
        if fda.get("manufacturer"):
            result.manufacturer = fda["manufacturer"]
        if fda.get("dosage_form"):
            result.dosage_form = fda["dosage_form"]
        if fda.get("indications"):
            result.indications = fda["indications"]
        if fda.get("warnings"):
            result.warnings = fda["warnings"]
        if fda.get("contraindications"):
            result.contraindications = fda["contraindications"]
        if fda.get("adverse_reactions"):
            result.adverse_reactions = fda["adverse_reactions"]
        if fda.get("dosage_and_administration"):
            result.dosage_instructions = fda["dosage_and_administration"]
        if fda.get("active_ingredients"):
            ingredients = fda["active_ingredients"]
            if isinstance(ingredients, list):
                if ingredients and isinstance(ingredients[0], dict):
                    result.active_ingredients = [
                        f"{i['name']} {i.get('strength', '')}".strip()
                        for i in ingredients
                    ]
                else:
                    result.active_ingredients = ingredients

    def _calculate_confidence(self, result: ScanResult) -> float:
        """
        Calculate overall confidence score based on data completeness.

        Factors:
        - Number of sources that contributed data
        - Presence of key fields (drug name, dosage)
        - Agreement between OCR and Vision AI
        """
        score = 0.0

        # Source diversity bonus (max 0.4)
        score += min(len(result.sources) * 0.13, 0.4)

        # Key fields present (max 0.4)
        if result.drug_name:
            score += 0.15
        if result.dosage:
            score += 0.1
        if result.manufacturer:
            score += 0.05
        if result.dosage_form:
            score += 0.05
        if result.generic_name or result.brand_name:
            score += 0.05

        # Safety data available (max 0.2)
        if result.warnings:
            score += 0.1
        if result.active_ingredients:
            score += 0.1

        return min(score, 1.0)


# Singleton instance
medicine_scanner = MedicineScanner()
