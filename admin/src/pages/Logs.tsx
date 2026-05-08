import { useEffect, useState } from 'react'
import { getHistory, ConsultationRecord } from '../api'
import { RefreshCw, MessageSquare } from 'lucide-react'

const TRIAGE_CLASS: Record<string, string> = {
  LOW: 'badge-low', MEDIUM: 'badge-medium', HIGH: 'badge-high', CRITICAL: 'badge-critical',
}

export default function Logs() {
  const [records, setRecords] = useState<ConsultationRecord[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try { setRecords(await getHistory(50)) }
    catch { setRecords([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Consultation Logs</h1>
          <p className="page-subtitle">Recent clinical consultations processed by MedEdge</p>
        </div>
        <button className="btn btn-ghost" onClick={load} disabled={loading}>
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', color: 'var(--text-muted)', padding: 40 }}>
          <div className="spinner" /> Loading consultation history...
        </div>
      ) : records.length === 0 ? (
        <div className="empty">
          <div className="empty-icon">🩺</div>
          <div className="empty-text">No consultations yet. Run a consultation from the mobile app to see records here.</div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Patient</th>
                <th>Triage</th>
                <th>Diagnosis</th>
                <th>Language</th>
                <th>Mode</th>
                <th>SMS</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {records.map(r => (
                <tr key={r.id}>
                  <td className="mono" style={{ color: 'var(--text-muted)' }}>#{r.id}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <MessageSquare size={13} color="var(--text-muted)" />
                      <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                        {r.patient_name ?? 'Anonymous'}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${TRIAGE_CLASS[r.triage_level] ?? 'badge-medium'}`}>
                      {r.triage_level}
                    </span>
                  </td>
                  <td style={{ maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {r.primary_diagnosis || '—'}
                  </td>
                  <td>{r.language}</td>
                  <td>
                    <span className={`badge ${r.operation_mode_used === 'online' ? 'badge-info' : 'badge-offline'}`}>
                      {r.operation_mode_used}
                    </span>
                  </td>
                  <td>
                    {r.sms_sent
                      ? <span className="badge badge-online">● Sent</span>
                      : <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>—</span>
                    }
                  </td>
                  <td className="mono" style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
