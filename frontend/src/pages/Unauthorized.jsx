import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Unauthorized() {
  const { user } = useAuth()
  const home = user?.role === 'admin' ? '/admin/dashboard' : '/employee/dashboard'
  return (
    <div className="auth-page">
      <div className="auth-card auth-header">
        <div className="auth-logo">403</div>
        <h2>Access denied</h2>
        <p>Your account does not have permission to open this page.</p>
        <Link className="btn btn-primary btn-block" to={home}>Return to dashboard</Link>
      </div>
    </div>
  )
}
