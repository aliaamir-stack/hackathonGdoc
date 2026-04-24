import asyncio
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Set

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from auth import router as auth_router
from config import get_settings
from database import get_anon_client, get_redis, get_service_client, run_supabase
from routes.dashboard import router as dashboard_router
from routes.emergency import router as emergency_router
from routes.facilities import router as facilities_router
from routes.medFact import router as medfact_router
from routes.medicine import router as medicine_router
from routes.outbreak import router as outbreak_router
from routes.symptoms import router as symptoms_router
from limiter import limiter

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pulse")
app = FastAPI(title="PULSE API", version="1.0.0")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

origins = ["*"]
if settings.VERCEL_FRONTEND_URL:
    origins.append(settings.VERCEL_FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(medfact_router, prefix="/api")
app.include_router(symptoms_router, prefix="/api")
app.include_router(medicine_router, prefix="/api")
app.include_router(facilities_router, prefix="/api")
app.include_router(outbreak_router, prefix="/api")
app.include_router(emergency_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "PULSE API"}


@app.get("/ping")
async def ping():
    return {"pong": True}


@app.exception_handler(404)
async def not_found_handler(request: Request, _exc):
    return JSONResponse(status_code=404, content={"error": "Not found", "path": str(request.url.path)})


@app.exception_handler(RequestValidationError)
async def validation_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "Validation error", "details": exc.errors()})


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "retry_after": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def generic_handler(_request: Request, exc: Exception):
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": "Unexpected error"})


@app.on_event("startup")
async def startup():
    service = get_service_client()
    await run_supabase(service.table("symptom_reports").select("id").limit(1).execute)
    redis = await get_redis()
    await redis.ping()
    logger.info("PULSE backend ready %s", datetime.now(timezone.utc).isoformat())


@app.get("/api/stream/gemini")
@limiter.limit("10/minute")
async def stream_gemini(request: Request, prompt: str):
    async def event_generator():
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            stream = model.generate_content(prompt, stream=True)
            for chunk in stream:
                text = getattr(chunk, "text", "") or ""
                payload = json.dumps({"chunk": text, "done": False})
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0)
            yield 'data: {"chunk": "", "done": true}\n\n'
        except Exception:
            yield 'data: {"chunk": "", "done": true}\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class WSManager:
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self._task = None

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.add(ws)

    def disconnect(self, ws: WebSocket):
        self.clients.discard(ws)

    async def broadcast(self, payload: dict):
        dead = []
        for ws in self.clients:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_initial(self, ws: WebSocket):
        client = get_anon_client()
        result = await run_supabase(
            client.table("outbreak_alerts").select("*").order("created_at", desc=True).limit(10).execute
        )
        await ws.send_json({"type": "initial", "data": result.data or []})

    async def poll_and_broadcast(self):
        last_report = None
        last_alert = None
        client = get_anon_client()
        while True:
            try:
                report_res = await run_supabase(
                    client.table("symptom_reports")
                    .select("id,latitude,longitude,symptoms,urgency_level,district")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute
                )
                alert_res = await run_supabase(
                    client.table("outbreak_alerts")
                    .select("id,title,severity,district,description")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute
                )
                if report_res.data:
                    rpt = report_res.data[0]
                    if rpt["id"] != last_report:
                        last_report = rpt["id"]
                        await self.broadcast(
                            {
                                "type": "new_report",
                                "data": {
                                    "lat": rpt["latitude"],
                                    "lng": rpt["longitude"],
                                    "symptoms": rpt["symptoms"],
                                    "urgency": rpt["urgency_level"],
                                    "district": rpt["district"],
                                },
                            }
                        )
                if alert_res.data:
                    alert = alert_res.data[0]
                    if alert["id"] != last_alert:
                        last_alert = alert["id"]
                        await self.broadcast(
                            {
                                "type": "alert",
                                "data": {
                                    "title": alert["title"],
                                    "severity": alert["severity"],
                                    "district": alert["district"],
                                    "description": alert["description"],
                                },
                            }
                        )
            except Exception as exc:
                logger.warning("WebSocket poll loop error: %s", exc)
            await asyncio.sleep(3)


ws_manager = WSManager()


@app.websocket("/ws/outbreak")
async def ws_outbreak(websocket: WebSocket):
    await ws_manager.connect(websocket)
    await ws_manager.send_initial(websocket)
    if ws_manager._task is None:
        ws_manager._task = asyncio.create_task(ws_manager.poll_and_broadcast())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


