import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { Activity, LayoutDashboard, Settings, Sliders, FileText, Pill } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import ModeControl from './pages/ModeControl'
import Providers from './pages/Providers'
import Logs from './pages/Logs'

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/mode', icon: Sliders, label: 'Mode Control' },
  { to: '/providers', icon: Settings, label: 'AI Providers' },
  { to: '/logs', icon: FileText, label: 'Consultation Logs' },
]

export default function App() {
  const loc = useLocation()

  return (
    <div className="shell">
      {/* Topbar */}
      <header className="topbar">
        <div className="topbar-logo">
          <span className="pulse-dot" />
          <span>MedEdge</span>
          <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>Admin</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Activity size={14} color="var(--teal)" />
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
            System Control Panel
          </span>
        </div>
      </header>

      {/* Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-section">Navigation</div>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Icon className="nav-icon" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Main */}
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/mode" element={<ModeControl />} />
          <Route path="/providers" element={<Providers />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </main>
    </div>
  )
}
