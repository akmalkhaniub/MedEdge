// MedEdge Admin — API client (proxied through Vite dev server to :8000)
import axios from 'axios'

const API_KEY = 'mededge-dev-key-2026'
const ADMIN_KEY = 'mededge-admin-2026'

export const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'X-API-Key': API_KEY },
})

export const adminApi = axios.create({
  baseURL: '/api/v1',
  headers: { 'X-API-Key': ADMIN_KEY },
})

// ── Types ──────────────────────────────────────────────────────────────────
export interface AppSettings {
  operation_mode: 'online' | 'offline'
  cloud_provider: 'gemini' | 'groq' | 'openrouter'
  cloud_model: string
  ollama_model: string
  ollama_vision_model: string
  use_medgemma: boolean
  medgemma_model: string
  medgemma_provider: 'openrouter' | 'google_ai_studio'
  stt_mode: 'auto' | 'openai' | 'local'
  whisper_local_model: string
  sms_gateway: 'africas_talking' | 'twilio' | 'disabled'
  sms_enabled: boolean
  default_language: string
  use_mock_ai: boolean
  drug_check_enabled: boolean
  prescription_draft_enabled: boolean
  wound_tracker_enabled: boolean
}

export interface HealthData {
  status: string
  operation_mode: string
  cloud_provider: string
  cloud_model: string
  providers: {
    ollama: { status: string; models?: string[] }
    gemini: { status: string; http_status?: number }
    groq: { status: string }
    openrouter: { status: string }
  }
  features: {
    use_medgemma: boolean
    medgemma_model: string
    stt_mode: string
    sms_gateway: string
    drug_check: boolean
  }
}

export interface ConsultationRecord {
  id: number
  patient_name: string | null
  triage_level: string
  primary_diagnosis: string
  language: string
  sms_sent: boolean
  operation_mode_used: string
  created_at: string
}

// ── API calls ──────────────────────────────────────────────────────────────
export const getHealth = () => api.get<HealthData>('/health').then(r => r.data)
export const getSettings = () => api.get<AppSettings>('/settings').then(r => r.data)
export const updateSettings = (s: AppSettings) => adminApi.put<{ status: string; settings: AppSettings }>('/settings', s).then(r => r.data)
export const getHistory = (limit = 30) => api.get<ConsultationRecord[]>(`/consult/history?limit=${limit}`).then(r => r.data)
