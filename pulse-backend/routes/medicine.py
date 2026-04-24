from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Request

from database import get_anon_client, run_supabase
from limiter import limiter
from models.schemas import MedicineScanRequest, MedicineScanResponse

router = APIRouter(tags=["medicine"])


@router.post("/medicine/scan", response_model=MedicineScanResponse)
@limiter.limit("10/minute")
async def medicine_scan(request: Request, payload: MedicineScanRequest) -> MedicineScanResponse:
    try:
        drug_name = "Paracetamol"
        dosage = "500mg"
        expiry = "2027-03-30"
        interactions = ["May interact with warfarin in high doses."]
        expired = datetime.fromisoformat(expiry) < datetime.utcnow()
        fda_info = {}

        try:
            from ai.gemini_client import identify_medicine  # type: ignore

            ai_result = await identify_medicine(payload.image_base64)
            drug_name = ai_result.get("drug_name", drug_name)
            dosage = ai_result.get("dosage", dosage)
            expiry = ai_result.get("expiry", expiry)
        except ImportError:
            pass

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://api.fda.gov/drug/ndc.json",
                params={"search": f"brand_name:{drug_name}", "limit": 1},
            )
            if r.status_code == 200:
                fda_info = r.json()

        db = get_anon_client()
        result = await run_supabase(
            db.table("drug_interactions")
            .select("description,severity")
            .or_(f"drug_a.ilike.%{drug_name}%,drug_b.ilike.%{drug_name}%")
            .limit(5)
            .execute
        )
        interactions = [x["description"] for x in (result.data or []) if x.get("description")] or interactions

        return MedicineScanResponse(
            drug_name=drug_name,
            dosage=dosage,
            expiry=expiry,
            interactions=interactions,
            fda_info=fda_info,
            expired=expired,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"medicine scan failed: {exc}") from exc
