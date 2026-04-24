// Single source of truth for all roadmap content. Keep prose verbatim from the brief.
export type AccentKey = "vital" | "map-blue" | "alert-red" | "alert-amber" | "signal-purple" | "signal-teal";

export const STATS = [
  { num: "15h", label: "Build window" },
  { num: "07", label: "Modules" },
  { num: "₨0", label: "Total cost" },
  { num: "06", label: "Operators" },
];

// Pin coordinates expressed in % of an asymmetric grid for the Features section.
export type Feature = {
  id: string;
  num: string;
  icon: string;
  title: string;
  desc: string;
  tech: string;
  accent: AccentKey;
  // pin position over a Pakistan-shaped backdrop (0-100)
  x: number;
  y: number;
};

export const FEATURES: Feature[] = [
  {
    id: "medfact",
    num: "01",
    icon: "◈",
    title: "MedFact Shield",
    desc: "Streaming RAG over 5,000 PubMed abstracts. Verdict badge, citation cards, source links — debunks medical misinformation in real time.",
    tech: "Gemini · LangChain · Chroma",
    accent: "vital",
    x: 22, y: 24,
  },
  {
    id: "symptom",
    num: "02",
    icon: "◊",
    title: "Symptom Navigator",
    desc: "Conversational triage. Maps free-text symptoms to ICD-10 codes, scores urgency, exports a clinician-ready PDF.",
    tech: "Gemini · medspaCy · ICD-10",
    accent: "map-blue",
    x: 58, y: 18,
  },
  {
    id: "scanner",
    num: "03",
    icon: "▣",
    title: "Medicine Scanner",
    desc: "Camera capture → Gemini Vision OCR → drug name, dosage, interactions, expiry warning. Works on any phone.",
    tech: "Gemini Vision · OpenFDA",
    accent: "signal-purple",
    x: 78, y: 38,
  },
  {
    id: "emergency",
    num: "04",
    icon: "✚",
    title: "Emergency Guide",
    desc: "Voice-first protocol playback for CPR, choking, bleeding, burns. Cached for offline use during outages.",
    tech: "Web Speech · PWA",
    accent: "alert-red",
    x: 18, y: 58,
  },
  {
    id: "locator",
    num: "05",
    icon: "◉",
    title: "Resource Locator",
    desc: "Live map of 3,000+ hospitals, pharmacies, blood banks, AEDs. OSRM routing to the nearest open facility.",
    tech: "OSM · OSRM · Leaflet",
    accent: "signal-teal",
    x: 50, y: 62,
  },
  {
    id: "outbreak",
    num: "06",
    icon: "◎",
    title: "Outbreak Radar",
    desc: "DBSCAN clustering on 300+ symptom reports, Prophet anomaly detection, Telegram alerts. The showstopper.",
    tech: "DBSCAN · Prophet · WebSocket",
    accent: "alert-amber",
    x: 80, y: 70,
  },
  {
    id: "dashboard",
    num: "07",
    icon: "▤",
    title: "Health Dashboard",
    desc: "JWT-protected. Pakistan district choropleth. 30-day timeline scrubber. Health score = outbreak proximity + facility access + report volume. FHIR R4 export.",
    tech: "GeoJSON · Recharts · FHIR",
    accent: "vital",
    x: 38, y: 84,
  },
];

export type StackLayer = {
  id: string;
  label: string;
  meta: string;
  accent: AccentKey;
  pills: { name: string; primary?: boolean }[];
  note: string;
  liveTag: string;
};

export const STACK: StackLayer[] = [
  {
    id: "frontend",
    label: "Frontend",
    meta: "Next.js 14 · TypeScript · Tailwind · Leaflet",
    accent: "map-blue",
    pills: [
      { name: "Next.js 14 App Router", primary: true },
      { name: "TypeScript strict", primary: true },
      { name: "Tailwind CSS" },
      { name: "shadcn/ui" },
      { name: "Framer Motion" },
      { name: "react-leaflet" },
      { name: "leaflet.heat" },
      { name: "Recharts" },
      { name: "Web Speech API" },
      { name: "Quagga.js (barcode)" },
      { name: "PWA + Service Worker" },
    ],
    note: "WebSocket client for live outbreak updates · Camera API for pill scanning · OSM tiles, no Mapbox key needed.",
    liveTag: "200 OK · 14 ms",
  },
  {
    id: "backend",
    label: "Backend",
    meta: "FastAPI · Python 3.12 · Async everywhere",
    accent: "vital",
    pills: [
      { name: "FastAPI + Uvicorn", primary: true },
      { name: "Pydantic v2", primary: true },
      { name: "SQLAlchemy async" },
      { name: "WebSockets" },
      { name: "Celery + Redis" },
      { name: "feedparser (WHO RSS)" },
      { name: "pytesseract + cv2" },
      { name: "python-telegram-bot" },
      { name: "httpx async" },
      { name: "python-jose (JWT)" },
      { name: "slowapi (rate limiting)" },
    ],
    note: "SSE streaming for Gemini · JWT auth on dashboard · Celery: WHO RSS hourly, DBSCAN every 15 min.",
    liveTag: "204 OK · 8 ms",
  },
  {
    id: "ai",
    label: "AI / ML Pipeline",
    meta: "Gemini 1.5 Flash · LangChain · DBSCAN · Prophet",
    accent: "signal-purple",
    pills: [
      { name: "Gemini 1.5 Flash", primary: true },
      { name: "Gemini Vision", primary: true },
      { name: "LangChain RAG" },
      { name: "SentenceTransformers MiniLM-L6" },
      { name: "ChromaDB" },
      { name: "scikit-learn DBSCAN" },
      { name: "Facebook Prophet" },
      { name: "spaCy + medspaCy" },
      { name: "ConversationMemory" },
      { name: "reportlab (PDF)" },
    ],
    note: "RAG: 512 tok / 50 overlap · DBSCAN ε=0.02° (~2 km), min_samples=5 · Gemini free tier: 1M tok/day.",
    liveTag: "INFER · 312 ms",
  },
  {
    id: "data",
    label: "Data Layer",
    meta: "Supabase · Upstash Redis · ChromaDB",
    accent: "alert-amber",
    pills: [
      { name: "Supabase PostgreSQL", primary: true },
      { name: "Supabase Realtime", primary: true },
      { name: "Upstash Redis" },
      { name: "ChromaDB (Docker)" },
      { name: "TimescaleDB" },
    ],
    note: "Supabase free: 500 MB, 2 GB bandwidth · Upstash free: 10k commands/day · All cloud-managed.",
    liveTag: "WS · 312 sub",
  },
  {
    id: "datasets",
    label: "Free Datasets",
    meta: "PubMed · ICD-10 · DrugBank · OSM · WHO",
    accent: "alert-red",
    pills: [
      { name: "PubMed (NCBI E-utilities)", primary: true },
      { name: "WHO ICD-10 (14k rows)", primary: true },
      { name: "OpenFDA drug DB", primary: true },
      { name: "DrugBank interactions" },
      { name: "OSM Overpass" },
      { name: "WHO Outbreak RSS" },
      { name: "Pakistan admin GeoJSON" },
      { name: "MedlinePlus (NIH)" },
    ],
    note: "~5,000 PubMed abstracts · ~3,000 OSM facilities in Pakistan · ~14,000 ICD-10 codes. All free.",
    liveTag: "INDEX · 5,142",
  },
  {
    id: "deploy",
    label: "Deployment",
    meta: "Vercel (frontend) · Render (backend)",
    accent: "signal-teal",
    pills: [
      { name: "Vercel — free forever", primary: true },
      { name: "Render — free tier", primary: true },
      { name: "GitHub Actions" },
    ],
    note: "Render free tier sleeps after 15 min. Hit /ping 30 s before the demo. Wake takes ~30 s.",
    liveTag: "DEPLOY · OK",
  },
];

export type SetupItem = { id: string; name: string; how: string; badge: string; link?: string };

export const SETUP_GROUPS: { title: string; items: SetupItem[] }[] = [
  {
    title: "Accounts to create — all free",
    items: [
      { id: "gemini", name: "Google AI Studio — Gemini API key", how: "Main AI engine. Free, no credit card. aistudio.google.com → Get API key.", badge: "Free forever", link: "https://aistudio.google.com" },
      { id: "supabase", name: "Supabase — URL + Anon + Service key", how: "Hosted Postgres + Realtime WebSockets. Settings → API → copy 3 values.", badge: "Free tier", link: "https://app.supabase.com" },
      { id: "upstash", name: "Upstash — Redis connection string", how: "Serverless Redis, 10k commands/day free. Console → Create DB → copy rediss:// URL.", badge: "Free tier", link: "https://console.upstash.com" },
      { id: "telegram", name: "Telegram — Bot token + chat ID", how: "Message @BotFather → /newbot → token. Then @userinfobot → numeric chat_id.", badge: "Free forever" },
      { id: "ncbi", name: "NCBI / PubMed E-Utilities key", how: "Raises ingestion 3 → 10 req/sec. ncbi.nlm.nih.gov/account → My NCBI → API key.", badge: "Free", link: "https://www.ncbi.nlm.nih.gov/account" },
      { id: "vercel", name: "Vercel + Render accounts", how: "Sign in with GitHub on both. Connect repo. Auto-deploys on push.", badge: "Free tier" },
    ],
  },
  {
    title: "Run-once seed scripts",
    items: [
      { id: "pubmed-seed", name: "Ingest 5,000 PubMed abstracts", how: "Pulls infectious-disease abstracts via E-utils, embeds with MiniLM-L6, stores in Chroma.", badge: "Run once" },
      { id: "icd-seed", name: "Load 14k ICD-10 codes", how: "Bulk insert WHO ICD-10 CSV into icd10_codes table. Used by Symptom Navigator.", badge: "Run once" },
      { id: "osm-seed", name: "Cache 3k Pakistan facilities", how: "Overpass query for hospitals, pharmacies, blood banks across major cities.", badge: "Run once" },
      { id: "report-seed", name: "Generate 300 mock symptom reports", how: "Realistic lat/lng across Karachi, Lahore, Islamabad — populates outbreak radar for the demo.", badge: "Run once" },
    ],
  },
  {
    title: "Free APIs — zero setup",
    items: [
      { id: "openfda", name: "OpenFDA", how: "api.fda.gov/drug/ndc.json — no key required.", badge: "No key" },
      { id: "overpass", name: "OSM Overpass", how: "overpass-api.de/api/interpreter — no key.", badge: "No key" },
      { id: "osrm", name: "OSRM Routing", how: "router.project-osrm.org — free public server.", badge: "No key" },
      { id: "who-rss", name: "WHO Outbreak RSS", how: "who.int/rss-feeds/news-english.xml", badge: "No key" },
      { id: "tiles", name: "OSM Map Tiles", how: "tile.openstreetmap.org/{z}/{x}/{y}.png", badge: "No key" },
      { id: "geojson", name: "Pakistan GeoJSON", how: "data.humdata.org/dataset/cod-ab-pak", badge: "Open data", link: "https://data.humdata.org/dataset/cod-ab-pak" },
    ],
  },
];

export type EnvLine =
  | { kind: "comment"; text: string }
  | { kind: "var"; key: string; value: string; powers?: string }
  | { kind: "blank" };

export const ENV_LINES: EnvLine[] = [
  { kind: "comment", text: "# ── AI ENGINE ────────────────────────────────────" },
  { kind: "var", key: "GEMINI_API_KEY", value: "AIza...", powers: "MedFact Shield · Symptom Navigator · Medicine Scanner" },
  { kind: "blank" },
  { kind: "comment", text: "# ── DATABASE (Supabase — free tier) ─────────────" },
  { kind: "var", key: "SUPABASE_URL", value: "https://xxxx.supabase.co", powers: "All persistent data + Realtime feed" },
  { kind: "var", key: "SUPABASE_ANON_KEY", value: "eyJ...", powers: "Frontend Realtime subscription on outbreak page" },
  { kind: "var", key: "SUPABASE_SERVICE_KEY", value: "eyJ...", powers: "Backend admin writes (seed scripts, Celery)" },
  { kind: "var", key: "DATABASE_URL", value: "postgresql+asyncpg://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres", powers: "SQLAlchemy async pool" },
  { kind: "blank" },
  { kind: "comment", text: "# ── REDIS (Upstash — free tier) ─────────────────" },
  { kind: "var", key: "REDIS_URL", value: "rediss://default:TOKEN@xxxx.upstash.io:6379", powers: "Celery broker + rate-limit cache" },
  { kind: "blank" },
  { kind: "comment", text: "# ── EMERGENCY ALERTS (Telegram — free) ──────────" },
  { kind: "var", key: "TELEGRAM_BOT_TOKEN", value: "123456789:ABC-xxxx", powers: "Outbreak Radar push alerts" },
  { kind: "var", key: "TELEGRAM_CHAT_ID", value: "your_personal_chat_id", powers: "Where alerts are delivered" },
  { kind: "blank" },
  { kind: "comment", text: "# ── MEDICAL DATA APIs (free, no billing) ────────" },
  { kind: "var", key: "NCBI_API_KEY", value: "your_ncbi_key", powers: "PubMed ingestion rate boost" },
  { kind: "comment", text: "# OpenFDA · Overpass · OSRM — no keys needed" },
  { kind: "blank" },
  { kind: "comment", text: "# ── VECTOR DB (local Docker) ─────────────────────" },
  { kind: "var", key: "CHROMA_HOST", value: "localhost", powers: "RAG vector store" },
  { kind: "var", key: "CHROMA_PORT", value: "8001", powers: "RAG vector store" },
  { kind: "blank" },
  { kind: "comment", text: "# ── APP ───────────────────────────────────────────" },
  { kind: "var", key: "JWT_SECRET", value: "paste_your_32_char_random_string_here", powers: "Dashboard route signing" },
  { kind: "var", key: "NEXT_PUBLIC_API_URL", value: "https://your-app.onrender.com", powers: "Frontend → Backend" },
  { kind: "var", key: "NEXT_PUBLIC_SUPABASE_URL", value: "https://xxxx.supabase.co", powers: "Frontend Realtime" },
  { kind: "var", key: "NEXT_PUBLIC_SUPABASE_ANON_KEY", value: "eyJ...", powers: "Frontend Realtime auth" },
  { kind: "var", key: "ENVIRONMENT", value: "development", powers: "Toggles logging + CORS" },
];

export type Member = {
  id: number;
  code: string;
  name: string;
  role: string;
  stack: string;
  accent: AccentKey;
  warn: string;
  tasks: { time: string; text: string; cmd?: string }[];
  needs: { name: string; how: string }[];
  // angular position around the war-room circle (0 = top, clockwise, degrees)
  angle: number;
  // who they depend on (other member ids)
  deps: number[];
};

export const MEMBERS: Member[] = [
  {
    id: 1, code: "M1", name: "Frontend Master", role: "Owns the pixels",
    stack: "Next.js · Leaflet · shadcn/ui · Framer Motion · PWA",
    accent: "map-blue", angle: 0, deps: [2],
    warn: "You carry the demo. If it looks bad, judges don't care how good the backend is. Visual impact over completeness — always.",
    tasks: [
      { time: "6:10 – 7:00 PM", text: "Bootstrap Next.js 14 + TypeScript + Tailwind + shadcn. Push to GitHub. Folder structure.", cmd: "npx create-next-app@latest pulse-frontend --typescript --tailwind --app" },
      { time: "7:00 – 8:30 PM", text: "Global layout: navbar, 7-link sidebar, loading skeletons, dark/light toggle, shared Card / Badge / Button." },
      { time: "8:30 – 10:00 PM", text: "MedFact Shield page (streaming + citations + verdict badge) + Symptom Navigator (chat, urgency meter, PDF download)." },
      { time: "10:00 PM – 12:00 AM", text: "Medicine Scanner (camera + pill result card). Emergency Guide (voice button, step cards, protocol selector, TTS indicator)." },
      { time: "12:00 – 2:00 AM", text: "Resource Locator: Leaflet map + facility detail panel + routing line + AED highlight.", cmd: "npm install leaflet react-leaflet leaflet.heat" },
      { time: "2:00 – 5:00 AM", text: "Outbreak Radar: full-screen heatmap, WebSocket live updates, WHO pins, district sidebar, anomaly banner. Make it spectacular." },
      { time: "5:00 – 7:00 AM", text: "Health Dashboard: choropleth + score cards + Recharts trends + timeline scrubber + JWT route wrapper." },
      { time: "7:00 – 8:30 AM", text: "PWA manifest + service worker (offline emergency protocols). Framer Motion. Mobile pass on all 7 pages." },
      { time: "8:30 – 9:00 AM", text: "Deploy to Vercel. Set NEXT_PUBLIC_ env vars. Test every page live. Share URL." },
    ],
    needs: [
      { name: "NEXT_PUBLIC_API_URL", how: "From M6 once Render is live." },
      { name: "Supabase anon key + URL", how: "From M2. Needed for outbreak Realtime." },
      { name: "Pakistan GeoJSON file", how: "data.humdata.org → district boundaries." },
      { name: "Vercel account", how: "Sign up with GitHub → connect repo." },
    ],
  },
  {
    id: 2, code: "M2", name: "Backend Lead", role: "The glue",
    stack: "FastAPI · Supabase · Upstash · JWT · WebSockets · Celery",
    accent: "vital", angle: 60, deps: [3, 5],
    warn: "Every other member depends on your endpoints. Get GET /health live in the first hour and share the URL immediately.",
    tasks: [
      { time: "6:10 – 7:00 PM", text: "FastAPI project + deps + Supabase + Upstash. Deploy /health to Render. Share URL.", cmd: "pip install fastapi uvicorn sqlalchemy asyncpg supabase redis celery python-jose pydantic httpx python-dotenv" },
      { time: "7:00 – 9:00 PM", text: "DB schema in Supabase SQL editor: symptom_reports, facilities, icd10_codes, drug_interactions, users, outbreak_alerts. Enable Realtime." },
      { time: "9:00 – 11:00 PM", text: "Stub all 7 route files with mock JSON so M1 can wire UI immediately." },
      { time: "11:00 PM – 1:00 AM", text: "JWT auth, SSE streaming endpoint for Gemini, WebSocket /ws/outbreak broadcasting Realtime events." },
      { time: "1:00 – 3:00 AM", text: "Celery: fetch_who_rss (hourly) + run_dbscan (every 15 min). Telegram alert on new cluster." },
      { time: "3:00 – 6:00 AM", text: "Wire all real handlers to M3 (AI) and M5 (data) functions. Rate limiting via slowapi." },
      { time: "6:00 – 9:00 AM", text: "Polish, error handling, deploy final to Render. Hit /ping right before demo." },
    ],
    needs: [
      { name: "Supabase service key", how: "From the same Supabase project as M1." },
      { name: "Upstash Redis URL", how: "From console.upstash.com → Create DB." },
      { name: "Render account", how: "render.com → New Web Service → connect repo." },
    ],
  },
  {
    id: 3, code: "M3", name: "AI / RAG Engineer", role: "Brains",
    stack: "Gemini · LangChain · ChromaDB · SentenceTransformers",
    accent: "signal-purple", angle: 120, deps: [2],
    warn: "Your work is invisible if the demo never reaches it. Coordinate hourly with M2 so endpoints surface your output.",
    tasks: [
      { time: "6:10 – 8:00 PM", text: "Run Chroma in Docker. Build PubMed ingestion: 5,000 abstracts → MiniLM-L6 → Chroma. Test top-k retrieval." },
      { time: "8:00 – 11:00 PM", text: "MedFact RAG chain: retrieve → Gemini reasoning → verdict + citations. Stream via SSE." },
      { time: "11:00 PM – 2:00 AM", text: "Symptom Navigator: medspaCy NER → ICD-10 lookup → Gemini conversational triage with memory." },
      { time: "2:00 – 4:00 AM", text: "Medicine Scanner: Gemini Vision pipeline + DrugBank interaction lookup + expiry parser." },
      { time: "4:00 – 7:00 AM", text: "Outbreak DBSCAN clustering + Prophet anomaly bound per district. Hand cluster IDs to M2." },
      { time: "7:00 – 9:00 AM", text: "Cache common queries in Redis. Stay under Gemini 15 req/min." },
    ],
    needs: [
      { name: "Gemini API key", how: "From aistudio.google.com." },
      { name: "NCBI API key", how: "Optional but raises ingestion to 10 req/sec." },
      { name: "Local Docker", how: "Required for ChromaDB during dev." },
    ],
  },
  {
    id: 4, code: "M4", name: "Maps & Geo", role: "Spatial layer",
    stack: "Leaflet · Overpass · OSRM · PostGIS · TimescaleDB",
    accent: "signal-teal", angle: 180, deps: [1, 2],
    warn: "The Outbreak Radar map IS the demo. If it looks empty or laggy, the project dies on stage.",
    tasks: [
      { time: "6:10 – 8:00 PM", text: "Pull Pakistan facilities from Overpass. Normalize to facilities table with lat/lng + type + open hours." },
      { time: "8:00 – 11:00 PM", text: "OSRM routing wrapper. Returns polyline + ETA. Cache routes by (origin, destination) hash." },
      { time: "11:00 PM – 2:00 AM", text: "DBSCAN cluster output → GeoJSON. Push live to /ws/outbreak via Supabase Realtime trigger." },
      { time: "2:00 – 5:00 AM", text: "District choropleth data layer: aggregate symptom_reports per district every 15 min." },
      { time: "5:00 – 9:00 AM", text: "Leaflet plugins: heatmap, marker clustering, AED iconography. Help M1 wire it all." },
    ],
    needs: [
      { name: "Pakistan admin GeoJSON", how: "data.humdata.org → district + tehsil boundaries." },
      { name: "Supabase service key", how: "Shared with M2." },
    ],
  },
  {
    id: 5, code: "M5", name: "Data Engineer", role: "Pipelines",
    stack: "Python · pandas · Celery · feedparser · pytesseract",
    accent: "alert-amber", angle: 240, deps: [2, 3],
    warn: "Bad data poisons everything. Validate before insert. If 10% of rows are garbage, the whole demo looks fake.",
    tasks: [
      { time: "6:10 – 8:00 PM", text: "Bulk insert 14k ICD-10 codes. Schema validation. Index on code prefix." },
      { time: "8:00 – 11:00 PM", text: "WHO Outbreak RSS poller (Celery). Dedupe by GUID. Insert into outbreak_alerts." },
      { time: "11:00 PM – 2:00 AM", text: "DrugBank interaction CSV importer. Build pairwise interaction lookup." },
      { time: "2:00 – 5:00 AM", text: "Mock symptom report generator: 300 realistic geo-tagged reports across 3 cities for the demo." },
      { time: "5:00 – 9:00 AM", text: "Backups, snapshot pre-demo, fixtures for fast E2E reset." },
    ],
    needs: [
      { name: "Supabase service key", how: "Shared with M2." },
      { name: "ICD-10 + DrugBank CSVs", how: "WHO + drugbank.ca open downloads." },
    ],
  },
  {
    id: 6, code: "M6", name: "DevOps & Demo", role: "Ship + present",
    stack: "Render · Vercel · GitHub Actions · Telegram · Pitch deck",
    accent: "alert-red", angle: 300, deps: [1, 2],
    warn: "The judges decide in 90 seconds. Rehearse the demo path 5+ times. Never let Render cold-start kill the opening.",
    tasks: [
      { time: "6:10 – 7:00 PM", text: "Provision Render service. Connect repo. Set env vars. First deploy of M2's /health." },
      { time: "7:00 – 10:00 PM", text: "GitHub Actions: lint + type-check on PR. Auto-deploy main → Render + Vercel." },
      { time: "10:00 PM – 2:00 AM", text: "Telegram bot wiring. Test alert end-to-end: DBSCAN cluster → Telegram message in <5 s." },
      { time: "2:00 – 5:00 AM", text: "Build the demo script. 7 features in 4 minutes. Choreograph the outbreak reveal." },
      { time: "5:00 – 8:00 AM", text: "Slide deck (5 slides max). Architecture diagram. Pre-record fallback video in case live demo dies." },
      { time: "8:00 – 9:00 AM", text: "Hit /ping on Render every 10 min. Cold start = death. Final dry-run." },
    ],
    needs: [
      { name: "Render + Vercel + GitHub", how: "All free, all sign-in-with-GitHub." },
      { name: "Telegram bot token + chat ID", how: "@BotFather and @userinfobot." },
      { name: "Quiet rehearsal corner", how: "Find one. You will need it at 8 AM." },
    ],
  },
];

// Live-telemetry strings that scroll along the bottom of the hero.
export const TELEMETRY = [
  "WHO-RSS · synced 14 s ago",
  "DBSCAN · ε=0.02° · min_samples=5",
  "Chroma · 5,142 vectors indexed",
  "Realtime · 312 subscribers",
  "Gemini · 1.2k tok/min · 4% of quota",
  "OSRM · avg routing 84 ms",
  "Render · uptime 99.96 % (last 24h)",
  "Karachi node · 03:42 local",
  "Telegram alerts · 0 false positives today",
  "PubMed ingest · last batch 4 m ago",
];

// Tiny waypoint list for the floating mini-map (top-to-bottom = scroll position).
export const WAYPOINTS = [
  { id: "hero", label: "Karachi", x: 24, y: 86 },
  { id: "features", label: "Multan", x: 38, y: 60 },
  { id: "stack", label: "Lahore", x: 60, y: 50 },
  { id: "setup", label: "Faisalabad", x: 50, y: 56 },
  { id: "env", label: "Peshawar", x: 36, y: 30 },
  { id: "team", label: "Islamabad", x: 50, y: 28 },
];
