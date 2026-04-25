/** Types aligned with Pulse API_DOCUMENTATION.md */

export type SymptomsChatRequest = {
  message: string;
  session_id: string;
  language?: string;
};

export type DifferentialItem = { code: string; name: string };

export type SymptomsChatResponse = {
  reply: string;
  urgency: number;
  differential: DifferentialItem[];
  red_flags: string[];
  recommended_action: string;
  session_id: string;
};

export type SymptomReportRequest = {
  symptoms: string[];
  latitude: number;
  longitude: number;
  urgency_level: number;
  district: string;
};

export type OutbreakCluster = {
  center_lat: number;
  center_lng: number;
  size: number;
  dominant_symptom: string;
};

export type OutbreakDataResponse = {
  clusters: OutbreakCluster[];
  anomalies: unknown[];
  heatmap_points: [number, number, number][];
  last_updated: string;
};

export type MedFactVerifyRequest = { claim: string };

export type MedFactCitation = { title: string; url: string };

export type MedFactVerifyResponse = {
  verdict: string;
  confidence: number;
  summary: string;
  citations: MedFactCitation[];
};

export type MedicineScanRequest = { image_base64: string };

export type MedicineScanResponse = {
  drug_name: string;
  dosage: string;
  expired: boolean;
  interactions: string[];
};

export type EmergencyIdentifyResponse = {
  protocol: string;
  steps: string[];
  call_ambulance: boolean;
};

/** Doc does not define shape — treat as key/value summary for cards */
export type DashboardStats = Record<string, unknown>;

export type PulseApiError = { ok: false; message: string; status?: number };
export type PulseApiOk<T> = { ok: true; data: T };
export type PulseApiResult<T> = PulseApiOk<T> | PulseApiError;
