import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { updateProfile } from '../services/authService'
import toast from 'react-hot-toast'

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    username: user?.username || '',
  })
  const [saving, setSaving] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.full_name || !form.email) {
      toast.error('Name and email are required')
      return
    }
    setSaving(true)
    try {
      const res = await updateProfile(form)
      updateUser(res.data)
      toast.success('Profile updated successfully')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container management-page profile-page">
      <section className="profile-hero">
        <div><span className="eyebrow">ACCOUNT & IDENTITY</span><h2>My Profile</h2><p>Keep your personal account information accurate and up to date.</p></div>
        <span className="profile-security-chip">✓ Secure account</span>
      </section>

      <div className="profile-grid">
        <div className="card profile-card">
          <div className="profile-avatar-section">
            <div className="profile-avatar">{user?.full_name?.charAt(0) || 'U'}</div>
            <span className="profile-role">{user?.role || 'user'}</span>
            <h3>{user?.full_name || 'User'}</h3>
            <p className="text-muted">{user?.email || ''}</p>
            <p className="text-muted">@{user?.username || ''}</p>
            <div className="profile-account-details">
              <div><span>Account status</span><strong><i /> Active</strong></div>
              <div><span>Access level</span><strong>{user?.role === 'admin' ? 'Administrator' : 'Employee self-service'}</strong></div>
            </div>
          </div>
        </div>

        <div className="card profile-edit-card">
          <div className="profile-form-heading"><div><span className="eyebrow">PERSONAL DETAILS</span><h3>Edit Profile</h3><p>Changes are applied to your authenticated account.</p></div><span className="profile-form-icon">P</span></div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="profile-name">Full Name</label>
              <input id="profile-name" type="text" name="full_name" value={form.full_name} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label htmlFor="profile-username">Username</label>
              <input id="profile-username" type="text" name="username" value={form.username} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label htmlFor="profile-email">Email address</label>
              <input id="profile-email" type="email" name="email" value={form.email} onChange={handleChange} className="form-control" />
            </div>
            <div className="profile-form-notice"><span>i</span>Your email and username are used for account identification. They must remain unique.</div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Saving…' : 'Update Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
