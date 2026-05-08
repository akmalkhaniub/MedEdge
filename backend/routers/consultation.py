"""
MedEdge — Consultation Router
POST /api/v1/consult  — Full pipeline (audio upload or text)
POST /api/v1/consult/transcribe — Audio-only transcription
"""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from core.security import require_api_key
from core.logger import logger
from services.stt_service import transcribe_audio
from services.clinical_service import run_full_consultation
from database import get_session
from models import ConsultationRecord
import json
from sqlmodel import Session

router = APIRouter(prefix="/api/v1/consult", tags=["Consultation"])

LANGUAGES = [
    "English", "French", "Spanish", "Portuguese", "Swahili",
    "Arabic", "Hindi", "Hausa", "Amharic", "Yoruba", "Zulu",
    "Bengali", "Urdu", "Tagalog", "Indonesian"
]


class TextConsultRequest(BaseModel):
    transcription: str
    patient_history: Optional[str] = ""
    patient_name: Optional[str] = None
    language: Optional[str] = "English"


@router.post("/text", dependencies=[Depends(require_api_key)])
async def consult_from_text(req: TextConsultRequest, session: Session = Depends(get_session)):
    """Run full consultation pipeline from a text transcription."""
    if not req.transcription.strip():
        raise HTTPException(status_code=400, detail="Transcription text cannot be empty.")

    results = await run_full_consultation(
        transcription=req.transcription,
        patient_history=req.patient_history or "",
        language=req.language or "English",
    )

    # Persist to DB
    from services.settings_service import settings_service
    cfg = settings_service.get_settings()
    record = ConsultationRecord(
        patient_name=req.patient_name,
        transcription=results["transcription"],
        soap_note=results["soap_note"],
        triage_level=results["triage"].get("triage_level", "MEDIUM"),
        triage_json=json.dumps(results["triage"]),
        medications_detected=json.dumps(results["triage"].get("medications_mentioned", [])),
        drug_interactions=results.get("drug_interactions", ""),
        prescription_draft=results.get("prescription_draft", ""),
        sms_summary=results.get("sms_summary", ""),
        language=req.language or "English",
        operation_mode_used=cfg.operation_mode,
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return {"id": record.id, **results}


@router.post("/audio", dependencies=[Depends(require_api_key)])
async def consult_from_audio(
    audio: UploadFile = File(...),
    patient_history: str = Form(default=""),
    patient_name: str = Form(default=""),
    language: str = Form(default="English"),
    session: Session = Depends(get_session),
):
    """Upload an audio file → transcribe → run full consultation pipeline."""
    # Save temp file
    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        transcription = transcribe_audio(tmp_path)
        if transcription.startswith("[STT Error") or transcription.startswith("[Transcription"):
            raise HTTPException(status_code=422, detail=transcription)

        results = await run_full_consultation(
            transcription=transcription,
            patient_history=patient_history,
            language=language,
        )

        from services.settings_service import settings_service
        cfg = settings_service.get_settings()
        record = ConsultationRecord(
            patient_name=patient_name or None,
            transcription=results["transcription"],
            soap_note=results["soap_note"],
            triage_level=results["triage"].get("triage_level", "MEDIUM"),
            triage_json=json.dumps(results["triage"]),
            medications_detected=json.dumps(results["triage"].get("medications_mentioned", [])),
            drug_interactions=results.get("drug_interactions", ""),
            prescription_draft=results.get("prescription_draft", ""),
            sms_summary=results.get("sms_summary", ""),
            language=language,
            operation_mode_used=cfg.operation_mode,
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        return {"id": record.id, **results}

    finally:
        os.unlink(tmp_path)


@router.get("/history", dependencies=[Depends(require_api_key)])
def get_consultation_history(limit: int = 20, session: Session = Depends(get_session)):
    """Retrieve recent consultation records."""
    from sqlmodel import select
    records = session.exec(
        select(ConsultationRecord).order_by(ConsultationRecord.created_at.desc()).limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "patient_name": r.patient_name,
            "triage_level": r.triage_level,
            "primary_diagnosis": json.loads(r.triage_json).get("primary_diagnosis", ""),
            "language": r.language,
            "sms_sent": r.sms_sent,
            "operation_mode_used": r.operation_mode_used,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@router.get("/{record_id}", dependencies=[Depends(require_api_key)])
def get_consultation_detail(record_id: int, session: Session = Depends(get_session)):
    record = session.get(ConsultationRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Consultation not found.")
    return {
        "id": record.id,
        "patient_name": record.patient_name,
        "transcription": record.transcription,
        "soap_note": record.soap_note,
        "triage": json.loads(record.triage_json),
        "medications_detected": json.loads(record.medications_detected),
        "drug_interactions": record.drug_interactions,
        "prescription_draft": record.prescription_draft,
        "sms_summary": record.sms_summary,
        "sms_sent": record.sms_sent,
        "language": record.language,
        "operation_mode_used": record.operation_mode_used,
        "created_at": record.created_at.isoformat(),
    }
