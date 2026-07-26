import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../services/authService'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await forgotPassword(email.trim().toLowerCase())
      setMessage(response.data.message)
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to process the request.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header"><div className="auth-logo">E</div><h2>Forgot Password?</h2><p>Enter your registered email address</p></div>
        {message && <div className="alert alert-success" role="status">{message}</div>}
        {error && <div className="alert alert-error" role="alert">{error}</div>}
        {!message && <form onSubmit={submit} className="auth-form">
          <div className="form-group"><label htmlFor="reset-email">Email</label><input id="reset-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="form-control" required autoFocus /></div>
          <button className="btn btn-primary btn-block" disabled={loading}>{loading ? 'Sending…' : 'Send Reset Link'}</button>
        </form>}
        <p className="auth-footer"><Link to="/login">Back to sign in</Link></p>
      </div>
    </div>
  )
}
