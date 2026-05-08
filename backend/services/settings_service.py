"""
MedEdge — Settings Service
Single source of truth for operational mode and AI configuration.
Reads/writes to SQLite DB (GlobalSettings singleton row).
"""
import json
from sqlmodel import Session
from database import engine
from models import GlobalSettings
from core.config import settings as env_settings
from core.logger import logger
from pydantic import BaseModel
from typing import Literal, Optional


class AppSettings(BaseModel):
    """Runtime settings managed via Admin Panel."""
    operation_mode: Literal["online", "offline"] = "online"
    cloud_provider: Literal["gemini", "groq", "openrouter"] = "gemini"
    cloud_model: str = "gemini-2.0-flash"
    ollama_model: str = "gemma2:9b"
    ollama_vision_model: str = "llava:7b"

    use_medgemma: bool = True
    medgemma_model: str = "google/medgemma-4b-it"
    medgemma_provider: Literal["openrouter", "google_ai_studio"] = "openrouter"

    stt_mode: Literal["auto", "openai", "local"] = "auto"
    whisper_local_model: str = "base"

    sms_gateway: Literal["africas_talking", "twilio", "disabled"] = "disabled"
    sms_enabled: bool = False

    default_language: str = "English"
    use_mock_ai: bool = False
    drug_check_enabled: bool = True
    prescription_draft_enabled: bool = True
    wound_tracker_enabled: bool = True


def _row_to_settings(row: GlobalSettings) -> AppSettings:
    return AppSettings(
        operation_mode=row.operation_mode,
        cloud_provider=row.cloud_provider,
        cloud_model=row.cloud_model,
        ollama_model=row.ollama_model,
        ollama_vision_model=row.ollama_vision_model,
        use_medgemma=row.use_medgemma,
        medgemma_model=row.medgemma_model,
        medgemma_provider=row.medgemma_provider,
        stt_mode=row.stt_mode,
        whisper_local_model=row.whisper_local_model,
        sms_gateway=row.sms_gateway,
        sms_enabled=row.sms_enabled,
        default_language=row.default_language,
        use_mock_ai=row.use_mock_ai,
        drug_check_enabled=row.drug_check_enabled,
        prescription_draft_enabled=row.prescription_draft_enabled,
        wound_tracker_enabled=row.wound_tracker_enabled,
    )


class SettingsService:
    def get_settings(self) -> AppSettings:
        with Session(engine) as session:
            row = session.get(GlobalSettings, 1)
            if not row:
                # Bootstrap defaults from .env
                row = GlobalSettings(
                    operation_mode=env_settings.operation_mode,
                    cloud_provider=env_settings.cloud_provider,
                    cloud_model=env_settings.cloud_model,
                    ollama_model=env_settings.ollama_model,
                    ollama_vision_model=env_settings.ollama_vision_model,
                    medgemma_model=env_settings.medgemma_model,
                    medgemma_provider=env_settings.medgemma_provider,
                    stt_mode=env_settings.stt_mode,
                    whisper_local_model=env_settings.whisper_local_model,
                    sms_gateway=env_settings.sms_gateway,
                )
                session.add(row)
                session.commit()
                session.refresh(row)
            return _row_to_settings(row)

    def save_settings(self, new_settings: AppSettings) -> AppSettings:
        with Session(engine) as session:
            row = session.get(GlobalSettings, 1)
            if not row:
                row = GlobalSettings()
                session.add(row)

            row.operation_mode = new_settings.operation_mode
            row.cloud_provider = new_settings.cloud_provider
            row.cloud_model = new_settings.cloud_model
            row.ollama_model = new_settings.ollama_model
            row.ollama_vision_model = new_settings.ollama_vision_model
            row.use_medgemma = new_settings.use_medgemma
            row.medgemma_model = new_settings.medgemma_model
            row.medgemma_provider = new_settings.medgemma_provider
            row.stt_mode = new_settings.stt_mode
            row.whisper_local_model = new_settings.whisper_local_model
            row.sms_gateway = new_settings.sms_gateway
            row.sms_enabled = new_settings.sms_enabled
            row.default_language = new_settings.default_language
            row.use_mock_ai = new_settings.use_mock_ai
            row.drug_check_enabled = new_settings.drug_check_enabled
            row.prescription_draft_enabled = new_settings.prescription_draft_enabled
            row.wound_tracker_enabled = new_settings.wound_tracker_enabled

            session.commit()

        logger.info("settings_updated", mode=new_settings.operation_mode, provider=new_settings.cloud_provider)
        return new_settings


# Singleton
settings_service = SettingsService()
