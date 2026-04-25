import type {
  DashboardStats,
  EmergencyIdentifyResponse,
  MedFactVerifyRequest,
  MedFactVerifyResponse,
  MedicineScanRequest,
  MedicineScanResponse,
  OutbreakDataResponse,
  PulseApiResult,
  SymptomReportRequest,
  SymptomsChatRequest,
  SymptomsChatResponse,
} from "@/lib/pulse-api/types";

/**
 * Origin only (no trailing /api). Example: http://localhost:8000
 * Full REST paths are prefixed with /api per API documentation.
 */
export function getPulseApiOrigin(): string {
  const raw = process.env.NEXT_PUBLIC_PULSE_API_BASE?.trim();
  const base = raw && raw.length > 0 ? raw : "http://localhost:8000";
  return base.replace(/\/$/, "").replace(/\/api$/i, "");
}

export function pulseRestUrl(path: string): string {
  const origin = getPulseApiOrigin();
  const p = path.startsWith("/") ? path : `/${path}`;
  if (p.startsWith("/api")) return `${origin}${p}`;
  return `${origin}/api${p}`;
}

export function pulseOutbreakWsUrl(): string {
  const o = getPulseApiOrigin();
  return o.replace(/^http/i, (m) => (m.toLowerCase() === "https" ? "wss" : "ws")) + "/ws/outbreak";
}

export async function readPulseJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  if (!text) return {} as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(text.slice(0, 200) || "Invalid JSON");
  }
}

async function wrap<T>(p: Promise<Response>): Promise<PulseApiResult<T>> {
  try {
    const res = await p;
    if (!res.ok) {
      const t = await res.text();
      return { ok: false, message: t || res.statusText, status: res.status };
    }
    const data = (await readPulseJson<T>(res)) as T;
    return { ok: true, data };
  } catch (e) {
    return { ok: false, message: e instanceof Error ? e.message : "Request failed" };
  }
}

export function fileToBase64(file: File): Promise<string> {
  return file.arrayBuffer().then((buf) => {
    const bytes = new Uint8Array(buf);
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  });
}

export function blobToBase64(blob: Blob): Promise<string> {
  return blob.arrayBuffer().then((buf) => {
    const bytes = new Uint8Array(buf);
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  });
}

/** GET /api/dashboard/stats */
export function fetchDashboardStats(): Promise<PulseApiResult<DashboardStats>> {
  return wrap(fetch(pulseRestUrl("/api/dashboard/stats"), { method: "GET" }));
}

/** GET /api/outbreak/data */
export function fetchOutbreakData(): Promise<PulseApiResult<OutbreakDataResponse>> {
  return wrap(fetch(pulseRestUrl("/api/outbreak/data"), { method: "GET" }));
}

/** POST /api/symptoms/chat */
export function postSymptomsChat(
  body: SymptomsChatRequest,
): Promise<PulseApiResult<SymptomsChatResponse>> {
  return wrap(
    fetch(pulseRestUrl("/api/symptoms/chat"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

/** POST /api/symptoms/report */
export function postSymptomsReport(
  body: SymptomReportRequest,
): Promise<PulseApiResult<unknown>> {
  return wrap(
    fetch(pulseRestUrl("/api/symptoms/report"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

/** POST /api/medfact/verify */
export function postMedFactVerify(
  body: MedFactVerifyRequest,
): Promise<PulseApiResult<MedFactVerifyResponse>> {
  return wrap(
    fetch(pulseRestUrl("/api/medfact/verify"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

/** POST /api/medicine/scan — JSON image_base64 */
export function postMedicineScan(
  body: MedicineScanRequest,
): Promise<PulseApiResult<MedicineScanResponse>> {
  return wrap(
    fetch(pulseRestUrl("/api/medicine/scan"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

/**
 * POST /api/emergency/identify — doc shows response only.
 * Order: multipart `audio` → JSON `{ audio_base64 }` → JSON `{ transcription }`.
 */
export async function postEmergencyIdentify(params: {
  audio?: Blob | null;
  transcription?: string;
  audioFileName?: string;
}): Promise<PulseApiResult<EmergencyIdentifyResponse>> {
  const { audio, transcription, audioFileName = "recording.webm" } = params;

  if (audio && audio.size > 0) {
    const fd = new FormData();
    fd.append("audio", audio, audioFileName);
    if (transcription?.trim()) fd.append("transcription", transcription.trim());
    const multipart = await wrap<EmergencyIdentifyResponse>(
      fetch(pulseRestUrl("/api/emergency/identify"), { method: "POST", body: fd }),
    );
    if (multipart.ok) return multipart;

    try {
      const audio_base64 = await blobToBase64(audio);
      const jsonAudio = await wrap<EmergencyIdentifyResponse>(
        fetch(pulseRestUrl("/api/emergency/identify"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            audio_base64,
            ...(transcription?.trim() ? { transcription: transcription.trim() } : {}),
          }),
        }),
      );
      if (jsonAudio.ok) return jsonAudio;
    } catch {
      /* continue */
    }
  }

  if (transcription?.trim()) {
    return wrap(
      fetch(pulseRestUrl("/api/emergency/identify"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcription: transcription.trim() }),
      }),
    );
  }

  return { ok: false, message: "Provide audio recording and/or a call transcript." };
}
