"""
MedEdge — API Key Security Middleware
Requires X-API-Key header on all /api/v1/* routes.
Admin routes require the elevated admin key.
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key and api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Pass X-API-Key header.",
        )
    return api_key


async def require_admin_key(api_key: str = Security(api_key_header)):
    if api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin API key required.",
        )
    return api_key
