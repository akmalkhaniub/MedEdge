"""
MedEdge Backend — Core Configuration
Loads all settings from .env using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
import os


class Settings(BaseSettings):
    # ── AI Providers ─────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    groq_api_key: str = ""
    openrouter_api_key: str = ""
    openai_api_key: str = ""

    # ── Offline / Ollama ─────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:9b"
    ollama_vision_model: str = "llava:7b"

    # ── Operational Mode ─────────────────────────────────────────────────────
    operation_mode: Literal["online", "offline"] = "online"
    cloud_provider: Literal["gemini", "groq", "openrouter"] = "gemini"
    cloud_model: str = "gemini-2.0-flash"

    # ── MedGemma ─────────────────────────────────────────────────────────────
    medgemma_model: str = "google/medgemma-4b-it"
    medgemma_provider: Literal["openrouter", "google_ai_studio"] = "openrouter"

    # ── STT ──────────────────────────────────────────────────────────────────
    stt_mode: Literal["auto", "openai", "local"] = "auto"
    whisper_local_model: str = "base"

    # ── SMS ──────────────────────────────────────────────────────────────────
    sms_gateway: Literal["africas_talking", "twilio", "disabled"] = "disabled"
    at_username: str = "sandbox"
    at_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # ── Security ─────────────────────────────────────────────────────────────
    api_key: str = "mededge-dev-key-2026"
    admin_api_key: str = "mededge-admin-2026"

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./mededge.db"

    # ── Observability ────────────────────────────────────────────────────────
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # ── Dev Flags ────────────────────────────────────────────────────────────
    use_mock_ai: bool = False
    debug: bool = True

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton
settings = Settings()
