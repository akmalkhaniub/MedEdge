import { useEffect, useState } from 'react'
import { getHealth, HealthData } from '../api'
import { RefreshCw } from 'lucide-react'

function statusClass(s: string) {
  if (s === 'online' || s === 'healthy') return 'ok'
  if (s === 'configured') return 'ok'
  if (s === 'no_key') return 'warn'
  return 'error'
}

function statusLabel(s: string) {
  if (s === 'online' || s === 'healthy') return 'Online'
  if (s === 'configured') return 'Configured'
  if (s === 'no_key') return 'No Key'
  if (s === 'offline') return 'Offline'
  return s
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthData | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(new Date())

  const load = async () => {
    setLoading(true)
    try {
      const data = await getHealth()
      setHealth(data)
      setLastRefresh(new Date())
    } catch {
      // backend may be down
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const modeOnline = health?.operation_mode === 'online'

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">System Dashboard</h1>
          <p className="page-subtitle">Real-time status of all MedEdge components</p>
        </div>
        <button className="btn btn-ghost" onClick={load} disabled={loading}>
          <RefreshCw size={14} className={loading ? 'spinner' : ''} />
          Refresh
        </button>
      </div>

      {/* Mode Banner */}
      <div style={{
        padding: '16px 20px',
        borderRadius: 'var(--r-lg)',
        marginBottom: 24,
        border: '1px solid',
        borderColor: modeOnline ? 'rgba(0,188,212,0.25)' : 'rgba(245,158,11,0.25)',
        background: modeOnline ? 'rgba(0,188,212,0.06)' : 'rgba(245,158,11,0.06)',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
      }}>
        <div style={{
          width: 10, height: 10, borderRadius: '50%',
          background: modeOnline ? 'var(--teal)' : 'var(--amber)',
          boxShadow: `0 0 10px ${modeOnline ? 'var(--teal)' : 'var(--amber)'}`,
          flexShrink: 0,
        }} />
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: modeOnline ? 'var(--teal)' : 'var(--amber)' }}>
            {modeOnline ? '🌐 ONLINE MODE' : '📡 OFFLINE MODE'}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
            {modeOnline
              ? `Cloud AI active — ${health?.cloud_model ?? '...'}`
              : 'Local Ollama/Gemma2 active — No internet required'}
          </div>
        </div>
        {health && (
          <span className={`badge ${modeOnline ? 'badge-online' : 'badge-offline'}`} style={{ marginLeft: 'auto' }}>
            {modeOnline ? '● Online' : '● Offline'}
          </span>
        )}
      </div>

      {/* Stats */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">AI Provider</div>
          <div className="stat-value" style={{ fontSize: 18, color: 'var(--teal)' }}>
            {health?.cloud_provider ?? '—'}
          </div>
          <div className="stat-sub">{health?.cloud_model ?? 'Loading...'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">MedGemma</div>
          <div className="stat-value" style={{ fontSize: 18, color: 'var(--blue)' }}>
            {health?.features.use_medgemma ? 'Active' : 'Disabled'}
          </div>
          <div className="stat-sub">{health?.features.medgemma_model ?? '—'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">STT Mode</div>
          <div className="stat-value" style={{ fontSize: 18, color: 'var(--text-primary)' }}>
            {health?.features.stt_mode ?? '—'}
          </div>
          <div className="stat-sub">Speech-to-text strategy</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">SMS Gateway</div>
          <div className="stat-value" style={{ fontSize: 18, color: health?.features.sms_gateway !== 'disabled' ? 'var(--green)' : 'var(--text-muted)' }}>
            {health?.features.sms_gateway ?? '—'}
          </div>
          <div className="stat-sub">Patient SMS delivery</div>
        </div>
      </div>

      {/* Provider HUD */}
      <div className="section">
        <div className="section-title">Provider Connectivity</div>
        {loading && !health ? (
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', color: 'var(--text-muted)', padding: 20 }}>
            <div className="spinner" /> Checking providers...
          </div>
        ) : (
          <div className="hud-grid">
            {health && Object.entries(health.providers).map(([name, info]) => {
              const cls = statusClass(info.status)
              const models = (info as any).models
              return (
                <div className={`hud-chip ${cls}`} key={name}>
                  <div className="hud-provider">{name}</div>
                  <div className="hud-status">{statusLabel(info.status)}</div>
                  {models && models.length > 0 && (
                    <div className="hud-detail">{models.slice(0, 2).join(', ')}</div>
                  )}
                  {(info as any).http_status && (
                    <div className="hud-detail">HTTP {(info as any).http_status}</div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 20 }}>
        Last refreshed: {lastRefresh.toLocaleTimeString()}
      </div>
    </div>
  )
}
