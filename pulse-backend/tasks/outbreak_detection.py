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
        try:
            from ai.outbreak import run_dbscan
        except ImportError:
            try:
                from tasks.ai.outbreak import run_dbscan
            except ImportError:
                # Last resort: absolute import if pathing is weird
                import sys
                import os
                sys.path.append(os.path.join(os.getcwd(), "pulse-backend"))
                from ai.outbreak import run_dbscan
        clusters = run_dbscan(coords)
    except Exception as e:
        print(f"DBSCAN failed: {e}")
        clusters = [{"size": len(coords[: min(20, len(coords))]), "centroid": coords[0]}]

    for cluster in clusters:
        size = int(cluster.get("size", 1))
        centroid = cluster.get("centroid", [reports[0]["latitude"], reports[0]["longitude"]])
        district = reports[0].get("district")
        
        # Prophet Anomaly Detection
        prophet_anomalies = []
        try:
            try:
                from ai.prophet_helper import OutbreakDetector
            except ImportError:
                from .ai.prophet_helper import OutbreakDetector
            
            # Get historical daily counts for this district
            hist_res = await run_supabase(
                client.table("symptom_reports")
                .select("created_at")
                .eq("district", district)
                .execute
            )
            hist_reports = hist_res.data or []
            
            if len(hist_reports) > 60:
                # Group by date
                daily_counts = {}
                for hr in hist_reports:
                    date = hr['created_at'][:10]
                    daily_counts[date] = daily_counts.get(date, 0) + 1
                
                ts_data = [{"date": k, "cases": v} for k, v in daily_counts.items()]
                
                detector = OutbreakDetector(location=district)
                if detector.train(ts_data):
                    # Check if today's count is anomalous
                    prophet_anomalies = detector.detect_anomalies(ts_data)
        except Exception as e:
            print("Prophet failed:", e)

        # Merge insights
        description = "Automated DBSCAN cluster alert from recent symptom reports."
        severity = _severity_from_size(size)
        if prophet_anomalies and prophet_anomalies[-1]['is_anomaly']:
            description += " PROPHET ANOMALY DETECTED: Spike in cases exceeds expected seasonal trends!"
            severity = "critical"

        await run_supabase(
            client.table("outbreak_alerts")
            .insert(
                {
                    "source": "automated",
                    "title": f"Cluster detected ({size} reports)",
                    "description": description,
                    "latitude": centroid[0],
                    "longitude": centroid[1],
                    "district": district,
                    "severity": severity,
                    "raw_data": {"cluster_size": size, "prophet_anomaly": bool(prophet_anomalies)},
                }
            )
            .execute
        )
