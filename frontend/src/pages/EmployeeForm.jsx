import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { createEmployee, getEmployee, updateEmployee } from '../services/employeeService'
import { getDepartments } from '../services/departmentService'
import { STATUS_OPTIONS, POSITION_OPTIONS } from '../utils/constants'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'

const emptyForm = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  position: '',
  department_id: '',
  salary: '',
  date_of_birth: '',
  date_of_hire: '',
  address: '',
  city: '',
  state: '',
  zip_code: '',
  status: 'active',
  role: 'employee',
  password: '',
  is_active: true,
}

export default function EmployeeForm() {
  const { id } = useParams()
  const isEdit = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(isEdit)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getDepartments()
      .then((res) => setDepartments(res.data || []))
      .catch(() => {})

    if (isEdit) {
      getEmployee(id)
        .then((res) => {
          const emp = res.data
          setForm({
            first_name: emp.first_name || '',
            last_name: emp.last_name || '',
            email: emp.email || '',
            phone: emp.phone || '',
            position: emp.position || '',
            department_id: emp.department_id || '',
            salary: emp.salary || '',
            date_of_birth: emp.date_of_birth ? emp.date_of_birth.split('T')[0] : '',
            date_of_hire: emp.date_of_hire ? emp.date_of_hire.split('T')[0] : '',
            address: emp.address || '',
            city: emp.city || '',
            state: emp.state || '',
            zip_code: emp.zip_code || '',
            status: emp.status || 'active',
            role: emp.role || 'employee',
            password: '',
            is_active: emp.is_active ?? true,
          })
        })
        .catch(() => {
          toast.error('Failed to load employee')
          navigate('/admin/employees')
        })
        .finally(() => setLoading(false))
    }
  }, [id, isEdit, navigate])

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.first_name || !form.last_name || !form.email) {
      setError('First name, last name, and email are required')
      return
    }
    if (!isEdit && form.password.length < 8) {
      setError('A login password of at least 8 characters is required')
      return
    }
    setSaving(true)
    try {
      const payload = {
        ...form,
        salary: form.salary ? Number(form.salary) : null,
        department_id: form.department_id || null,
      }
      if (isEdit && !payload.password) delete payload.password
      if (isEdit) {
        await updateEmployee(id, payload)
        toast.success('Employee updated successfully')
      } else {
        await createEmployee(payload)
        toast.success('Employee created successfully')
      }
      navigate('/admin/employees')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to save employee'
      setError(msg)
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading />

  return (
    <div className="page-container management-page employee-form-page">
      <div className="page-header">
        <h2>{isEdit ? 'Edit Employee' : 'Add Employee'}</h2>
      </div>

      <div className="card">
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit} className="employee-form">
          <div className="form-row">
            <div className="form-group">
              <label>First Name *</label>
              <input type="text" name="first_name" value={form.first_name} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Last Name *</label>
              <input type="text" name="last_name" value={form.last_name} onChange={handleChange} className="form-control" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Account Role *</label>
              <select name="role" value={form.role} onChange={handleChange} className="form-control">
                <option value="employee">Employee</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="form-group">
              <label>{isEdit ? 'New Password (optional)' : 'Login Password *'}</label>
              <input type="password" name="password" minLength={isEdit ? undefined : 8} maxLength={72} value={form.password} onChange={handleChange} className="form-control" autoComplete="new-password" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email *</label>
              <input type="email" name="email" value={form.email} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input type="text" name="phone" value={form.phone} onChange={handleChange} className="form-control" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Department</label>
              <select name="department_id" value={form.department_id} onChange={handleChange} className="form-control">
                <option value="">Select Department</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Position</label>
              <select name="position" value={form.position} onChange={handleChange} className="form-control">
                <option value="">Select Position</option>
                {POSITION_OPTIONS.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Salary</label>
              <input type="number" name="salary" value={form.salary} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Status</label>
              <select name="status" value={form.status} onChange={handleChange} className="form-control">
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Date of Birth</label>
              <input type="date" name="date_of_birth" value={form.date_of_birth} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Date of Hire</label>
              <input type="date" name="date_of_hire" value={form.date_of_hire} onChange={handleChange} className="form-control" />
            </div>
          </div>
          <div className="form-group">
            <label>Address</label>
            <input type="text" name="address" value={form.address} onChange={handleChange} className="form-control" />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>City</label>
              <input type="text" name="city" value={form.city} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>State</label>
              <input type="text" name="state" value={form.state} onChange={handleChange} className="form-control" />
            </div>
            <div className="form-group">
              <label>Zip Code</label>
              <input type="text" name="zip_code" value={form.zip_code} onChange={handleChange} className="form-control" />
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-outline" onClick={() => navigate('/admin/employees')}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : isEdit ? 'Update Employee' : 'Create Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
