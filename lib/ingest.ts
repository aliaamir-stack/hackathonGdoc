/**
 * POST multipart form: fields `image` (optional File) and `audio` (optional File).
 * Set NEXT_PUBLIC_INGEST_URL to your full backend URL (e.g. https://api.example.com/v1/prescriptions/ingest).
 * If unset, requests go to /api/ingest (local stub for development).
 */
export function getIngestUrl(): string {
  const base = process.env.NEXT_PUBLIC_INGEST_URL?.trim();
  if (base) return base.replace(/\/$/, "");
  return "/api/ingest";
}
