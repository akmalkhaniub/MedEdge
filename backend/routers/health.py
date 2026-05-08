"""
MedEdge — Health Router
GET /api/v1/health  — Full system health check
Returns status of backend, AI providers, Ollama, and SMS gateway.
"""
import asyncio
import httpx
from fastapi import APIRouter
from core.config import settings as env_settings
from core.logger import logger

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


async def _check_ollama() -> dict:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{env_settings.ollama_base_url}/api/tags")
            if r.status_code == 200:
                models = [m["name"] for m in r.json().get("models", [])]
                return {"status": "online", "models": models}
    except Exception as e:
        pass
    return {"status": "offline", "models": []}


async def _check_gemini() -> dict:
    if not env_settings.gemini_api_key:
        return {"status": "no_key"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={env_settings.gemini_api_key}"
            )
            return {"status": "online" if r.status_code == 200 else "error", "http_status": r.status_code}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("")
async def health_check():
    """Full system health check — no auth required."""
    from services.settings_service import settings_service
    cfg = settings_service.get_settings()

    # Run checks in parallel
    ollama_status, gemini_status = await asyncio.gather(
        _check_ollama(),
        _check_gemini(),
    )

    return {
        "status": "healthy",
        "operation_mode": cfg.operation_mode,
        "cloud_provider": cfg.cloud_provider,
        "cloud_model": cfg.cloud_model,
        "providers": {
            "ollama": ollama_status,
            "gemini": gemini_status,
            "groq": {"status": "configured" if env_settings.groq_api_key else "no_key"},
            "openrouter": {"status": "configured" if env_settings.openrouter_api_key else "no_key"},
        },
        "features": {
            "use_medgemma": cfg.use_medgemma,
            "medgemma_model": cfg.medgemma_model,
            "stt_mode": cfg.stt_mode,
            "sms_gateway": cfg.sms_gateway,
            "drug_check": cfg.drug_check_enabled,
        },
    }
