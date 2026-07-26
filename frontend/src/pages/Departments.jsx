import { useState, useEffect } from 'react'
import {
  getDepartments,
  normalizeDepartments,
  createDepartment,
  updateDepartment,
  deleteDepartment,
} from '../services/departmentService'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'

export default function Departments() {
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editDept, setEditDept] = useState(null)
  const [form, setForm] = useState({ name: '', description: '' })
  const [saving, setSaving] = useState(false)
  const [deleteId, setDeleteId] = useState(null)

  const fetchDepartments = async () => {
    try {
      const res = await getDepartments()
      setDepartments(normalizeDepartments(res))
    } catch {
      toast.error('Failed to load departments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDepartments()
  }, [])

  const openCreate = () => {
    setEditDept(null)
    setForm({ name: '', description: '' })
    setShowModal(true)
  }

  const openEdit = (dept) => {
    setEditDept(dept)
    setForm({ name: dept.name, description: dept.description || '' })
    setShowModal(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    if (!form.name.trim()) {
      toast.error('Department name is required')
      return
    }
    setSaving(true)
    try {
      if (editDept) {
        await updateDepartment(editDept.id, form)
        toast.success('Department updated')
      } else {
        await createDepartment(form)
        toast.success('Department created')
      }
      setShowModal(false)
      fetchDepartments()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save department')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteDepartment(deleteId)
      toast.success('Department deleted')
      setDeleteId(null)
      fetchDepartments()
    } catch {
      toast.error('Failed to delete department')
    }
  }

  if (loading) return <Loading />

  return (
    <div className="page-container management-page departments-page">
      <div className="page-header">
        <h2>Departments</h2>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Department</button>
      </div>

      <div className="card">
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Employee Count</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {departments.length === 0 ? (
                <tr><td colSpan={5} className="text-center">No departments found</td></tr>
              ) : (
                departments.map((dept, index) => (
                  <tr key={dept.id}>
                    <td>{index + 1}</td>
                    <td><strong>{dept.name}</strong></td>
                    <td>{dept.description || '-'}</td>
                    <td><span className="badge badge-active">{dept.employee_count || 0}</span></td>
                    <td className="actions-cell">
                      <button className="btn btn-sm btn-outline" onClick={() => openEdit(dept)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(dept.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editDept ? 'Edit Department' : 'Add Department'}</h3>
            <form onSubmit={handleSave}>
              <div className="form-group">
                <label>Name *</label>
                <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="form-control" placeholder="Department name" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="form-control" rows={3} placeholder="Optional description" />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : editDept ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteId && (
        <div className="modal-overlay" onClick={() => setDeleteId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this department?</p>
            <div className="modal-actions">
              <button className="btn btn-outline" onClick={() => setDeleteId(null)}>Cancel</button>
              <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
