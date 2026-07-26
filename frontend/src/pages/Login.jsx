import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'

export default function Login() {
  const location = useLocation()
  const [role, setRole] = useState('admin')
  const [form, setForm] = useState({ identifier: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const requestedRole = new URLSearchParams(location.search).get('role')
    if (requestedRole === 'employee') setRole('employee')
  }, [location.search])

  const selectRole = (selectedRole) => {
    setRole(selectedRole)
    setError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const identifier = form.identifier.trim().toLowerCase()
    if (!identifier || !form.password) {
      setError('Email or username and password are required.')
      return
    }
    setLoading(true)
    try {
      const data = await login(identifier, form.password, role)
      navigate(data.user.role === 'admin' ? '/admin/dashboard' : '/employee/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).join(', ')
        : detail || (err.request
          ? 'Cannot connect to the server. Please make sure the backend is running.'
          : 'Login failed. Please try again.')
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page login-page">
      <div className="login-ambient" aria-hidden="true"><span /><span /><span /></div>
      <div className="auth-card login-card">
        <div className="auth-header">
          <div className="auth-logo">E</div>
          <h2>Welcome Back</h2>
          <p>Sign in to your account</p>
        </div>

        <div className="role-selector" role="tablist" aria-label="Select login role">
          <button type="button" role="tab" aria-selected={role === 'admin'} className={role === 'admin' ? 'active' : ''} onClick={() => selectRole('admin')}>
            Administrator
          </button>
          <button type="button" role="tab" aria-selected={role === 'employee'} className={role === 'employee' ? 'active' : ''} onClick={() => selectRole('employee')}>
            Employee
          </button>
        </div>

        {role === 'admin' && <p className="role-help">Administrator accounts are created through secure system setup.</p>}
        {error && <div className="alert alert-error" role="alert">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form" key={role}>
          <div className="form-group">
            <label htmlFor="identifier">Email or Username</label>
            <input id="identifier" type="text" autoComplete="username" value={form.identifier} onChange={(event) => { setForm({ ...form, identifier: event.target.value }); setError('') }} placeholder="you@example.com or username" className="form-control" required autoFocus />
          </div>
          <div className="form-group">
            <div className="label-row">
              <label htmlFor="password">Password</label>
              <Link to="/forgot-password">Forgot Password?</Link>
            </div>
            <div className="password-input">
              <input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" value={form.password} onChange={(event) => { setForm({ ...form, password: event.target.value }); setError('') }} placeholder="Enter your password" className="form-control" required maxLength={72} />
              <button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button>
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Signing in…' : `Sign In as ${role === 'admin' ? 'Administrator' : 'Employee'}`}
          </button>
        </form>
        <p className="auth-footer">New employee? <Link to="/register-employee">Register as Employee</Link></p>
      </div>
    </div>
  )
}
