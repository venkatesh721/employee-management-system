import { useState, useEffect } from 'react'
import { getAttendance, checkIn, checkOut, getTodayAttendance, getAttendanceSummary } from '../services/attendanceService'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'

export default function Attendance() {
  const [records, setRecords] = useState([])
  const [todayRecord, setTodayRecord] = useState(null)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [checkedIn, setCheckedIn] = useState(false)
  const [currentId, setCurrentId] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const params = { page, size: 10 }
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo

      const [recordsRes, todayRes, summaryRes] = await Promise.all([
        getAttendance(params),
        getTodayAttendance(),
        getAttendanceSummary(),
      ])
      setRecords(recordsRes.data.items || recordsRes.data.data || [])
      setTotalPages(recordsRes.data.total_pages || recordsRes.data.pages || 1)
      const td = todayRes.data
      setTodayRecord(td)
      if (td && td.check_in && !td.check_out) {
        setCheckedIn(true)
        setCurrentId(td.id)
      } else {
        setCheckedIn(false)
        setCurrentId(null)
      }
      setSummary(summaryRes.data)
    } catch {
      toast.error('Failed to load attendance data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, dateFrom, dateTo])

  const handleCheckIn = async () => {
    try {
      const res = await checkIn({ notes: '' })
      setCheckedIn(true)
      setCurrentId(res.data.id)
      toast.success('Checked in successfully')
      fetchData()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Check in failed')
    }
  }

  const handleCheckOut = async () => {
    if (!currentId) return
    try {
      await checkOut(currentId)
      setCheckedIn(false)
      setCurrentId(null)
      toast.success('Checked out successfully')
      fetchData()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Check out failed')
    }
  }

  if (loading && records.length === 0) return <Loading />

  return (
    <div className="page-container">
      <div className="attendance-summary">
        <div className="summary-card">
          <span className="summary-label">Present</span>
          <span className="summary-value" style={{ color: '#22c55e' }}>{summary?.present || 0}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Absent</span>
          <span className="summary-value" style={{ color: '#ef4444' }}>{summary?.absent || 0}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Late</span>
          <span className="summary-value" style={{ color: '#f59e0b' }}>{summary?.late || 0}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">Half Day</span>
          <span className="summary-value" style={{ color: '#8b5cf6' }}>{summary?.half_day || 0}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">On Leave</span>
          <span className="summary-value" style={{ color: '#64748b' }}>{summary?.leave || 0}</span>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Today's Attendance</h3>
          <div className="check-action">
            {todayRecord ? (
              <div className="current-status">
                <span className="badge badge-active">Checked In: {todayRecord.check_in ? new Date(todayRecord.check_in).toLocaleTimeString() : '-'}</span>
              </div>
            ) : (
              checkedIn ? null : <span className="text-muted">No record for today</span>
            )}
            {!checkedIn ? (
              <button className="btn btn-success" onClick={handleCheckIn}>Check In</button>
            ) : (
              <button className="btn btn-warning" onClick={handleCheckOut}>Check Out</button>
            )}
          </div>
        </div>

        <div className="search-filters">
          <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setPage(1) }} className="form-control" />
          <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setPage(1) }} className="form-control" />
        </div>

        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Status</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {records.length === 0 ? (
                <tr><td colSpan={6} className="text-center">No attendance records found</td></tr>
              ) : (
                records.map((rec) => (
                  <tr key={rec.id}>
                    <td>{rec.employee_name || rec.employee?.first_name + ' ' + rec.employee?.last_name || `Employee #${rec.employee_id}`}</td>
                    <td>{rec.date ? new Date(rec.date).toLocaleDateString() : '-'}</td>
                    <td>{rec.check_in ? new Date(rec.check_in).toLocaleTimeString() : '-'}</td>
                    <td>{rec.check_out ? new Date(rec.check_out).toLocaleTimeString() : '-'}</td>
                    <td><span className={`badge badge-${rec.status || 'present'}`}>{rec.status || 'present'}</span></td>
                    <td>{rec.notes || '-'}</td>
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
    </div>
  )
}
