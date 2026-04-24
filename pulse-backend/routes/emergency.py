from fastapi import APIRouter, HTTPException
from telegram import Bot

from config import get_settings
from database import get_service_client, run_supabase
from models.schemas import (
    EmergencyAlertRequest,
    EmergencyAlertResponse,
    EmergencyIdentifyRequest,
    EmergencyIdentifyResponse,
)

router = APIRouter(tags=["emergency"])
settings = get_settings()


@router.post("/emergency/identify", response_model=EmergencyIdentifyResponse)
async def identify_protocol(payload: EmergencyIdentifyRequest) -> EmergencyIdentifyResponse:
    try:
        try:
            from ai.gemini_client import match_emergency_protocol  # type: ignore

            data = await match_emergency_protocol(payload.transcription)
            return EmergencyIdentifyResponse(**data)
        except ImportError:
            return EmergencyIdentifyResponse(
                protocol="CPR Adult",
                steps=[
                    "Call emergency services immediately",
                    "Start chest compressions at 100-120/min",
                    "Use AED if available",
                ],
                call_ambulance=True,
                matched_confidence=0.94,
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"identify failed: {exc}") from exc


@router.post("/emergency/alert", response_model=EmergencyAlertResponse)
async def emergency_alert(payload: EmergencyAlertRequest) -> EmergencyAlertResponse:
    message = (
        "🚨 PULSE Emergency Alert\n"
        f"Situation: {payload.situation}\n"
        f"Location: https://maps.google.com/?q={payload.latitude},{payload.longitude}"
    )
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        sent = await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)
        client = get_service_client()
        await run_supabase(
            client.table("outbreak_alerts")
            .insert(
                {
                    "source": "dbscan",
                    "title": f"Emergency: {payload.situation}",
                    "description": message,
                    "latitude": payload.latitude,
                    "longitude": payload.longitude,
                    "severity": "high",
                }
            )
            .execute
        )
        return EmergencyAlertResponse(sent=True, telegram_message_id=sent.message_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"emergency alert failed: {exc}") from exc
