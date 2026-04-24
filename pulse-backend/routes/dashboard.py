import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from database import get_anon_client, run_supabase
from models.schemas import DashboardStatsResponse, DistrictScore

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def dashboard_stats(_user=Depends(get_current_user)):
    client = get_anon_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    try:
        total_q = run_supabase(client.table("symptom_reports").select("id", count="exact").execute)
        clusters_q = run_supabase(
            client.table("outbreak_alerts").select("id", count="exact").gte("created_at", since).execute
        )
        facilities_q = run_supabase(client.table("facilities").select("type").execute)
        districts_q = run_supabase(client.table("symptom_reports").select("district,urgency_level").execute)
        total, clusters, facilities, districts = await asyncio.gather(total_q, clusters_q, facilities_q, districts_q)

        facilities_count = {}
        for row in facilities.data or []:
            f_type = row.get("type") or "unknown"
            facilities_count[f_type] = facilities_count.get(f_type, 0) + 1

        by_district = {}
        for row in districts.data or []:
            district = row.get("district") or "Unknown"
            urgency = row.get("urgency_level") or 1
            metric = by_district.setdefault(district, {"reports": 0, "weighted": 0})
            metric["reports"] += 1
            metric["weighted"] += urgency

        district_scores = [
            DistrictScore(district=k, reports=v["reports"], score=round(v["weighted"] / max(v["reports"], 1), 2))
            for k, v in by_district.items()
        ]
        return DashboardStatsResponse(
            total_reports=total.count or 0,
            active_clusters=clusters.count or 0,
            facilities_count=facilities_count,
            district_scores=district_scores,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"dashboard stats failed: {exc}") from exc
