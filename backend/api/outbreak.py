# backend/api/outbreak.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from backend.utils.prophet_helper import OutbreakDetector
from backend.models.anomaly import Anomaly
from backend.database import SessionLocal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outbreak", tags=["outbreak"])

# --- Request/Response schemas ---

class CasePoint(BaseModel):
    date: str
    cases: int

class DetectRequest(BaseModel):
    location: str
    case_data: List[CasePoint]


# --- Endpoints ---

@router.post("/detect")
def detect_anomalies(body: DetectRequest):
    """
    POST /api/outbreak/detect

    Request body:
    {
        "location": "Karachi",
        "case_data": [
            {"date": "2026-01-01", "cases": 10},
            {"date": "2026-01-02", "cases": 12}
        ]
    }

    Response:
    {
        "location": "Karachi",
        "anomalies": [...],
        "count": 1
    }
    """
    case_data = [p.dict() for p in body.case_data]

    detector = OutbreakDetector(body.location)
    if not detector.train(case_data):
        raise HTTPException(status_code=400, detail="Training failed (insufficient data)")

    anomalies = detector.detect_anomalies(case_data)

    return {
        "location": body.location,
        "anomalies": anomalies,
        "count": len(anomalies)
    }


@router.get("/history/{location}")
def get_anomaly_history(location: str, days: int = Query(default=30, ge=1)):
    """
    GET /api/outbreak/history/Karachi?days=30

    Returns all anomalies detected for a location.
    """
    with SessionLocal() as session:
        anomalies = (
            session.query(Anomaly)
            .filter_by(location=location)
            .order_by(Anomaly.date.desc())
            .limit(days * 2)
            .all()
        )
        return {
            "location": location,
            "anomalies": [a.to_dict() for a in anomalies]
        }


@router.get("/stats/{location}")
def get_outbreak_stats(location: str):
    """
    GET /api/outbreak/stats/Karachi

    Returns summary statistics for the last 7 days.
    """
    week_ago = datetime.utcnow() - timedelta(days=7)

    with SessionLocal() as session:
        recent_anomalies = (
            session.query(Anomaly)
            .filter(Anomaly.location == location, Anomaly.date >= week_ago)
            .all()
        )

    avg_severity = (
        sum(a.severity for a in recent_anomalies) / len(recent_anomalies)
        if recent_anomalies else 0
    )

    return {
        "location": location,
        "anomalies_this_week": len(recent_anomalies),
        "average_severity": avg_severity,
        "high_severity_count": len([a for a in recent_anomalies if a.severity > 0.8])
    }