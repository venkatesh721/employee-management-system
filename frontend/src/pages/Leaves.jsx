import { useCallback, useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'

const initialForm = { leave_type: 'annual', start_date: '', end_date: '', reason: '' }
const leaveLabels = { annual: 'Annual Leave', sick: 'Sick Leave', casual: 'Casual Leave' }

export default function Leaves() {
  const { user } = useAuth()
  const admin = user?.role === 'admin'
  const [rows, setRows] = useState([])
  const [balances, setBalances] = useState([])
  const [form, setForm] = useState(initialForm)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [requests, balanceResponse] = await Promise.all([
        api.get('/leaves'),
        ...(!admin ? [api.get('/leaves/balances')] : []),
      ])
      setRows(requests.data || [])
      if (balanceResponse) setBalances(balanceResponse.data || [])
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load leave information')
    } finally {
      setLoading(false)
    }
  }, [admin])

  useEffect(() => { load() }, [load])

  const submit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/leaves', {
        ...form,
        start_date: `${form.start_date}T00:00:00`,
        end_date: `${form.end_date}T00:00:00`,
      })
      toast.success('Leave request submitted')
      setForm(initialForm)
      load()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unable to apply for leave')
    } finally {
      setSubmitting(false)
    }
  }

  const review = async (id, status) => {
    const remarks = window.prompt(`Add remarks for this ${status} request`) || ''
    try {
      await api.put(`/leaves/${id}/review`, { status, remarks })
      toast.success(`Leave request ${status}`)
      load()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Review failed')
    }
  }

  if (loading) return <Loading />
  const statusCounts = ['pending', 'approved', 'rejected'].map((status) => ({
    status,
    count: rows.filter((row) => row.status === status).length,
  }))

  return (
    <div className="page-container leave-page">
      <div className="leave-summary-grid">
        {!admin && <div className="leave-summary-card balance"><span>Available Leave</span><strong>{balances.reduce((sum, item) => sum + item.available_days, 0)} days</strong><small>Across all leave types</small></div>}
        {statusCounts.map(({ status, count }) => <div className={`leave-summary-card ${status}`} key={status}><span>{status}</span><strong>{count}</strong><small>{status === 'pending' ? 'Awaiting review' : `${status} requests`}</small></div>)}
      </div>

      {!admin && <form className="card leave-form-card" onSubmit={submit}>
        <div className="section-heading"><div><h3>Apply for Leave</h3><p>Submit your dates and reason for administrator review.</p></div><span className="section-icon">L</span></div>
        <div className="leave-form-grid">
          <div className="form-group"><label htmlFor="leave-type">Leave type</label><select id="leave-type" className="form-control" value={form.leave_type} onChange={(event) => setForm({ ...form, leave_type: event.target.value })}>{Object.entries(leaveLabels).map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></div>
          <div className="form-group"><label htmlFor="leave-start">Start date</label><input id="leave-start" className="form-control" type="date" required value={form.start_date} onChange={(event) => setForm({ ...form, start_date: event.target.value })} /></div>
          <div className="form-group"><label htmlFor="leave-end">End date</label><input id="leave-end" className="form-control" type="date" required min={form.start_date} value={form.end_date} onChange={(event) => setForm({ ...form, end_date: event.target.value })} /></div>
          <div className="form-group reason-field"><label htmlFor="leave-reason">Reason</label><textarea id="leave-reason" className="form-control" rows="3" required maxLength="500" placeholder="Briefly explain your leave request" value={form.reason} onChange={(event) => setForm({ ...form, reason: event.target.value })} /></div>
        </div>
        <div className="leave-form-footer"><small>{form.reason.length}/500 characters</small><button className="btn btn-primary" disabled={submitting}>{submitting ? 'Submitting…' : 'Submit Leave Request'}</button></div>
      </form>}

      <div className="card leave-table-card">
        <div className="section-heading"><div><h3>{admin ? 'Leave Approvals' : 'My Leave Requests'}</h3><p>{admin ? 'Review employee requests and record your decision.' : 'Track your submitted leave and approval status.'}</p></div><span className="record-count">{rows.length} records</span></div>
        <div className="table-responsive"><table className="table"><thead><tr><th>Leave type</th><th>Dates</th><th>Duration</th><th>Reason</th><th>Status</th>{admin && <th>Review</th>}</tr></thead>
          <tbody>{!rows.length ? <tr><td colSpan={admin ? 6 : 5}><div className="polished-empty"><span>L</span><strong>No leave requests yet</strong><p>Your submitted requests will appear here.</p></div></td></tr> : rows.map((row) => {
            const days = Math.round((new Date(row.end_date) - new Date(row.start_date)) / 86400000) + 1
            return <tr key={row.id}><td><strong>{leaveLabels[row.leave_type] || row.leave_type}</strong></td><td><span className="date-range">{new Date(row.start_date).toLocaleDateString()}<small>to {new Date(row.end_date).toLocaleDateString()}</small></span></td><td>{days} {days === 1 ? 'day' : 'days'}</td><td className="leave-reason-cell">{row.reason}</td><td><span className={`status-pill ${row.status}`}><i />{row.status}</span></td>{admin && <td>{row.status === 'pending' ? <div className="review-actions"><button className="btn btn-success btn-sm" onClick={() => review(row.id, 'approved')}>Approve</button><button className="btn btn-danger btn-sm" onClick={() => review(row.id, 'rejected')}>Reject</button></div> : <span className="text-muted">Reviewed</span>}</td>}</tr>
          })}</tbody>
        </table></div>
      </div>
    </div>
  )
}
