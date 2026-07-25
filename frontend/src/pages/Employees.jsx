import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { getEmployees, deleteEmployee } from '../services/employeeService'
import { getDepartments } from '../services/departmentService'
import { STATUS_OPTIONS, PAGE_SIZE } from '../utils/constants'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [deleteId, setDeleteId] = useState(null)

  const fetchEmployees = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page, size: PAGE_SIZE }
      if (search) params.search = search
      if (departmentId) params.department_id = departmentId
      if (status) params.status = status
      const res = await getEmployees(params)
      setEmployees(res.data.items || res.data.data || [])
      setTotalPages(res.data.total_pages || res.data.pages || 1)
      setTotal(res.data.total || 0)
    } catch {
      toast.error('Failed to load employees')
    } finally {
      setLoading(false)
    }
  }, [page, search, departmentId, status])

  useEffect(() => {
    fetchEmployees()
  }, [fetchEmployees])

  useEffect(() => {
    getDepartments()
      .then((res) => setDepartments(res.data || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setPage(1)
  }, [search, departmentId, status])

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteEmployee(deleteId)
      toast.success('Employee deleted')
      setDeleteId(null)
      fetchEmployees()
    } catch {
      toast.error('Failed to delete employee')
    }
  }

  if (loading && employees.length === 0) return <Loading />

  return (
    <div className="page-container">
      <div className="page-header">
        <h2>Employees ({total})</h2>
        <Link to="/employees/new" className="btn btn-primary">+ Add Employee</Link>
      </div>

      <div className="card">
        <div className="search-filters">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="form-control search-input-wide"
          />
          <select value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} className="form-control">
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="form-control">
            <option value="">All Status</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>

        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Position</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr><td colSpan={7} className="text-center">No employees found</td></tr>
              ) : (
                employees.map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.id}</td>
                    <td>{emp.first_name} {emp.last_name}</td>
                    <td>{emp.email}</td>
                    <td>{emp.department_name || emp.department || '-'}</td>
                    <td>{emp.position || '-'}</td>
                    <td><span className={`badge badge-${emp.status}`}>{emp.status}</span></td>
                    <td className="actions-cell">
                      <Link to={`/employees/${emp.id}/edit`} className="btn btn-sm btn-outline">Edit</Link>
                      <button className="btn btn-sm btn-danger" onClick={() => setDeleteId(emp.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="btn btn-outline btn-sm">Previous</button>
            <span className="page-info">Page {page} of {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => setPage(page + 1)} className="btn btn-outline btn-sm">Next</button>
          </div>
        )}
      </div>

      {deleteId && (
        <div className="modal-overlay" onClick={() => setDeleteId(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Delete</h3>
            <p>Are you sure you want to delete this employee? This action cannot be undone.</p>
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
