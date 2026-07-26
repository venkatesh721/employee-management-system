import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getEmployeeDashboard } from '../services/dashboardService'
import Loading from '../components/common/Loading'
import toast from 'react-hot-toast'

const money = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value || 0)

export default function EmployeeDashboard() {
  const [data, setData] = useState(null)
  useEffect(() => { getEmployeeDashboard().then((response) => setData(response.data)).catch(() => toast.error('Failed to load your dashboard')) }, [])
  if (!data) return <Loading />

  const cards = [
    ['Employee ID', data.employee?.employee_id || '—', 'identity', 'ID'],
    ['Present This Month', data.present_this_month || 0, 'present', '✓'],
    ['Late This Month', data.late_this_month || 0, 'late', '◷'],
    ['Absent This Month', data.absent_this_month || 0, 'absent', '×'],
    ['Latest Net Salary', data.latest_salary ? money(data.latest_salary.net_salary) : 'Not generated', 'salary', '₹'],
  ]

  return <div className="dashboard employee-dashboard">
    <section className="employee-welcome"><div><span className="eyebrow">MY GLOBALCO WORKSPACE</span><h2>Welcome, {data.employee?.name || 'Employee'}</h2><p>{data.employee?.position || 'Position not assigned'} · {data.message}</p></div><div className="employee-welcome-date"><span>{new Date().toLocaleDateString('en-US', { weekday: 'long' })}</span><strong>{new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}</strong></div></section>

    <div className="employee-stats-grid">{cards.map(([label, value, variant, icon]) => <article className={`employee-stat-card ${variant}`} key={label}><span className="employee-stat-icon">{icon}</span><div><span>{label}</span><strong>{value}</strong><small>{variant === 'salary' ? 'Latest payroll period' : variant === 'identity' ? 'Your profile identifier' : 'Current calendar month'}</small></div></article>)}</div>

    <div className="employee-dashboard-grid">
      <section className="card employee-salary-chart">
        <div className="employee-section-heading"><div><span className="eyebrow">COMPENSATION</span><h3>Salary Trend</h3><p>Your recent net salary progression</p></div><Link to="/employee/salary">View payslips →</Link></div>
        {!data.salary_history?.length ? <p className="text-muted">No salary has been generated yet.</p> : <ResponsiveContainer width="100%" height={280}><AreaChart data={data.salary_history}><defs><linearGradient id="salaryGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#4f46e5" stopOpacity={0.7}/><stop offset="95%" stopColor="#4f46e5" stopOpacity={0.05}/></linearGradient></defs><CartesianGrid strokeDasharray="4 6" vertical={false} stroke="var(--border)" /><XAxis dataKey="month" tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short' })} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false}/><YAxis tickFormatter={(value) => `₹${Math.round(value / 1000)}k`} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false}/><Tooltip formatter={(value) => money(value)} labelFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}/><Area type="monotone" dataKey="net_salary" name="Net salary" stroke="#4f46e5" fill="url(#salaryGradient)" strokeWidth={3}/></AreaChart></ResponsiveContainer>}
      </section>

      <section className="card employee-latest-salary">
        <div className="employee-section-heading"><div><span className="eyebrow">LATEST PAYROLL</span><h3>Salary Snapshot</h3></div><span className={`payroll-status ${data.latest_salary?.status || 'draft'}`}>{data.latest_salary?.status || 'Unavailable'}</span></div>
        {data.latest_salary ? <><p className="salary-hero">{money(data.latest_salary.net_salary)}</p><p className="text-muted">Net salary for {new Date(data.latest_salary.month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</p><div className="salary-detail"><span>Gross salary</span><strong>{money(data.latest_salary.gross_salary)}</strong></div><Link className="btn btn-primary" to="/employee/salary">Open Salary History</Link></> : <p className="text-muted">Payroll has not been generated for this account.</p>}
      </section>
    </div>

    <section className="card employee-attendance-card">
      <div className="employee-section-heading"><div><span className="eyebrow">MY ATTENDANCE</span><h3>Recent Attendance</h3><p>Your seven latest attendance records</p></div><Link to="/employee/attendance">Full history →</Link></div>
      <div className="table-responsive"><table className="table"><thead><tr><th>Date</th><th>Check In</th><th>Check Out</th><th>Status</th></tr></thead><tbody>{!data.recent_attendance?.length ? <tr><td colSpan="4" className="text-center">No attendance records found</td></tr> : data.recent_attendance.map((row) => <tr key={row.id}><td><strong>{new Date(`${row.date}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</strong></td><td>{row.check_in ? new Date(row.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</td><td>{row.check_out ? new Date(row.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</td><td><span className={`status-pill ${row.status === 'present' ? 'approved' : row.status === 'absent' ? 'rejected' : 'pending'}`}><i />{row.status.replace('_', ' ')}</span></td></tr>)}</tbody></table></div>
    </section>
  </div>
}
