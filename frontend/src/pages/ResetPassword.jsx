import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { resetPassword } from '../services/authService'
import toast from 'react-hot-toast'

export default function ResetPassword() {
  const [params] = useSearchParams()
  const [form, setForm] = useState({ password: '', confirm_password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const token = params.get('token') || ''

  const submit = async (event) => {
    event.preventDefault()
    if (!token) return setError('The password-reset link is invalid.')
    if (form.password !== form.confirm_password) return setError('Passwords do not match.')
    setLoading(true)
    try {
      await resetPassword({ token, ...form })
      toast.success('Password reset successful. Please sign in.')
      navigate('/login')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || 'Password reset failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header"><div className="auth-logo">E</div><h2>Reset Password</h2><p>Choose a strong new password</p></div>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <form onSubmit={submit} className="auth-form">
          <div className="form-group"><label htmlFor="new-password">New Password</label><div className="password-input"><input id="new-password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={(event) => { setForm({ ...form, password: event.target.value }); setError('') }} className="form-control" required minLength={8} maxLength={72} autoComplete="new-password" /><button type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button></div><small className="password-guidance">Use uppercase, lowercase, number, and special character.</small></div>
          <div className="form-group"><label htmlFor="confirm-new-password">Confirm New Password</label><input id="confirm-new-password" type="password" value={form.confirm_password} onChange={(event) => { setForm({ ...form, confirm_password: event.target.value }); setError('') }} className="form-control" required minLength={8} maxLength={72} autoComplete="new-password" /></div>
          <button className="btn btn-primary btn-block" disabled={loading || !token}>{loading ? 'Updating…' : 'Reset Password'}</button>
        </form>
        <p className="auth-footer"><Link to="/login">Back to sign in</Link></p>
      </div>
    </div>
  )
}
