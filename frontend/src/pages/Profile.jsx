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
    <div className="page-container">
      <div className="page-header">
        <h2>Profile</h2>
      </div>

      <div className="profile-grid">
        <div className="card profile-card">
          <div className="profile-avatar-section">
            <div className="profile-avatar">{user?.full_name?.charAt(0) || 'U'}</div>
            <h3>{user?.full_name || 'User'}</h3>
            <p className="text-muted">{user?.email || ''}</p>
            <p className="text-muted">@{user?.username || ''}</p>
          </div>
        </div>

        <div className="card">
          <h3>Edit Profile</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" name="full_name" value={form.full_name} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input type="text" name="username" value={form.username} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Saving...' : 'Update Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
