# MedEdge — Detailed Implementation Plan
**Version:** 1.0  
**Date:** May 2026  
**Status:** 🟡 In Planning

---

## 1. Project Overview

MedEdge is a cross-platform, hybrid-mode clinical assistant evolved from the MediVoice v2 hackathon prototype. It transforms the Gradio-based proof-of-concept into a production-architecture system with:

- A **FastAPI backend** serving as the AI brain
- A **React/Vite Admin Panel** for clinic operators
- A **React Native (Expo) mobile app** for clinic staff
- **Dual AI mode** — cloud (online) or local Ollama (offline)

---

## 2. Repository Structure

```
MedEdge/
├── backend/                    # FastAPI REST API
│   ├── main.py                 # App factory + router registration
│   ├── routers/
│   │   ├── consultation.py     # /consult endpoints
│   │   ├── imaging.py          # /analyze-image, /wound-tracker, /vitals-ocr
│   │   ├── documents.py        # /summarize-document
│   │   ├── sms.py              # /compose-sms, /send-sms
│   │   ├── drugs.py            # /check-interactions
│   │   └── settings.py         # /settings (admin CRUD)
│   ├── services/
│   │   ├── ai_service.py       # LLM orchestration (online/offline switching)
│   │   ├── stt_service.py      # Speech-to-text (Whisper API or local Whisper.cpp)
│   │   ├── sms_service.py      # Africa's Talking / Twilio gateway
│   │   ├── drug_service.py     # Offline drug interaction DB
│   │   └── settings_service.py # Mode & config management
│   ├── models/
│   │   ├── consultation.py     # Pydantic schemas
│   │   ├── settings.py
│   │   └── triage.py
│   ├── core/
│   │   ├── config.py           # Pydantic Settings from .env
│   │   ├── database.py         # SQLite (dev) / PostgreSQL (prod)
│   │   └── security.py         # API key auth middleware
│   ├── data/
│   │   └── drug_interactions.json  # Local offline drug DB
│   ├── requirements.txt
│   └── .env.example
│
├── admin/                      # React/Vite Admin Panel
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx   # System health overview
│   │   │   ├── ModeControl.tsx # Online/Offline toggle
│   │   │   ├── Providers.tsx   # API key config
│   │   │   └── Logs.tsx        # Recent consultation logs
│   │   ├── components/
│   │   │   ├── StatusBadge.tsx
│   │   │   ├── ModeToggle.tsx
│   │   │   └── ConnectivityHUD.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── mobile/                     # React Native (Expo)
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── consultation.tsx
│   │   │   ├── imaging.tsx
│   │   │   ├── sms.tsx
│   │   │   └── drugs.tsx
│   │   └── _layout.tsx
│   ├── components/
│   │   ├── AudioRecorder.tsx
│   │   ├── TriageBadge.tsx
│   │   ├── SOAPNoteViewer.tsx
│   │   └── CameraCapture.tsx
│   ├── services/
│   │   └── api.ts              # Axios client pointing to backend
│   ├── app.json
│   └── package.json
│
├── docs/
│   ├── implementation_plan.md  # This file
│   ├── api_reference.md        # REST API documentation
│   ├── architecture.md         # System architecture diagrams
│   └── deployment_guide.md     # How to deploy on clinic hardware
│
└── scripts/
    ├── setup.sh                # One-shot dev environment setup
    └── seed_drugs.py           # Populate drug interaction DB
```

---

## 3. Phase Breakdown

### Phase 1 — Backend Foundation ✅ [PRIORITY: START HERE]

**Goal:** Replace the Gradio monolith with a proper FastAPI REST API. The existing `ai_core.py` logic is mostly good — we refactor its delivery layer, not the logic itself.

#### Tasks:
- [ ] Initialize FastAPI project in `/backend`
- [ ] Move all logic from `ai_core.py` into `services/ai_service.py`
- [ ] Create Pydantic models for all request/response shapes
- [ ] Implement `settings_service.py`:
  - Reads/writes `settings.json` (persisted config)
  - Exposes `get_llm_client()` which returns OpenAI or Ollama client based on current mode
- [ ] Wire up all routers (consultation, imaging, drugs, sms, settings)
- [ ] Add API key authentication middleware
- [ ] Add `/health` endpoint for connectivity checks
- [ ] Fix audio transcription — implement `stt_service.py`:
  - **Online mode**: OpenAI Whisper API (`whisper-1`)
  - **Offline mode**: `faster-whisper` Python library (runs locally, no Ollama needed)
- [ ] Create `.env.example` with all required keys documented

#### API Endpoints (v1):
```
POST /api/v1/consult          — Full consultation pipeline
POST /api/v1/analyze-image    — Single medical image analysis
POST /api/v1/wound-tracker    — Compare two wound images
POST /api/v1/vitals-ocr       — Extract vitals from image
POST /api/v1/summarize-doc    — Summarize medical document
POST /api/v1/compose-sms      — Generate SMS message
POST /api/v1/check-drugs      — Drug interaction check
GET  /api/v1/settings         — Get current settings
PUT  /api/v1/settings         — Update settings (admin only)
GET  /api/v1/health           — System health check
```

#### Key Design Decisions:
- **Mode Switching**: A single `settings.json` flag (`"mode": "online" | "offline"`) controls which provider is used. The `settings_service.py` is the single source of truth.
- **Database**: SQLite via SQLModel for dev. Schema is designed to be PostgreSQL-compatible for future migration.
- **Auth**: Simple API Key in `X-API-Key` header. Key stored in `.env`. Admin panel uses the same key.

---

### Phase 2 — Settings Service & Mode Engine

**Goal:** Implement the core mode-switching logic that everything else depends on.

#### The Mode Engine:

```python
# settings_service.py (pseudocode)

class OperationalMode(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class AppSettings(BaseModel):
    mode: OperationalMode = OperationalMode.ONLINE
    # Online providers
    openai_api_key: str = ""
    gemini_api_key: str = ""
    preferred_cloud_provider: str = "gemini"   # "openai" | "gemini"
    cloud_model: str = "gemini-2.0-flash"
    # Offline providers
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma2:9b"
    # STT
    stt_mode: str = "auto"  # "auto" | "openai" | "local"
    # SMS Gateway
    sms_gateway: str = "africas_talking"  # "africas_talking" | "twilio"
    africas_talking_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

def get_llm_client(settings: AppSettings) -> OpenAI:
    if settings.mode == OperationalMode.OFFLINE:
        return OpenAI(base_url=settings.ollama_base_url + "/v1", api_key="ollama")
    # Online: return appropriate cloud client
    ...
```

---

### Phase 3 — Admin Control Panel (React/Vite)

**Goal:** A premium, medical-themed web dashboard for clinic operators.

#### Screens:

**1. Dashboard (Home)**
- System status cards: Backend ✅ | LLM Provider ✅ | SMS Gateway ✅ | Ollama 🟡
- Today's consultation count
- Current mode badge (ONLINE 🌐 / OFFLINE 📡)

**2. Mode Control**
- Large, prominent toggle: `[🌐 ONLINE]` ↔ `[📡 OFFLINE]`
- Current provider displayed below toggle
- "Test Connection" button that hits `/health` and shows latency

**3. Provider Configuration**
- Online: Input fields for Gemini API Key, OpenAI API Key, preferred model dropdown
- Offline: Ollama URL field, model selector (auto-populated from `ollama list`)
- SMS: Africa's Talking / Twilio credentials

**4. Consultation Logs**
- Table of recent consultations with triage level, timestamp, SMS sent status
- Expandable row to view SOAP note

#### Design System:
- Color palette: Deep navy (`#0A1628`) + Electric teal (`#00BCD4`) + Alert amber/red
- Font: Inter (clinical, clean)
- Glassmorphism cards for status panels
- Framer Motion for mode toggle animation

---

### Phase 4 — React Native Mobile App (Expo)

**Goal:** A mobile-first interface for clinic staff — connecting to the backend over clinic LAN WiFi.

#### Screens:

**1. Consultation HUD**
- Large pulsing record button
- Real-time waveform animation while recording
- After processing: SOAP note displayed in card format
- Triage badge prominently displayed
- "Send SMS to Patient" button

**2. Clinical Vision**
- Camera tab with mode selectors: Wound | Rash | X-Ray | Vitals Chart | Document
- Tap to capture → instant AI analysis
- Wound Tracker: capture "before" and "after" sequentially

**3. Drug Checker**
- Typeahead search for medication names
- Real-time interaction alerts as you add drugs
- Works fully offline (no API call needed)

**4. Settings (Clinic Config)**
- "Clinic Server IP" input (for local WiFi connection)
- Current mode display (pulled from backend)
- App version info

#### Mobile Architecture:
- **API Client**: Axios with configurable base URL (set to clinic server IP on LAN)
- **State Management**: Zustand for app-wide state (current mode, server config)
- **Offline Caching**: AsyncStorage to queue failed requests when WiFi drops
- **Audio**: `expo-av` for recording
- **Camera**: `expo-camera` for image capture

---

### Phase 5 — Offline Hardening

**Goal:** Ensure the system degrades gracefully without internet.

#### Tasks:
- [ ] Integrate `faster-whisper` as local STT fallback
- [ ] Verify Ollama integration with `gemma2:9b` for full consultation pipeline
- [ ] Implement request queue in mobile app (AsyncStorage buffer)
- [ ] Add `/health` endpoint that checks Ollama status independently
- [ ] Expand drug interaction database (`data/drug_interactions.json`) to 500+ pairs
- [ ] Test full offline workflow: record → transcribe locally → SOAP note via Gemma → SMS via cellular

---

## 4. Technology Stack (Final)

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | FastAPI (Python 3.12) | Async, high-performance, OpenAPI docs auto-generated |
| **Backend ORM** | SQLModel + SQLite | Simple, type-safe, PostgreSQL-compatible |
| **AI Online** | Gemini 2.0 Flash / OpenAI GPT-4o | Best accuracy for clinical NLP |
| **AI Offline** | Gemma 2 9B via Ollama | Free, local, OpenAI-compatible API |
| **STT Online** | OpenAI Whisper API | Best-in-class accuracy |
| **STT Offline** | faster-whisper (Python lib) | Local, no GPU required, good accuracy |
| **Admin Panel** | React 18 + Vite + TypeScript | Fast dev, modern tooling |
| **Admin Styling** | Tailwind CSS v4 | Utility-first, consistent with FamilyDoc AI |
| **Mobile** | React Native + Expo (SDK 52) | iOS + Android from one codebase |
| **Mobile State** | Zustand | Lightweight, no boilerplate |
| **SMS Gateway** | Africa's Talking | Best coverage for African markets |
| **Containerization** | Docker Compose | One-command clinic server setup |

---

## 5. Audio Transcription Plan (Critical Fix from v2)

The original MediVoice v2 called `manus-speech-to-text` — a sandboxed tool that doesn't exist in production. Here is the production plan:

```python
# stt_service.py

async def transcribe(audio_path: str, mode: OperationalMode) -> str:
    if mode == OperationalMode.ONLINE:
        # OpenAI Whisper API
        with open(audio_path, "rb") as f:
            result = openai_client.audio.transcriptions.create(
                model="whisper-1", file=f
            )
        return result.text
    else:
        # faster-whisper (local, no internet)
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu")  # or "small" for better accuracy
        segments, _ = model.transcribe(audio_path)
        return " ".join([s.text for s in segments])
```

---

## 6. Deployment Model

### Clinic Edge Server (Recommended)
```
Clinic Laptop (Linux/Windows/Mac)
├── Docker Compose
│   ├── mededge-backend (FastAPI on port 8000)
│   └── ollama (Gemma 2 on port 11434)
└── Admin Panel (served by backend at /admin or standalone Nginx)

Clinic WiFi Router
└── Mobile devices connect to clinic WiFi
    └── Staff app points to http://192.168.1.X:8000
```

### Cloud Deployment (Online Mode Only)
```
Railway / Render / AWS EC2
└── mededge-backend (FastAPI)
    └── Connected to Gemini API + OpenAI API
    └── SQLite or PostgreSQL
```

---

## 7. Data Privacy

- All consultation data stored locally on clinic device by default
- No data transmitted to cloud except AI API calls (transcript/image → LLM)
- In Offline Mode: **zero external data transmission** — fully air-gapped
- Patient PII stripped before SMS composition
- API keys stored in `.env` — never committed to repo

---

## 8. Hackathon Differentiation

What makes MedEdge stand out for the **Gemma 4 Good** hackathon:

1. **Dual-mode with seamless switching** — most submissions are online-only
2. **Feature phone SMS bridge** — true last-mile inclusion
3. **Admin Panel** — professional, production-minded design
4. **Cross-platform mobile** — not just a web demo
5. **Medical image analysis** — wound tracking, vitals OCR (multimodal Gemma)
6. **Local drug interaction database** — works with zero connectivity

---

## 9. Milestones

| Milestone | Target | Status |
|---|---|---|
| Repo scaffolded | Day 1 | ✅ Done |
| Backend Phase 1 (FastAPI refactor) | Day 2 | 🔲 |
| Settings Service + Mode Engine | Day 3 | 🔲 |
| Admin Panel (core screens) | Day 4 | 🔲 |
| Mobile App (Consultation + Camera) | Day 5–6 | 🔲 |
| Offline Hardening (Whisper + Ollama) | Day 7 | 🔲 |
| Integration Testing | Day 8 | 🔲 |
| Hackathon Submission | Day 9 | 🔲 |

---

*MedEdge — Built for the Gemma 4 Good Hackathon, May 2026*
