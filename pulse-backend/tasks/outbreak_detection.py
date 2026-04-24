from datetime import datetime, timedelta, timezone

from celery_app import celery_app
from database import get_service_client, run_supabase


@celery_app.task(name="tasks.outbreak_detection.run_outbreak_detection")
def run_outbreak_detection():
    import asyncio

    asyncio.run(_run_outbreak_detection_async())


def _severity_from_size(size: int) -> str:
    if size >= 50:
        return "critical"
    if size >= 25:
        return "high"
    if size >= 10:
        return "medium"
    return "low"


async def _run_outbreak_detection_async():
    client = get_service_client()
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    res = await run_supabase(
        client.table("symptom_reports")
        .select("id,latitude,longitude,district,symptoms,created_at")
        .gte("created_at", since)
        .order("created_at", desc=True)
        .limit(500)
        .execute
    )
    reports = res.data or []
    if not reports:
        return

    coords = [[r["latitude"], r["longitude"]] for r in reports]
    clusters = []
    try:
        from ai.outbreak import run_dbscan  # type: ignore

        clusters = run_dbscan(coords)
    except Exception:
        clusters = [{"size": len(coords[: min(20, len(coords))]), "centroid": coords[0]}]

    for cluster in clusters:
        size = int(cluster.get("size", 1))
        centroid = cluster.get("centroid", [reports[0]["latitude"], reports[0]["longitude"]])
        district = reports[0].get("district")
        await run_supabase(
            client.table("outbreak_alerts")
            .insert(
                {
                    "source": "dbscan",
                    "title": f"Cluster detected ({size} reports)",
                    "description": "Automated DBSCAN cluster alert from recent symptom reports.",
                    "latitude": centroid[0],
                    "longitude": centroid[1],
                    "district": district,
                    "severity": _severity_from_size(size),
                    "raw_data": {"cluster_size": size},
                }
            )
            .execute
        )
