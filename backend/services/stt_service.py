"""
MedEdge — STT Service
Speech-to-Text with dual-mode support:
  - Online: OpenAI Whisper API (whisper-1)
  - Offline: faster-whisper (local CPU, no internet)
"""
import os
from core.config import settings as env_settings
from core.logger import logger


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe an audio file.
    Mode is determined by STT_MODE env var and current operation mode.
    """
    from services.settings_service import settings_service
    cfg = settings_service.get_settings()

    use_local = (
        cfg.stt_mode == "local"
        or cfg.operation_mode == "offline"
        or (cfg.stt_mode == "auto" and cfg.operation_mode == "offline")
    )

    if use_local:
        return _transcribe_local(audio_path, cfg.whisper_local_model)
    else:
        return _transcribe_openai(audio_path)


def _transcribe_openai(audio_path: str) -> str:
    """Use OpenAI Whisper API for transcription."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=env_settings.openai_api_key or env_settings.gemini_api_key)
        with open(audio_path, "rb") as f:
            result = client.audio.transcriptions.create(model="whisper-1", file=f)
        logger.info("stt_complete", provider="openai_whisper")
        return result.text
    except Exception as e:
        logger.error("stt_openai_failed", error=str(e))
        # Fallback to local
        return _transcribe_local(audio_path, "base")


def _transcribe_local(audio_path: str, model_size: str = "base") -> str:
    """Use faster-whisper for fully local, offline transcription."""
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(audio_path, beam_size=5)
        text = " ".join([seg.text.strip() for seg in segments])
        logger.info("stt_complete", provider="faster_whisper", model=model_size, language=info.language)
        return text
    except ImportError:
        logger.error("faster_whisper_not_installed")
        return "[STT Error: faster-whisper not installed. Run: pip install faster-whisper]"
    except Exception as e:
        logger.error("stt_local_failed", error=str(e))
        return f"[STT Error: {str(e)}]"
