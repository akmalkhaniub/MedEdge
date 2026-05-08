"""
MedEdge — Settings Router (Admin-only)
GET  /api/v1/settings  — Retrieve current settings
PUT  /api/v1/settings  — Update settings (requires admin key)
"""
from fastapi import APIRouter, Depends
from core.security import require_api_key, require_admin_key
from services.settings_service import settings_service, AppSettings

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.get("", dependencies=[Depends(require_api_key)])
def get_settings():
    """Get current operational settings."""
    return settings_service.get_settings()


@router.put("", dependencies=[Depends(require_admin_key)])
def update_settings(new_settings: AppSettings):
    """Update settings (Admin API key required). Changes take effect immediately."""
    updated = settings_service.save_settings(new_settings)
    return {"status": "updated", "settings": updated}
