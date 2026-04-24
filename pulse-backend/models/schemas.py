from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class MedFactRequest(BaseModel):
    claim: str


class Citation(BaseModel):
    title: str
    source: str
    url: str


class MedFactResponse(BaseModel):
    verdict: str
    confidence: float
    sub_claims: List[str]
    citations: List[Citation]
    summary: str


class SymptomsChatRequest(BaseModel):
    message: str
    session_id: str
    language: Literal["en", "ur"] = "en"


class DifferentialItem(BaseModel):
    code: str
    name: str


class SymptomsChatResponse(BaseModel):
    reply: str
    urgency: int = Field(ge=1, le=5)
    differential: List[DifferentialItem]
    red_flags: List[str]
    recommended_action: str
    session_id: str


class SymptomsReportRequest(BaseModel):
    symptoms: List[str]
    latitude: float
    longitude: float
    urgency_level: int = Field(ge=1, le=5)
    icd10_codes: List[str] = []
    district: Optional[str] = None


class SymptomsReportResponse(BaseModel):
    id: str
    saved: bool


class MedicineScanRequest(BaseModel):
    image_base64: str


class MedicineScanResponse(BaseModel):
    drug_name: str
    dosage: str
    expiry: str
    interactions: List[str]
    fda_info: Dict[str, Any]
    expired: bool


class FacilityItem(BaseModel):
    id: str
    name: str
    type: str
    latitude: float
    longitude: float
    address: Optional[str] = None


class FacilitiesResponse(BaseModel):
    facilities: List[FacilityItem]
    count: int


class Cluster(BaseModel):
    center_lat: float
    center_lng: float
    size: int
    dominant_symptom: str


class OutbreakResponse(BaseModel):
    clusters: List[Cluster]
    anomalies: List[Dict[str, Any]]
    heatmap_points: List[List[float]]
    last_updated: datetime


class EmergencyIdentifyRequest(BaseModel):
    transcription: str


class EmergencyIdentifyResponse(BaseModel):
    protocol: str
    steps: List[str]
    call_ambulance: bool
    matched_confidence: float


class EmergencyAlertRequest(BaseModel):
    latitude: float
    longitude: float
    situation: str


class EmergencyAlertResponse(BaseModel):
    sent: bool
    telegram_message_id: int


class DistrictScore(BaseModel):
    district: str
    reports: int
    score: float


class DashboardStatsResponse(BaseModel):
    total_reports: int
    active_clusters: int
    facilities_count: Dict[str, int]
    district_scores: List[DistrictScore]


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
