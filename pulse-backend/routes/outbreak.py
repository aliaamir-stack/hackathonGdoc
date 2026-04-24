from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from database import get_anon_client, run_supabase
from models.schemas import Cluster, OutbreakResponse

router = APIRouter(tags=["outbreak"])


@router.get("/outbreak/clusters", response_model=OutbreakResponse)
async def outbreak_clusters():
    try:
        client = get_anon_client()
        res = await run_supabase(
            client.table("outbreak_alerts").select("*").order("created_at", desc=True).limit(20).execute
        )
        alerts = res.data or []
        clusters = [
            Cluster(
                center_lat=item.get("latitude") or 24.86,
                center_lng=item.get("longitude") or 67.01,
                size=8,
                dominant_symptom="fever",
            )
            for item in alerts[:3]
        ]
        anomalies = [
            {
                "district": item.get("district") or "Unknown",
                "severity": item.get("severity") or "medium",
                "title": item.get("title"),
            }
            for item in alerts[:5]
        ]
        heatmap_points = [[c.center_lat, c.center_lng, float(c.size)] for c in clusters]
        return OutbreakResponse(
            clusters=clusters,
            anomalies=anomalies,
            heatmap_points=heatmap_points,
            last_updated=datetime.now(timezone.utc),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"outbreak clusters failed: {exc}") from exc
