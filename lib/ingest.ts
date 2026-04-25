/**
 * Legacy multipart ingest (optional). Primary integration is Pulse REST — see `lib/pulse-api/client.ts`.
 * `NEXT_PUBLIC_PULSE_API_BASE` — e.g. http://localhost:8000 (paths use /api/...).
 */
export function getIngestUrl(): string {
  const base = process.env.NEXT_PUBLIC_INGEST_URL?.trim();
  if (base) return base.replace(/\/$/, "");
  return "/api/ingest";
}
