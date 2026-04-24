from fastapi import APIRouter, HTTPException, Query

from database import get_anon_client, run_supabase
from models.schemas import FacilitiesResponse, FacilityItem

router = APIRouter(tags=["facilities"])


async def _fetch_facilities(lat: float, lng: float, radius_km: float, f_type: str | None):
    # Fallback select; production should use RPC with PostGIS ST_DWithin.
    client = get_anon_client()
    query = client.table("facilities").select("*").limit(20)
    if f_type:
        query = query.eq("type", f_type)
    result = await run_supabase(query.execute)
    return result.data or []


@router.get("/facilities", response_model=FacilitiesResponse)
async def get_facilities(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0),
    type: str | None = Query(None),
    urgency: int | None = Query(None),
):
    try:
        final_type = "hospital" if urgency == 5 else type
        rows = await _fetch_facilities(lat, lng, radius_km, final_type)
        facilities = [FacilityItem(**row) for row in rows]
        return FacilitiesResponse(facilities=facilities, count=len(facilities))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"facilities fetch failed: {exc}") from exc


@router.get("/facilities/nearby", response_model=FacilitiesResponse)
async def get_facilities_nearby(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0),
    type: str | None = Query(None),
    urgency: int | None = Query(None),
):
    return await get_facilities(lat=lat, lng=lng, radius_km=radius_km, type=type, urgency=urgency)
