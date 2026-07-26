import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getAttendanceChart, getDepartmentDistribution, getRecentEmployees, getStats } from '../services/dashboardService'
import { useAuth } from '../hooks/useAuth'
import Loading from '../components/common/Loading'

const palette = ['#243b64', '#4f46e5', '#c6923c', '#3f7d72', '#8a5a7b', '#70839e', '#a85751']
const shortDate = (value) => new Date(`${value}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return <div className="classic-tooltip"><strong>{label?.includes('-') ? shortDate(label) : label}</strong>{payload.map((item) => <span key={item.name}><i style={{ background: item.color }} />{item.name}: <b>{item.value}</b></span>)}</div>
}

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [chartData, setChartData] = useState([])
  const [deptData, setDeptData] = useState([])
  const [recentEmployees, setRecentEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), getAttendanceChart(), getDepartmentDistribution(), getRecentEmployees()])
      .then(([statsRes, chartRes, deptRes, recentRes]) => {
        setStats(statsRes.data)
        setChartData(chartRes.data?.datasets || [])
        setDeptData(deptRes.data || [])
        setRecentEmployees(recentRes.data || [])
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />

  const activeRate = stats?.total_employees ? Math.round((stats.active_employees / stats.total_employees) * 100) : 0
  const cards = [
    { label: 'Total Employees', value: stats?.total_employees || 0, note: 'Company workforce', color: '#243b64', icon: '◎' },
    { label: 'Active Employees', value: stats?.active_employees || 0, note: `${activeRate}% active rate`, color: '#3f7d72', icon: '✓' },
    { label: 'Departments', value: stats?.total_departments || 0, note: 'Business units', color: '#c6923c', icon: '▤' },
    { label: "Today's Attendance", value: stats?.today_attendance || 0, note: 'Records submitted', color: '#4f46e5', icon: '◷' },
  ]

  return (
    <div className="dashboard admin-dashboard">
      <section className="admin-welcome">
        <div><span className="eyebrow">GLOBALCO WORKFORCE OVERVIEW</span><h2>Good day, {user?.full_name?.split(' ')[0] || 'Administrator'}</h2><p>Here is a clear view of your people, attendance, and organisation today.</p></div>
        <div className="welcome-date"><span>{new Date().toLocaleDateString('en-US', { weekday: 'long' })}</span><strong>{new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</strong></div>
      </section>

      <div className="classic-stats-grid">
        {cards.map((card) => <article key={card.label} className="classic-stat-card" style={{ '--card-accent': card.color }}>
          <div className="classic-stat-icon">{card.icon}</div><div className="classic-stat-copy"><span>{card.label}</span><strong>{card.value}</strong><small>{card.note}</small></div><i className="card-corner" />
        </article>)}
      </div>

      <div className="classic-charts-grid">
        <section className="card classic-chart-card attendance-panel">
          <div className="classic-card-heading"><div><span className="eyebrow">ATTENDANCE</span><h3>30-Day Attendance Trend</h3><p>Daily workforce presence and exceptions</p></div><Link to="/admin/attendance" className="text-action">View records →</Link></div>
          {!chartData.length ? <div className="polished-empty"><span>◷</span><strong>No attendance data</strong></div> : <ResponsiveContainer width="100%" height={320}>
            <BarChart data={chartData} margin={{ top: 12, right: 8, left: -18, bottom: 4 }} barGap={2}>
              <CartesianGrid strokeDasharray="4 6" vertical={false} stroke="var(--border)" />
              <XAxis dataKey="date" tickFormatter={shortDate} interval="preserveStartEnd" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: 'var(--primary-light)', opacity: .45 }} />
              <Legend iconType="circle" iconSize={8} wrapperStyle={{ paddingTop: 16, fontSize: 12 }} />
              <Bar dataKey="present" name="Present" fill="#3f7d72" radius={[5, 5, 0, 0]} maxBarSize={18} />
              <Bar dataKey="late" name="Late" fill="#c6923c" radius={[5, 5, 0, 0]} maxBarSize={18} />
              <Bar dataKey="absent" name="Absent" fill="#a85751" radius={[5, 5, 0, 0]} maxBarSize={18} />
            </BarChart>
          </ResponsiveContainer>}
        </section>

        <section className="card classic-chart-card department-panel">
          <div className="classic-card-heading"><div><span className="eyebrow">ORGANISATION</span><h3>Department Composition</h3><p>Employee distribution by business unit</p></div></div>
          {!deptData.length ? <div className="polished-empty"><span>▤</span><strong>No department data</strong></div> : <>
            <div className="donut-wrap"><ResponsiveContainer width="100%" height={245}><PieChart><Pie data={deptData} dataKey="count" nameKey="department" innerRadius={68} outerRadius={98} paddingAngle={3} stroke="var(--bg-card)" strokeWidth={3}>{deptData.map((entry, index) => <Cell key={entry.department} fill={palette[index % palette.length]} />)}</Pie><Tooltip content={<ChartTooltip />} /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{stats?.total_employees || 0}</strong><span>Employees</span></div></div>
            <div className="department-legend">{deptData.map((item, index) => <div key={item.department}><i style={{ background: palette[index % palette.length] }} /><span>{item.department}</span><strong>{item.count}</strong></div>)}</div>
          </>}
        </section>
      </div>

      <section className="card classic-table-card">
        <div className="classic-card-heading"><div><span className="eyebrow">NEW TEAM MEMBERS</span><h3>Recently Added Employees</h3><p>The latest profiles added to your workforce</p></div><Link to="/admin/employees" className="classic-button">View all employees</Link></div>
        <div className="table-responsive"><table className="table classic-table"><thead><tr><th>Employee</th><th>Employee ID</th><th>Contact</th><th>Position</th><th>Status</th></tr></thead><tbody>
          {!recentEmployees.length ? <tr><td colSpan={5} className="text-center">No employees found</td></tr> : recentEmployees.map((employee) => <tr key={employee.id}><td><div className="employee-cell"><span>{employee.full_name?.charAt(0)}</span><div><strong>{employee.full_name}</strong><small>GLOBALCO team member</small></div></div></td><td><code>{employee.employee_id}</code></td><td>{employee.email}</td><td>{employee.position || 'Not assigned'}</td><td><span className={`status-pill ${employee.status === 'active' ? 'approved' : 'pending'}`}><i />{employee.status}</span></td></tr>)}
        </tbody></table></div>
      </section>
    </div>
  )
}
