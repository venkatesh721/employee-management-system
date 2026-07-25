import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { getStats, getAttendanceChart, getDepartmentDistribution, getRecentEmployees } from '../services/dashboardService'
import { DEPARTMENT_COLORS } from '../utils/constants'
import Loading from '../components/common/Loading'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [chartData, setChartData] = useState([])
  const [deptData, setDeptData] = useState([])
  const [recentEmployees, setRecentEmployees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, chartRes, deptRes, recentRes] = await Promise.all([
          getStats(),
          getAttendanceChart(),
          getDepartmentDistribution(),
          getRecentEmployees(),
        ])
        setStats(statsRes.data)
        setChartData(chartRes.data || [])
        setDeptData(deptRes.data || [])
        setRecentEmployees(recentRes.data || [])
      } catch {
        setStats({ total_employees: 0, active_employees: 0, departments: 0, today_attendance: 0 })
        setChartData([])
        setDeptData([])
        setRecentEmployees([])
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <Loading />

  const statCards = [
    { label: 'Total Employees', value: stats?.total_employees || 0, color: '#4f46e5', icon: '👥' },
    { label: 'Active Employees', value: stats?.active_employees || 0, color: '#22c55e', icon: '✅' },
    { label: 'Departments', value: stats?.departments || 0, color: '#f59e0b', icon: '🏢' },
    { label: "Today's Attendance", value: stats?.today_attendance || 0, color: '#06b6d4', icon: '📋' },
  ]

  return (
    <div className="dashboard">
      <div className="stats-grid">
        {statCards.map((card) => (
          <div key={card.label} className="stat-card" style={{ '--accent': card.color }}>
            <div className="stat-icon">{card.icon}</div>
            <div className="stat-info">
              <span className="stat-value">{card.value}</span>
              <span className="stat-label">{card.label}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="charts-grid">
        <div className="card chart-card">
          <h3>Attendance (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <h3>Department Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={deptData}
                dataKey="count"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {deptData.map((entry) => (
                  <Cell key={entry.name} fill={DEPARTMENT_COLORS[entry.name] || '#64748b'} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Recent Employees</h3>
          <Link to="/employees" className="btn btn-outline btn-sm">View All</Link>
        </div>
        <div className="table-responsive">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentEmployees.length === 0 ? (
                <tr><td colSpan={4} className="text-center">No employees found</td></tr>
              ) : (
                recentEmployees.map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.first_name} {emp.last_name}</td>
                    <td>{emp.email}</td>
                    <td>{emp.department_name || emp.department || '-'}</td>
                    <td><span className={`badge badge-${emp.status}`}>{emp.status}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
