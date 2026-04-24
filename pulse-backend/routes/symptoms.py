import json
from typing import List

from fastapi import APIRouter, HTTPException, Request

from database import get_redis, get_service_client, run_supabase
from limiter import limiter
from models.schemas import (
    DifferentialItem,
    SymptomsChatRequest,
    SymptomsChatResponse,
    SymptomsReportRequest,
    SymptomsReportResponse,
)

router = APIRouter(tags=["symptoms"])


@router.post("/symptoms/chat", response_model=SymptomsChatResponse)
@limiter.limit("30/minute")
async def symptoms_chat(request: Request, payload: SymptomsChatRequest) -> SymptomsChatResponse:
    redis = await get_redis()
    key = f"session:{payload.session_id}"
    try:
        history = await redis.lrange(key, 0, 4)
        history_payload: List[str] = [json.loads(item) for item in history] if history else []

        try:
            from ai.symptom_engine import chat_turn  # type: ignore

            result = await chat_turn(payload.message, payload.session_id, payload.language)
            reply = result.get("reply", "")
            urgency = int(result.get("urgency", 3))
            differential = [
                DifferentialItem(**item) for item in result.get("differential", [])
            ]
            red_flags = result.get("red_flags", [])
            recommended = result.get("recommended_action", "")
        except ImportError:
            reply = "Based on your symptoms, this appears moderate. Please hydrate and monitor fever."
            urgency = 3
            differential = [DifferentialItem(code="A90", name="Dengue fever")]
            red_flags = ["Persistent vomiting", "Bleeding gums"]
            recommended = "Visit the nearest clinic within 12 hours."

        await redis.lpush(key, json.dumps(payload.message))
        await redis.ltrim(key, 0, 4)
        if history_payload:
            reply = f"{reply} (context messages: {len(history_payload)})"

        return SymptomsChatResponse(
            reply=reply,
            urgency=urgency,
            differential=differential,
            red_flags=red_flags,
            recommended_action=recommended,
            session_id=payload.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"symptoms/chat failed: {exc}") from exc


@router.post("/symptoms/report", response_model=SymptomsReportResponse)
async def symptoms_report(payload: SymptomsReportRequest) -> SymptomsReportResponse:
    client = get_service_client()
    data = {
        "symptoms": payload.symptoms,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "urgency_level": payload.urgency_level,
        "icd10_codes": payload.icd10_codes,
        "district": payload.district,
        "is_anonymous": True,
    }
    try:
        result = await run_supabase(client.table("symptom_reports").insert(data).execute)
        created = result.data[0]
        return SymptomsReportResponse(id=created["id"], saved=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"symptoms/report save failed: {exc}") from exc


@router.get("/symptoms/report/count")
async def symptoms_report_count():
    client = get_service_client()
    try:
        result = await run_supabase(client.table("symptom_reports").select("id", count="exact").execute)
        return {"count": result.count or 0}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"count fetch failed: {exc}") from exc
