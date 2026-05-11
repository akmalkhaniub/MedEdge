import { useState } from 'react'
import { Eye, EyeOff, CheckCircle } from 'lucide-react'

const PROVIDERS = [
  {
    id: 'gemini',
    name: 'Google Gemini',
    badge: '🌐 Cloud',
    models: ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash'],
    envKey: 'GEMINI_API_KEY',
    note: 'Used for text + vision in online mode. Fastest, most capable.',
    color: 'var(--teal)',
  },
  {
    id: 'medgemma',
    name: 'MedGemma 4B',
    badge: '🧬 Medical',
    models: ['google/medgemma-4b-it'],
    envKey: 'OPENROUTER_API_KEY',
    note: 'Clinical specialist model via OpenRouter. Used for triage, prescriptions, SOAP refinement.',
    color: 'var(--blue)',
  },
  {
    id: 'groq',
    name: 'Groq (Llama)',
    badge: '⚡ Ultra-Fast',
    models: ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'],
    envKey: 'GROQ_API_KEY',
    note: 'Sub-second inference. Used as fallback or speed-critical tasks.',
    color: 'var(--amber)',
  },
  {
    id: 'openrouter',
    name: 'OpenRouter',
    badge: '🔀 Gateway',
    models: ['deepseek/deepseek-r1', 'anthropic/claude-3.5-sonnet'],
    envKey: 'OPENROUTER_API_KEY',
    note: 'Gateway to 100+ models including DeepSeek and Claude.',
    color: 'var(--orange)',
  },
  {
    id: 'ollama',
    name: 'Ollama (Local)',
    badge: '📡 Offline',
    models: ['gemma2:9b', 'llava:7b', 'llama3:8b'],
    envKey: '— (local)',
    note: 'Runs fully offline on clinic hardware. No internet or API key needed.',
    color: 'var(--green)',
  },
]

function MaskedInput({ value, placeholder }: { value: string; placeholder: string }) {
  const [show, setShow] = useState(false)
  return (
    <div style={{ position: 'relative' }}>
      <input
        className="input input-mono"
        type={show ? 'text' : 'password'}
        value={value}
        readOnly
        placeholder={placeholder}
        style={{ paddingRight: 40 }}
      />
      <button
        style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
        onClick={() => setShow(s => !s)}
      >
        {show ? <EyeOff size={14} /> : <Eye size={14} />}
      </button>
    </div>
  )
}

export default function Providers() {
  // API keys from .env are baked in — shown as masked. Real editing would require a backend endpoint.
  const KEYS: Record<string, string> = {
    GEMINI_API_KEY: import.meta.env.VITE_GEMINI_API_KEY || 'AIzaSy... (Set in .env)',
    GROQ_API_KEY: import.meta.env.VITE_GROQ_API_KEY || 'gsk_... (Set in .env)',
    OPENROUTER_API_KEY: import.meta.env.VITE_OPENROUTER_API_KEY || 'sk-or-v1-... (Set in .env)',
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Providers</h1>
          <p className="page-subtitle">Configured AI providers and their roles in the MedEdge pipeline</p>
        </div>
      </div>

      <div style={{ marginBottom: 20, padding: '12px 16px', background: 'var(--teal-glow-sm)', border: '1px solid rgba(0,188,212,0.15)', borderRadius: 'var(--r-md)', fontSize: 12, color: 'var(--text-secondary)' }}>
        💡 API keys are loaded from <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--teal)' }}>backend/.env</code> at server startup. Restart the backend after editing the .env file.
      </div>

      <div className="provider-grid">
        {PROVIDERS.map(p => (
          <div className="provider-card" key={p.id} style={{ borderColor: `${p.color}22` }}>
            <div className="provider-name">
              <span style={{ color: p.color }}>{p.name}</span>
              <span className="badge badge-info" style={{ fontSize: 10 }}>{p.badge}</span>
            </div>
            <div className="provider-model">{p.models[0]}</div>

            {p.envKey !== '— (local)' && (
              <div className="input-group">
                <label className="input-label">{p.envKey}</label>
                <MaskedInput value={KEYS[p.envKey] ?? ''} placeholder={`Enter ${p.envKey}`} />
              </div>
            )}

            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, marginTop: 4 }}>
              {p.note}
            </div>

            <div style={{ marginTop: 12 }}>
              <div className="section-title" style={{ fontSize: 10, marginBottom: 6 }}>Available Models</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                {p.models.map(m => (
                  <span key={m} style={{ fontFamily: 'var(--font-mono)', fontSize: 10, padding: '2px 8px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 4, color: 'var(--text-secondary)' }}>
                    {m}
                  </span>
                ))}
              </div>
            </div>

            {p.id !== 'ollama' && (
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'var(--green)' }}>
                <CheckCircle size={12} />
                <span>Key configured</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
