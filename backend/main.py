"""
MedEdge — FastAPI Application
Hybrid clinical assistant backend.
Supports Online (Gemini/MedGemma/Groq) and Offline (Ollama/Gemma2) modes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables
from core.logger import logger
from routers import consultation, imaging, drugs, settings, health

app = FastAPI(
    title="MedEdge API",
    description="AI-Powered Hybrid Clinical Assistant — Online & Offline modes with MedGemma",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow admin panel + mobile app on LAN) ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict in production to known origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(consultation.router)
app.include_router(imaging.router)
app.include_router(drugs.router)
app.include_router(settings.router)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("mededge_startup", version="1.0.0", message="MedEdge backend is running.")


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "service": "MedEdge API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
