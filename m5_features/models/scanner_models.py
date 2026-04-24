"""
Pydantic v2 Models for the Medicine Scanner API.

Defines request/response schemas for the /api/medicine/scan endpoint.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MedicineScanRequest(BaseModel):
    """Request body for POST /api/medicine/scan."""

    image_base64: str = Field(
        ...,
        description="Base64-encoded image of the medicine/pill",
        min_length=100,
    )
    current_medications: Optional[list[str]] = Field(
        default=None,
        description="List of user's current medications for interaction checking",
        examples=[["aspirin", "metformin", "lisinopril"]],
    )
    mime_type: str = Field(
        default="image/jpeg",
        description="MIME type of the image",
        pattern=r"^image/(jpeg|png|webp|gif)$",
    )


class InteractionWarning(BaseModel):
    """A drug-drug interaction warning."""

    drug_a: str = Field(..., description="First drug in the interaction pair")
    drug_b: str = Field(..., description="Second drug in the interaction pair")
    severity: str = Field(
        ...,
        description="Severity level: high, moderate, or low",
    )
    effect: str = Field(..., description="Clinical effect of the interaction")
    source: str = Field(
        default="local_database",
        description="Data source for this interaction",
    )


class DrugInfo(BaseModel):
    """Structured drug identification information."""

    drug_name: Optional[str] = Field(None, description="Generic drug name")
    brand_name: Optional[str] = Field(None, description="Brand/trade name")
    generic_name: Optional[str] = Field(None, description="Generic/INN name")
    dosage: Optional[str] = Field(None, description="Dosage (e.g., '500mg')")
    dosage_form: Optional[str] = Field(
        None, description="Form (tablet, capsule, syrup, etc.)"
    )
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    color: Optional[str] = Field(None, description="Pill color")
    shape: Optional[str] = Field(None, description="Pill shape")
    imprint: Optional[str] = Field(None, description="Text imprinted on pill")


class SafetyInfo(BaseModel):
    """Drug safety and usage information from FDA."""

    indications: Optional[str] = Field(None, description="What the drug treats")
    warnings: Optional[str] = Field(None, description="Important warnings")
    contraindications: Optional[str] = Field(
        None, description="When NOT to use this drug"
    )
    adverse_reactions: Optional[str] = Field(None, description="Side effects")
    dosage_instructions: Optional[str] = Field(
        None, description="How to take this drug"
    )
    active_ingredients: list[str] = Field(
        default_factory=list, description="Active ingredient list"
    )


class MedicineScanResponse(BaseModel):
    """Response body for POST /api/medicine/scan."""

    # Status
    status: str = Field(
        default="success",
        description="Pipeline status: 'success' or 'error'",
    )
    confidence: float = Field(
        default=0.0,
        description="Overall identification confidence (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    error_message: Optional[str] = Field(
        None, description="Error details if status is 'error'"
    )

    # Drug identification
    drug_info: DrugInfo = Field(
        default_factory=DrugInfo,
        description="Identified drug information",
    )

    # Expiry
    expiry_date: Optional[str] = Field(None, description="Expiry date if found")
    is_expired: Optional[bool] = Field(
        None, description="Whether the drug appears expired"
    )

    # Safety
    safety_info: SafetyInfo = Field(
        default_factory=SafetyInfo,
        description="Drug safety information from FDA",
    )

    # Interactions
    interactions: list[InteractionWarning] = Field(
        default_factory=list,
        description="Drug interaction warnings",
    )
    interaction_analysis: Optional[str] = Field(
        None, description="AI-generated interaction analysis"
    )

    # Metadata
    sources: list[str] = Field(
        default_factory=list,
        description="Data sources used (tesseract_ocr, gemini_vision, openfda)",
    )
    ocr_raw_text: Optional[str] = Field(
        None, description="Raw OCR text for debugging"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "status": "success",
                "confidence": 0.85,
                "drug_info": {
                    "drug_name": "Paracetamol",
                    "brand_name": "Panadol",
                    "dosage": "500mg",
                    "dosage_form": "tablet",
                    "manufacturer": "GlaxoSmithKline",
                },
                "expiry_date": "12/2027",
                "is_expired": False,
                "safety_info": {
                    "warnings": "Do not exceed 4g daily. Liver damage risk with alcohol.",
                    "active_ingredients": ["Acetaminophen 500mg"],
                },
                "interactions": [],
                "sources": ["tesseract_ocr", "gemini_vision", "openfda"],
            }
        }
