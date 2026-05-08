"""
MedEdge — AI Service
The core orchestration engine. Supports:
  - Gemini 2.0 Flash (online, cloud)
  - MedGemma 4B (medical specialist, via OpenRouter)
  - Groq / Llama (online, ultra-fast)
  - Gemma2 9B via Ollama (offline, local)
  - LLaVA via Ollama (offline vision)

Provider resolution is always driven by settings_service,
which the Admin Panel controls at runtime.
"""
import asyncio
import base64
import json
import os
from typing import Any, Dict, Optional

from core.config import settings as env_settings
from core.logger import logger

# ── Conditional Provider Imports ──────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    genai_types = None
    _GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    _OPENAI_AVAILABLE = False

try:
    from groq import Groq
    _GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    _GROQ_AVAILABLE = False


# ── Lazy import to avoid circular dependency ──────────────────────────────────
def _get_settings():
    from services.settings_service import settings_service
    return settings_service.get_settings()


class AIService:
    """
    Unified AI provider with runtime mode-switching.
    All methods check settings_service on each call so that
    the Admin Panel's mode toggle takes effect immediately
    without restarting the server.
    """

    # ── Client Factory ────────────────────────────────────────────────────────
    def _get_openai_compat_client(self, cfg) -> Optional[Any]:
        """Return an OpenAI-compatible client for the current mode."""
        if not _OPENAI_AVAILABLE:
            return None

        if cfg.operation_mode == "offline":
            return OpenAI(
                base_url=f"{env_settings.ollama_base_url}/v1",
                api_key="ollama",
            )

        if cfg.cloud_provider == "gemini":
            # Gemini via OpenAI-compat endpoint (for simple text)
            return OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=env_settings.gemini_api_key,
            )
        elif cfg.cloud_provider == "groq" and _GROQ_AVAILABLE:
            return Groq(api_key=env_settings.groq_api_key)
        elif cfg.cloud_provider == "openrouter":
            return OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=env_settings.openrouter_api_key,
            )
        return None

    def _get_model_name(self, cfg) -> str:
        """Return the correct model string for the current mode."""
        if cfg.operation_mode == "offline":
            return cfg.ollama_model
        return cfg.cloud_model

    def _get_vision_model(self, cfg) -> str:
        """Return the correct vision model for the current mode."""
        if cfg.operation_mode == "offline":
            return cfg.ollama_vision_model
        # Online: Gemini Flash is multimodal natively
        return cfg.cloud_model

    # ── MedGemma Client ───────────────────────────────────────────────────────
    def _get_medgemma_client(self, cfg):
        """MedGemma via OpenRouter (specialized clinical reasoning)."""
        if not _OPENAI_AVAILABLE or not cfg.use_medgemma:
            return None, None
        if cfg.operation_mode == "offline":
            return None, None  # MedGemma not available offline

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=env_settings.openrouter_api_key,
        )
        return client, cfg.medgemma_model

    # ── Native Gemini Client (for vision + complex tasks) ─────────────────────
    def _get_gemini_native(self, cfg):
        if not _GEMINI_AVAILABLE or not env_settings.gemini_api_key:
            return None
        if cfg.operation_mode == "offline":
            return None
        return genai.Client(api_key=env_settings.gemini_api_key)

    # ── Core Text Completion ──────────────────────────────────────────────────
    async def complete(self, prompt: str, system: str = "", temperature: float = 0.2) -> str:
        """Generic text completion — uses current mode provider."""
        cfg = _get_settings()

        if cfg.use_mock_ai:
            return f"[MOCK AI RESPONSE — prompt: {prompt[:60]}...]"

        client = self._get_openai_compat_client(cfg)
        model = self._get_model_name(cfg)

        if not client:
            raise RuntimeError("No AI client available. Check API keys and settings.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=temperature,
            )
            result = response.choices[0].message.content
            logger.info("ai_completion", provider=cfg.cloud_provider, mode=cfg.operation_mode, model=model)
            return result
        except Exception as e:
            logger.error("ai_completion_failed", error=str(e), model=model)
            raise

    # ── MedGemma Completion (for clinical reasoning) ──────────────────────────
    async def medgemma_complete(self, prompt: str, system: str = "") -> str:
        """
        Use MedGemma for specialist clinical reasoning.
        Falls back to primary model if MedGemma unavailable or offline.
        """
        cfg = _get_settings()
        client, model = self._get_medgemma_client(cfg)

        if not client:
            logger.info("medgemma_fallback", reason="unavailable or offline mode")
            return await self.complete(prompt, system)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=messages,
                temperature=0.1,
            )
            result = response.choices[0].message.content
            logger.info("medgemma_completion", model=model)
            return result
        except Exception as e:
            logger.error("medgemma_failed", error=str(e))
            return await self.complete(prompt, system)

    # ── Vision Completion ─────────────────────────────────────────────────────
    async def vision_complete(self, image_path: str, prompt: str, context: str = "") -> str:
        """Analyze an image with context. Uses Gemini native SDK or Ollama/LLaVA."""
        cfg = _get_settings()

        with open(image_path, "rb") as f:
            image_bytes = f.read()
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        ext = os.path.splitext(image_path)[1].lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

        full_prompt = f"{prompt}\n\nClinical context: {context}" if context else prompt

        # Online: prefer native Gemini SDK for best vision quality
        if cfg.operation_mode == "online":
            gemini = self._get_gemini_native(cfg)
            if gemini and _GEMINI_AVAILABLE:
                try:
                    response = await asyncio.to_thread(
                        gemini.models.generate_content,
                        model=cfg.cloud_model,
                        contents=[
                            full_prompt,
                            genai_types.Part.from_bytes(data=image_bytes, mime_type=mime)
                        ]
                    )
                    logger.info("vision_complete", provider="gemini_native")
                    return response.text
                except Exception as e:
                    logger.error("gemini_vision_failed", error=str(e))

        # Fallback: OpenAI-compat vision (works for Ollama/LLaVA + OpenRouter)
        client = self._get_openai_compat_client(cfg)
        vision_model = self._get_vision_model(cfg)

        if not client:
            raise RuntimeError("No vision client available.")

        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=vision_model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                    ]
                }],
                temperature=0.2,
            )
            logger.info("vision_complete", provider="openai_compat", model=vision_model)
            return response.choices[0].message.content
        except Exception as e:
            logger.error("vision_complete_failed", error=str(e))
            raise

    # ── JSON Extraction Helper ────────────────────────────────────────────────
    async def complete_json(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """Complete and parse JSON from the response."""
        raw = await self.complete(prompt, system, temperature=0.1)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end])
            except json.JSONDecodeError:
                pass
        # Last resort: return raw in a wrapper
        return {"raw": raw}


# Singleton
ai_service = AIService()
