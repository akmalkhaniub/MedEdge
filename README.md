# 🏥 MedEdge
### AI-Powered Hybrid Clinical Assistant
> *AI-driven clinical intelligence. Online, offline, and everywhere in between.*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-orange.svg)]()
[![Hackathon: Gemma 4 Good](https://img.shields.io/badge/Hackathon-Gemma%204%20Good-blue.svg)]()

---

## What is MedEdge?

MedEdge is a **cross-platform, hybrid-mode clinical assistant** designed for healthcare workers in resource-constrained environments. It runs AI inference locally on a clinic's device (offline) or via cloud APIs (online), with a seamless admin panel to switch between modes — and a mobile app for clinic staff to use at the bedside.

At the "last mile" — rural clinics with unreliable internet, feature-phone-only patients, and a single overworked nurse — MedEdge gives healthcare workers a **clinical superpower**.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎙️ **Consultation Pipeline** | Audio recording → Transcription → SOAP Note → Triage → Prescription Draft |
| 🔬 **Medical Image Analysis** | Wound tracking, rash identification, X-ray assessment, Vitals OCR |
| 📱 **Feature Phone SMS Bridge** | Plain-language SMS in 15+ languages delivered to 2G phones via Africa's Talking |
| 💊 **Drug Interaction Checker** | Offline database, no internet required |
| 🌐 **Hybrid AI Mode** | Cloud (Gemini/GPT-4) when online; Gemma 4 via Ollama when offline |
| 🛠️ **Admin Control Panel** | Web dashboard to switch modes, configure providers, monitor system health |
| 📱 **Mobile App** | React Native/Expo for iOS + Android — runs over clinic local WiFi |

---

## 🏗️ Architecture

```
MedEdge/
├── backend/        # FastAPI — the AI brain & REST API
├── admin/          # React/Vite — Admin Control Panel (web)
├── mobile/         # React Native/Expo — Mobile app for clinic staff
├── docs/           # Architecture, API specs, roadmap
└── scripts/        # Setup, deployment, database migration scripts
```

### Hybrid Mode Strategy

```
Online Mode  → Backend calls Gemini 2.0 Flash / OpenAI (cloud API)
Offline Mode → Backend calls Gemma 4 (via local Ollama instance)
               Mobile app connects to backend over clinic LAN (WiFi)
               SMS delivery via Africa's Talking (2G network, no patient internet needed)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- [Ollama](https://ollama.com/) (for offline mode)
- Git

### 1. Clone the repo
```bash
git clone https://github.com/akmalkhaniub/MedEdge.git
cd MedEdge
```

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # Fill in your API keys
uvicorn main:app --reload
```

### 3. Start the Admin Panel
```bash
cd admin
npm install
npm run dev
```

### 4. Start the Mobile App
```bash
cd mobile
npm install
npx expo start
```

### 5. (Optional) Enable Offline Mode with Ollama
```bash
ollama pull gemma2:9b
# Then toggle "Offline Mode" in the Admin Panel
```

---

## 🧠 AI Providers

| Mode | LLM | STT | Vision |
|---|---|---|---|
| **Online** | Gemini 2.0 Flash | OpenAI Whisper API | Gemini Vision |
| **Offline** | Gemma 2 9B (Ollama) | Whisper.cpp (local) | LLaVA (Ollama) |

---

## 📡 Patient Communication (Last Mile)

Patients receive clinical summaries via SMS — no smartphone needed:
- **Gateway**: Africa's Talking or Twilio
- **Network**: 2G / GSM (works on any basic feature phone)
- **Languages**: English, French, Arabic, Swahili, Urdu, Hindi, + 9 more
- **Cost**: ~$0.004 per SMS

---

## ⚠️ Disclaimer

MedEdge is a **clinical decision support tool**. All AI-generated outputs (SOAP notes, triage classifications, prescription drafts) must be reviewed and approved by a licensed medical professional before any clinical action is taken. MedEdge does not replace physicians.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for the Gemma 4 Good Hackathon — May 2026*
