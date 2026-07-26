import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerEmployee } from '../services/authService'
import toast from 'react-hot-toast'

const initialForm = {
  full_name: '', username: '', email: '', phone: '',
  password: '', confirm_password: '', accept_terms: false,
}

export default function RegisterEmployee() {
  const [form, setForm] = useState(initialForm)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const update = (event) => {
    const { name, value, type, checked } = event.target
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value })
    setError('')
  }

  const submit = async (event) => {
    event.preventDefault()
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      await registerEmployee({ ...form, email: form.email.trim().toLowerCase() })
      toast.success('Employee registration successful. Please sign in.')
      navigate('/login?role=employee')
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || 'Registration failed.'
      setError(message)
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <div className="auth-header"><div className="auth-logo">E</div><h2>Register as Employee</h2><p>Create your employee account</p></div>
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        <form onSubmit={submit} className="auth-form">
          <div className="form-row">
            <div className="form-group"><label htmlFor="full_name">Full Name</label><input id="full_name" name="full_name" value={form.full_name} onChange={update} className="form-control" required maxLength={255} /></div>
            <div className="form-group"><label htmlFor="username">Username</label><input id="username" name="username" value={form.username} onChange={update} className="form-control" required minLength={3} maxLength={150} pattern="[A-Za-z0-9_.-]+" /></div>
          </div>
          <div className="form-row">
            <div className="form-group"><label htmlFor="email">Email</label><input id="email" name="email" type="email" value={form.email} onChange={update} className="form-control" required /></div>
            <div className="form-group"><label htmlFor="phone">Phone Number</label><input id="phone" name="phone" type="tel" value={form.phone} onChange={update} className="form-control" maxLength={30} /></div>
          </div>
          <div className="form-group">
            <label htmlFor="register-password">Password</label>
            <div className="password-input">
              <input id="register-password" name="password" type={showPassword ? 'text' : 'password'} value={form.password} onChange={update} className="form-control" required minLength={8} maxLength={72} autoComplete="new-password" />
              <button type="button" onClick={() => setShowPassword(!showPassword)}>{showPassword ? 'Hide' : 'Show'}</button>
            </div>
            <small className="password-guidance">8+ characters with uppercase, lowercase, number, and special character.</small>
          </div>
          <div className="form-group"><label htmlFor="confirm_password">Confirm Password</label><input id="confirm_password" name="confirm_password" type="password" value={form.confirm_password} onChange={update} className="form-control" required minLength={8} maxLength={72} autoComplete="new-password" /></div>
          <label className="checkbox-row"><input name="accept_terms" type="checkbox" checked={form.accept_terms} onChange={update} required /><span>I accept the terms and privacy policy.</span></label>
          <button className="btn btn-primary btn-block" disabled={loading}>{loading ? 'Creating account…' : 'Register Employee'}</button>
        </form>
        <p className="auth-footer">Already registered? <Link to="/login?role=employee">Sign in as Employee</Link></p>
      </div>
    </div>
  )
}
