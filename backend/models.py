"""
MedEdge — SQLModel Database Models
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import json


# ── Settings (singleton row, id=1) ───────────────────────────────────────────
class GlobalSettings(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)

    # Mode control
    operation_mode: str = "online"           # "online" | "offline"
    cloud_provider: str = "gemini"           # "gemini" | "groq" | "openrouter"
    cloud_model: str = "gemini-2.0-flash"
    ollama_model: str = "gemma2:9b"
    ollama_vision_model: str = "llava:7b"

    # MedGemma
    use_medgemma: bool = True
    medgemma_model: str = "google/medgemma-4b-it"
    medgemma_provider: str = "openrouter"

    # STT
    stt_mode: str = "auto"                   # "auto" | "openai" | "local"
    whisper_local_model: str = "base"

    # SMS
    sms_gateway: str = "disabled"            # "africas_talking" | "twilio" | "disabled"
    sms_enabled: bool = False

    # Languages
    default_language: str = "English"

    # Feature flags
    use_mock_ai: bool = False
    drug_check_enabled: bool = True
    prescription_draft_enabled: bool = True
    wound_tracker_enabled: bool = True


# ── Consultation History ──────────────────────────────────────────────────────
class ConsultationRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_name: Optional[str] = None
    patient_id_ref: Optional[str] = None      # External reference (optional)
    transcription: str = ""
    soap_note: str = ""
    triage_level: str = "MEDIUM"              # LOW | MEDIUM | HIGH | CRITICAL
    triage_json: str = "{}"                   # Full triage JSON as string
    medications_detected: str = "[]"          # JSON array of medication names
    drug_interactions: str = ""
    prescription_draft: str = ""
    sms_summary: str = ""
    sms_sent: bool = False
    language: str = "English"
    ai_provider_used: str = ""
    operation_mode_used: str = "online"       # Track which mode was active
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── Image Analysis History ────────────────────────────────────────────────────
class ImageAnalysisRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_type: str = "general"            # general | wound | vitals | document
    patient_ref: Optional[str] = None
    clinical_context: str = ""
    analysis_result: str = ""
    ai_provider_used: str = ""
    operation_mode_used: str = "online"
    created_at: datetime = Field(default_factory=datetime.utcnow)
