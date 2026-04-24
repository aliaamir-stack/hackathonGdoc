"""
Emergency Guide API Routes — FastAPI endpoints for emergency protocols.

Endpoints:
- POST /api/emergency/identify — Match voice/text to emergency protocol
- POST /api/emergency/alert — Send Email GPS emergency alert
- GET  /api/emergency/protocols — List all available protocols
- GET  /api/emergency/protocols/{id} — Get specific protocol details
"""

import logging
from fastapi import APIRouter, HTTPException

# ==========================================
# NOTE FOR M2 (Backend Lead):
# Call `await protocol_matcher.sync_with_redis()` in your main.py
# lifespan/startup event to cache the protocols in Upstash Redis!
# ==========================================

from m5_features.models.emergency_models import (
    EmergencyIdentifyRequest,
    EmergencyIdentifyResponse,
    EmergencyAlertRequest,
    EmergencyAlertResponse,
    ProtocolListResponse,
    ProtocolSummary,
    ProtocolStep,
)
from m5_features.emergency.protocol_matcher import protocol_matcher
from m5_features.emergency.email_alert import email_alert_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/emergency", tags=["Emergency Guide"])


@router.post(
    "/identify",
    response_model=EmergencyIdentifyResponse,
    summary="Identify emergency protocol from voice/text",
    description=(
        "Accepts transcribed voice text or typed emergency description, "
        "matches it to the best emergency protocol using keyword matching "
        "and Gemini AI, and returns step-by-step instructions."
    ),
)
async def identify_emergency(
    request: EmergencyIdentifyRequest,
) -> EmergencyIdentifyResponse:
    """
    Match transcribed voice input to an emergency protocol.

    Flow:
    1. Web Speech API transcribes voice → sends text here
    2. Keyword matching + Gemini AI identify the protocol
    3. Returns full protocol with step-by-step instructions
    4. Frontend reads steps via Web Speech TTS
    """
    logger.info(f"Emergency identify request: '{request.transcribed_text[:100]}'")

    try:
        # Match to protocol
        result = protocol_matcher.match(request.transcribed_text)

        if not result.matched:
            return EmergencyIdentifyResponse(
                matched=False,
                confidence=0.0,
                method="none",
                reasoning="No matching protocol found for the described situation",
            )

        # Build response with full protocol data
        protocol = result.protocol_data or {}
        steps = [
            ProtocolStep(**step)
            for step in protocol.get("steps", [])
        ]

        response = EmergencyIdentifyResponse(
            matched=True,
            confidence=result.confidence,
            method=result.method,
            reasoning=result.reasoning,
            protocol_id=result.protocol_id,
            protocol_title=result.protocol_title,
            category=protocol.get("category"),
            severity_level=protocol.get("severity_level"),
            call_ambulance=protocol.get("call_ambulance", True),
            immediate_action=protocol.get("immediate_action"),
            steps=steps,
            do_not=protocol.get("do_not", []),
            when_to_stop=protocol.get("when_to_stop", []),
        )

        logger.info(
            f"Matched protocol: {result.protocol_id} "
            f"(confidence: {result.confidence:.2f}, method: {result.method})"
        )
        return response

    except Exception as e:
        logger.error(f"Emergency identify error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Protocol matching failed: {str(e)}",
        )


@router.post(
    "/alert",
    response_model=EmergencyAlertResponse,
    summary="Send emergency email alert with GPS",
    description=(
        "Sends an emergency alert email via Gmail "
        "with GPS coordinates, Google Maps link, and situation description."
    ),
)
async def send_alert(request: EmergencyAlertRequest) -> EmergencyAlertResponse:
    """
    Send emergency GPS alert via Email.

    Sends a formatted HTML email to the configured recipient
    with the emergency location, situation description, and
    a Google Maps link for navigation.
    """
    logger.info(
        f"Emergency alert: lat={request.latitude}, lng={request.longitude}, "
        f"situation='{request.situation[:50]}'"
    )

    try:
        result = await email_alert_service.send_emergency_alert(
            latitude=request.latitude,
            longitude=request.longitude,
            situation=request.situation,
            contact_name=request.contact_name,
            contact_phone=request.contact_phone,
        )
        return result

    except Exception as e:
        logger.error(f"Email alert error: {e}")
        return EmergencyAlertResponse(
            sent=False,
            message=f"Alert failed: {str(e)}",
        )


@router.get(
    "/protocols",
    response_model=ProtocolListResponse,
    summary="List all emergency protocols",
    description="Returns a summary of all 15 available emergency protocols.",
)
async def list_protocols() -> ProtocolListResponse:
    """List all available emergency protocols."""
    summaries = protocol_matcher.get_all_protocol_summaries()
    return ProtocolListResponse(
        count=len(summaries),
        protocols=[ProtocolSummary(**s) for s in summaries],
    )


@router.get(
    "/protocols/{protocol_id}",
    summary="Get a specific protocol by ID",
    description="Returns the full details of a specific emergency protocol.",
)
async def get_protocol(protocol_id: str):
    """Get a specific emergency protocol by its ID."""
    protocol = protocol_matcher.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404,
            detail=f"Protocol '{protocol_id}' not found",
        )
    return protocol


@router.get(
    "/health",
    summary="Emergency guide health check",
)
async def emergency_health():
    """Health check for the emergency guide service."""
    return {
        "service": "emergency_guide",
        "status": "operational",
        "protocols_loaded": len(protocol_matcher.protocols),
        "protocol_ids": protocol_matcher.get_all_protocol_ids(),
        "gemini_available": gemini_client_status(),
    }


def gemini_client_status() -> bool:
    """Check if Gemini client is available."""
    try:
        from m5_features.ai.gemini_client import gemini_client
        return gemini_client.is_configured
    except Exception:
        return False
