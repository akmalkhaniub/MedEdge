# MedEdge — System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│             CLINIC EDGE SERVER                  │
│  ┌──────────────────┐   ┌─────────────────────┐ │
│  │  FastAPI Backend │   │  Ollama (Offline AI) │ │
│  │  Port 8000       │◄─►│  gemma2:9b :11434   │ │
│  └────────┬─────────┘   └─────────────────────┘ │
│           │                                      │
│  ┌────────┴─────────┐                            │
│  │  Admin Panel     │                            │
│  │  React/Vite :3000│                            │
│  └──────────────────┘                            │
└───────────────────┬─────────────────────────────┘
                    │ Clinic WiFi (LAN)
         ┌──────────┴──────────┐
    ┌────▼────┐           ┌────▼────┐
    │ Mobile  │           │ Mobile  │
    │ (Nurse) │           │ (Doctor)│
    └─────────┘           └─────────┘
                    │ Internet (online mode)
         ┌──────────┼──────────┐
    ┌────▼───┐  ┌───▼────┐  ┌──▼────────────────┐
    │Gemini  │  │OpenAI  │  │ Africa's Talking   │
    │ API    │  │Whisper │  │ SMS/IVR Gateway    │
    └────────┘  └────────┘  └──────────┬─────────┘
                                        │ 2G SMS
                                   ┌────▼────────┐
                                   │Feature Phone│
                                   │  (Patient)  │
                                   └─────────────┘
```

## Data Flow — Full Consultation

```
Audio → STT (Whisper API / faster-whisper local)
     → SOAP Note (Gemini / Gemma2)
     → Triage JSON (Gemini / Gemma2)
     → Drug Interaction Check (local DB, always offline)
     → Prescription Draft (Gemini / Gemma2)
     → SMS Summary (Gemini / Gemma2) → Africa's Talking → Patient 2G phone
```

## Mode Switching

```json
// settings.json (managed by Admin Panel)
{
  "mode": "online",
  "cloud_provider": "gemini",
  "cloud_model": "gemini-2.0-flash",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "gemma2:9b"
}
```

`settings_service.get_llm_client()` returns the correct OpenAI-compatible client based on the current mode — no other code changes needed when switching.

## API Overview

```
POST /api/v1/consult          Full consultation pipeline
POST /api/v1/analyze-image    Medical image analysis
POST /api/v1/wound-tracker    Compare two wound images
POST /api/v1/vitals-ocr       Extract vitals from image
POST /api/v1/summarize-doc    Summarize medical document
POST /api/v1/compose-sms      Generate SMS message
POST /api/v1/check-drugs      Drug interaction check
GET  /api/v1/settings         Get current settings
PUT  /api/v1/settings         Update settings (admin)
GET  /api/v1/health           System health check
```
