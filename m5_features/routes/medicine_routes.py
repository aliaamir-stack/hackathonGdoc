"""
Medicine Scanner API Routes — FastAPI endpoints for medicine identification.

Endpoints:
- POST /api/medicine/scan — Scan a medicine image and return identification
"""

import logging
from fastapi import APIRouter, HTTPException

from m5_features.models.scanner_models import (
    MedicineScanRequest,
    MedicineScanResponse,
    DrugInfo,
    SafetyInfo,
    InteractionWarning,
)
from m5_features.scanner.medicine_scanner import medicine_scanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/medicine", tags=["Medicine Scanner"])


@router.post(
    "/scan",
    response_model=MedicineScanResponse,
    summary="Scan a medicine/pill image",
    description=(
        "Accepts a base64-encoded image of a medicine or pill, "
        "runs it through OCR + Vision AI + OpenFDA lookup, "
        "and returns comprehensive drug identification with "
        "safety information and interaction warnings."
    ),
    responses={
        200: {"description": "Successful scan with drug identification"},
        400: {"description": "Invalid image data"},
        500: {"description": "Internal pipeline error"},
    },
)
async def scan_medicine(request: MedicineScanRequest) -> MedicineScanResponse:
    """
    Scan a medicine image and return comprehensive identification.

    Pipeline:
    1. OpenCV preprocessing (grayscale, sharpen, threshold)
    2. Tesseract OCR (drug name, dosage, expiry)
    3. Gemini Vision AI (visual identification)
    4. OpenFDA lookup (official drug data)
    5. Drug interaction check (if current medications provided)

    Processing time: typically 2–4 seconds.
    """
    logger.info("Received medicine scan request")

    # Validate image data
    if len(request.image_base64) < 100:
        raise HTTPException(
            status_code=400,
            detail="Image data too small — please provide a valid photo",
        )

    try:
        # Run the full scanning pipeline
        result = await medicine_scanner.scan(
            image_base64=request.image_base64,
            current_medications=request.current_medications,
        )

        # Convert pipeline result to API response
        response = MedicineScanResponse(
            status=result.status,
            confidence=result.confidence,
            error_message=result.error_message,
            drug_info=DrugInfo(
                drug_name=result.drug_name,
                brand_name=result.brand_name,
                generic_name=result.generic_name,
                dosage=result.dosage,
                dosage_form=result.dosage_form,
                manufacturer=result.manufacturer,
                color=result.color,
                shape=result.shape,
                imprint=result.imprint,
            ),
            expiry_date=result.expiry_date,
            is_expired=result.is_expired,
            safety_info=SafetyInfo(
                indications=result.indications,
                warnings=result.warnings,
                contraindications=result.contraindications,
                adverse_reactions=result.adverse_reactions,
                dosage_instructions=result.dosage_instructions,
                active_ingredients=result.active_ingredients,
            ),
            interactions=[
                InteractionWarning(**interaction)
                for interaction in result.interactions
            ],
            interaction_analysis=result.interaction_analysis,
            sources=result.sources,
            ocr_raw_text=result.ocr_raw_text,
        )

        logger.info(
            f"Scan completed: {result.drug_name} "
            f"(confidence: {result.confidence:.2f})"
        )
        return response

    except Exception as e:
        logger.error(f"Medicine scan endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scan pipeline failed: {str(e)}",
        )


@router.get(
    "/health",
    summary="Medicine scanner health check",
    description="Returns the status of the medicine scanner service",
)
async def scanner_health():
    """Health check endpoint for the medicine scanner service."""
    from m5_features.ai.gemini_client import gemini_client

    return {
        "service": "medicine_scanner",
        "status": "operational",
        "gemini_configured": gemini_client.is_configured,
        "pipeline_stages": [
            "image_preprocessing",
            "ocr_extraction",
            "gemini_vision",
            "openfda_lookup",
            "interaction_check",
        ],
    }
