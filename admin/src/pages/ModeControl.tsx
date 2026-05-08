import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { getSettings, updateSettings, AppSettings } from '../api'
import { Wifi, WifiOff, Zap, CheckCircle, AlertCircle } from 'lucide-react'

function Toast({ msg, type }: { msg: string; type: 'success' | 'error' }) {
  return (
    <motion.div
      className={`toast ${type}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
    >
      {type === 'success' ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
      {msg}
    </motion.div>
  )
}

export default function ModeControl() {
  const [settings, setSettings] = useState<AppSettings | null>(null)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState<{ msg: string; type: 'success' | 'error' } | null>(null)

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  useEffect(() => {
    getSettings().then(setSettings).catch(() => {})
  }, [])

  const toggleMode = async () => {
    if (!settings) return
    const next: AppSettings = {
      ...settings,
      operation_mode: settings.operation_mode === 'online' ? 'offline' : 'online',
    }
    setSaving(true)
    try {
      const res = await updateSettings(next)
      setSettings(res.settings)
      showToast(`Switched to ${res.settings.operation_mode.toUpperCase()} mode`, 'success')
    } catch {
      showToast('Failed to switch mode', 'error')
    } finally {
      setSaving(false)
    }
  }

  const save = async (patch: Partial<AppSettings>) => {
    if (!settings) return
    const next = { ...settings, ...patch }
    setSaving(true)
    try {
      const res = await updateSettings(next)
      setSettings(res.settings)
      showToast('Settings saved', 'success')
    } catch {
      showToast('Save failed', 'error')
    } finally {
      setSaving(false)
    }
  }

  const isOnline = settings?.operation_mode === 'online'

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Mode Control</h1>
          <p className="page-subtitle">Switch between cloud AI (online) and local Gemma (offline)</p>
        </div>
      </div>

      {/* Big Mode Toggle */}
      <motion.div
        className="mode-toggle-container"
        animate={{ borderColor: isOnline ? 'rgba(0,188,212,0.3)' : 'rgba(245,158,11,0.3)' }}
        style={{ border: '1px solid' }}
      >
        <motion.div
          animate={{ scale: isOnline ? [1, 1.05, 1] : 1 }}
          transition={{ duration: 0.4 }}
        >
          {isOnline
            ? <Wifi size={32} color="var(--teal)" />
            : <WifiOff size={32} color="var(--amber)" />
          }
        </motion.div>

        <div style={{ flex: 1 }}>
          <motion.div
            className="mode-label-text"
            animate={{ color: isOnline ? 'var(--teal)' : 'var(--amber)' }}
          >
            {settings ? (isOnline ? '🌐 Online Mode' : '📡 Offline Mode') : '...'}
          </motion.div>
          <div className="mode-sublabel">
            {isOnline
              ? `Cloud AI via ${settings?.cloud_provider ?? '...'} — Internet required`
              : 'Local Ollama/Gemma2 — No internet required'}
          </div>
        </div>

        <button
          className={`btn ${isOnline ? 'btn-ghost' : 'btn-primary'}`}
          onClick={toggleMode}
          disabled={saving || !settings}
          style={{ minWidth: 140 }}
        >
          {saving ? <div className="spinner" /> : <Zap size={14} />}
          {saving ? 'Switching...' : `Switch to ${isOnline ? 'Offline' : 'Online'}`}
        </button>
      </motion.div>

      {/* Online Settings */}
      <div className="section">
        <div className="section-title">Online Mode Settings</div>
        {settings && (
          <div className="card" style={{ opacity: isOnline ? 1 : 0.5 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="input-group">
                <label className="input-label">Cloud Provider</label>
                <select
                  className="input"
                  value={settings.cloud_provider}
                  disabled={!isOnline}
                  onChange={e => save({ cloud_provider: e.target.value as AppSettings['cloud_provider'] })}
                >
                  <option value="gemini">Gemini (Google)</option>
                  <option value="groq">Groq (Llama)</option>
                  <option value="openrouter">OpenRouter</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Cloud Model</label>
                <select
                  className="input"
                  value={settings.cloud_model}
                  disabled={!isOnline}
                  onChange={e => save({ cloud_model: e.target.value })}
                >
                  <option value="gemini-2.0-flash">gemini-2.0-flash</option>
                  <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                  <option value="gemini-2.5-flash">gemini-2.5-flash</option>
                  <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
                </select>
              </div>
            </div>

            {/* MedGemma toggle */}
            <div className="medgemma-card" style={{ marginTop: 8 }}>
              <div className="medgemma-title">
                🧬 MedGemma Clinical Specialist
              </div>
              <div className="medgemma-desc">
                When enabled, triage classification and prescription drafts are routed to
                <strong> google/medgemma-4b-it</strong> via OpenRouter — a model specialized
                for clinical medical tasks. Falls back to primary provider in offline mode.
              </div>
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 12 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={settings.use_medgemma}
                    onChange={e => save({ use_medgemma: e.target.checked })}
                    style={{ accentColor: 'var(--blue)', width: 16, height: 16 }}
                  />
                  <span style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 500 }}>
                    Use MedGemma for clinical reasoning
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Offline Settings */}
      <div className="section">
        <div className="section-title">Offline Mode Settings</div>
        {settings && (
          <div className="card" style={{ opacity: !isOnline ? 1 : 0.5 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="input-group">
                <label className="input-label">Ollama LLM Model</label>
                <input
                  className="input input-mono"
                  value={settings.ollama_model}
                  disabled={isOnline}
                  onChange={e => setSettings({ ...settings, ollama_model: e.target.value })}
                  onBlur={() => save({ ollama_model: settings.ollama_model })}
                  placeholder="gemma2:9b"
                />
              </div>
              <div className="input-group">
                <label className="input-label">Ollama Vision Model</label>
                <input
                  className="input input-mono"
                  value={settings.ollama_vision_model}
                  disabled={isOnline}
                  onChange={e => setSettings({ ...settings, ollama_vision_model: e.target.value })}
                  onBlur={() => save({ ollama_vision_model: settings.ollama_vision_model })}
                  placeholder="llava:7b"
                />
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>
              💡 Run <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--teal)', background: 'var(--bg-surface)', padding: '1px 6px', borderRadius: 4 }}>ollama pull gemma2:9b</code> on this machine to enable offline mode.
            </div>
          </div>
        )}
      </div>

      {/* STT + SMS */}
      <div className="section">
        <div className="section-title">Speech & Communication</div>
        {settings && (
          <div className="card">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
              <div className="input-group">
                <label className="input-label">STT Mode</label>
                <select className="input" value={settings.stt_mode} onChange={e => save({ stt_mode: e.target.value as AppSettings['stt_mode'] })}>
                  <option value="auto">Auto (follows mode)</option>
                  <option value="openai">Always OpenAI Whisper</option>
                  <option value="local">Always Local (faster-whisper)</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Local Whisper Model</label>
                <select className="input" value={settings.whisper_local_model} onChange={e => save({ whisper_local_model: e.target.value })}>
                  <option value="tiny">tiny (fastest)</option>
                  <option value="base">base (balanced)</option>
                  <option value="small">small (accurate)</option>
                  <option value="medium">medium (best)</option>
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">SMS Gateway</label>
                <select className="input" value={settings.sms_gateway} onChange={e => save({ sms_gateway: e.target.value as AppSettings['sms_gateway'] })}>
                  <option value="disabled">Disabled</option>
                  <option value="africas_talking">Africa's Talking</option>
                  <option value="twilio">Twilio</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      <AnimatePresence>
        {toast && <Toast msg={toast.msg} type={toast.type} />}
      </AnimatePresence>
    </div>
  )
}
