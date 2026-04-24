"""
Pydantic v2 Models for the Emergency Guide API.

Defines request/response schemas for:
- POST /api/emergency/identify — Match voice text to protocol
- POST /api/emergency/alert — Send Telegram GPS alert
- GET /api/emergency/protocols — List all available protocols
"""

from typing import Optional
from pydantic import BaseModel, Field


class ProtocolStep(BaseModel):
    """A single step in an emergency protocol."""

    step_number: int = Field(..., description="Step sequence number")
    instruction: str = Field(..., description="What to do")
    tip: str = Field(default="", description="Additional guidance")
    timer_seconds: int = Field(
        default=0, description="Suggested time for this step in seconds"
    )


class EmergencyIdentifyRequest(BaseModel):
    """Request body for POST /api/emergency/identify."""

    transcribed_text: str = Field(
        ...,
        description="Transcribed voice text or typed emergency description",
        min_length=3,
        max_length=1000,
        examples=[
            "someone is not breathing",
            "my child is choking on food",
            "severe chest pain and difficulty breathing",
        ],
    )


class EmergencyIdentifyResponse(BaseModel):
    """Response body for POST /api/emergency/identify."""

    matched: bool = Field(
        ..., description="Whether a protocol was matched"
    )
    confidence: float = Field(
        default=0.0,
        description="Match confidence (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    method: str = Field(
        default="none",
        description="Matching method used: 'keyword', 'ai', or 'none'",
    )
    reasoning: Optional[str] = Field(
        None, description="Why this protocol was matched"
    )

    # Protocol info
    protocol_id: Optional[str] = Field(None, description="Matched protocol ID")
    protocol_title: Optional[str] = Field(
        None, description="Protocol title for display"
    )
    category: Optional[str] = Field(
        None, description="Emergency category"
    )
    severity_level: Optional[int] = Field(
        None, description="Severity 1-5 (5 = most severe)"
    )
    call_ambulance: bool = Field(
        default=True, description="Whether to call emergency services"
    )
    immediate_action: Optional[str] = Field(
        None, description="First thing to do — read aloud immediately"
    )

    # Steps
    steps: list[ProtocolStep] = Field(
        default_factory=list,
        description="Step-by-step instructions to follow",
    )

    # Safety
    do_not: list[str] = Field(
        default_factory=list,
        description="Things to absolutely avoid",
    )
    when_to_stop: list[str] = Field(
        default_factory=list,
        description="Conditions when you can stop the protocol",
    )


class EmergencyAlertRequest(BaseModel):
    """Request body for POST /api/emergency/alert."""

    latitude: float = Field(
        ...,
        description="GPS latitude of the emergency",
        ge=-90.0,
        le=90.0,
        examples=[24.8607],
    )
    longitude: float = Field(
        ...,
        description="GPS longitude of the emergency",
        ge=-180.0,
        le=180.0,
        examples=[67.0011],
    )
    situation: str = Field(
        ...,
        description="Brief description of the emergency",
        min_length=5,
        max_length=500,
        examples=["Person collapsed, not breathing. CPR in progress."],
    )
    contact_name: Optional[str] = Field(
        None,
        description="Name of the person reporting",
    )
    contact_phone: Optional[str] = Field(
        None,
        description="Phone number for callback",
    )


class EmergencyAlertResponse(BaseModel):
    """Response body for POST /api/emergency/alert."""

    sent: bool = Field(..., description="Whether the alert was sent")
    message: str = Field(
        ..., description="Status message"
    )
    google_maps_link: Optional[str] = Field(
        None, description="Google Maps link with coordinates"
    )
    timestamp: Optional[str] = Field(
        None, description="When the alert was sent"
    )


class ProtocolSummary(BaseModel):
    """Summary of a protocol for listing."""

    id: str = Field(..., description="Protocol ID")
    title: str = Field(..., description="Protocol title")
    category: str = Field(default="general", description="Category")
    severity_level: int = Field(default=3, description="Severity 1-5")
    call_ambulance: bool = Field(default=True)
    trigger_phrases: list[str] = Field(default_factory=list)


class ProtocolListResponse(BaseModel):
    """Response for GET /api/emergency/protocols."""

    count: int = Field(..., description="Total number of protocols")
    protocols: list[ProtocolSummary] = Field(
        ..., description="List of available protocols"
    )
