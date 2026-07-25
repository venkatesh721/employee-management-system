import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/employees', label: 'Employees', icon: '👥' },
  { to: '/departments', label: 'Departments', icon: '🏢' },
  { to: '/attendance', label: 'Attendance', icon: '📋' },
  { to: '/profile', label: 'Profile', icon: '👤' },
]

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth()

  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon">E</span>
            <span className="logo-text">EMS</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={onClose}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">{user?.full_name?.charAt(0) || 'U'}</div>
            <div className="user-info">
              <p className="user-name">{user?.full_name || 'User'}</p>
              <p className="user-role">{user?.email || ''}</p>
            </div>
          </div>
          <button className="btn btn-danger btn-sm logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>
    </>
  )
}
