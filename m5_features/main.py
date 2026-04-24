"""
PULSE — Member 5 Features API Server.

FastAPI application that serves the Medicine Scanner,
Emergency First Aid Guide, and Email Emergency Alert endpoints.

Run with: uvicorn m5_features.main:app --reload --port 8000
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from m5_features.config import settings
from m5_features.routes.medicine_routes import router as medicine_router
from m5_features.routes.emergency_routes import router as emergency_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production() else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PULSE — M5 Features API",
    description=(
        "AI-Powered Community Health Intelligence Network. "
        "Medicine Scanner · Emergency First Aid Guide · Email Alert. "
        "Member 5 — Features Engineer module."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware — allow Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # Next.js dev
        "http://localhost:3001",     # Alt dev port
        "https://*.vercel.app",     # Vercel deployments
        "*",                        # Allow all for hackathon
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(medicine_router)
app.include_router(emergency_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint — API info."""
    return {
        "name": "PULSE — M5 Features API",
        "version": "1.0.0",
        "author": "Zajnan Aslam — Features Engineer",
        "features": [
            "Medicine Scanner (OCR + Vision AI + OpenFDA)",
            "Emergency First Aid Guide (15 protocols + voice matching)",
            "Email Emergency Alert (GPS + Google Maps)",
        ],
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Global health check endpoint.
    
    Verifies all M5 services are operational.
    Returns status of each component.
    """
    from m5_features.ai.gemini_client import gemini_client
    from m5_features.emergency.protocol_matcher import protocol_matcher
    from m5_features.emergency.email_alert import email_alert_service

    # Check configuration
    missing_vars = settings.validate()

    return {
        "status": "healthy" if not missing_vars else "degraded",
        "environment": settings.ENVIRONMENT,
        "components": {
            "gemini_ai": {
                "configured": gemini_client.is_configured,
                "model": settings.GEMINI_MODEL_VISION,
            },
            "email_alert": {
                "configured": email_alert_service.is_configured,
            },
            "protocols": {
                "loaded": len(protocol_matcher.protocols),
                "expected": 15,
            },
            "scanner": {
                "stages": [
                    "image_preprocessing",
                    "ocr_extraction",
                    "gemini_vision",
                    "openfda_lookup",
                    "interaction_check",
                ],
            },
        },
        "missing_env_vars": missing_vars,
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """
    Wake-up endpoint for Render free tier.
    
    Hit this 30 seconds before live demo to wake up
    the Render server from its 15-min sleep cycle.
    """
    return {"pong": True}


# Startup log
@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("PULSE M5 Features API starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Gemini configured: {bool(settings.GEMINI_API_KEY)}")
    logger.info(f"Email alert configured: {bool(settings.ALERT_EMAIL)}")

    from m5_features.emergency.protocol_matcher import protocol_matcher
    logger.info(f"Protocols loaded: {len(protocol_matcher.protocols)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "m5_features.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=not settings.is_production(),
    )
