"""
AI-Powered Preventive Oral Health Screening & Monitoring System
FastAPI Backend Application
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routes.health import router as health_router
from app.routes.analyze import router as analyze_router
from app.routes.quality import router as quality_router
from app.routes.enhancement import router as enhancement_router
from app.routes.screenings import router as screenings_router
from app.services.db import init_db

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and demo baseline
    try:
        init_db()
        logger.info("SQLite database initialized.")
    except Exception as db_err:
        logger.error("Database initialization failed: %s", db_err)

    mock_mode = os.getenv("MOCK_AI", "true").lower() in ("true", "1", "yes")
    logger.info("Initializing Dental Screening Backend (MOCK_AI=%s)", mock_mode)
    if mock_mode:
        logger.info("MOCK_AI is ENABLED: Gemini API calls are mocked with deterministic findings.")
    else:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set while MOCK_AI=false! Real analyses will fail until configured.")
        else:
            logger.info("GEMINI_API_KEY is configured for real AI analysis.")
    yield
    logger.info("Shutting down Dental Screening Backend.")


app = FastAPI(
    title="Dental Screening API",
    description=(
        "## AI-Powered Preventive Oral Health Screening\n\n"
        "This API performs a **preliminary visual screening** of dental photographs. "
        "It is **NOT** a diagnostic tool and does **NOT** replace professional dental examination.\n\n"
        "All findings use cautious, non-diagnostic language.\n\n"
        "**Disclaimer:** Results must be reviewed by a qualified dental professional."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────────────────
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
)
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(quality_router)
app.include_router(enhancement_router)
app.include_router(analyze_router)
app.include_router(screenings_router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "AI Preventive Oral Health Screening API",
        "docs": "/docs",
        "health": "/health"
    }
