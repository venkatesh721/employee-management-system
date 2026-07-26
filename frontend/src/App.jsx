import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/common/ProtectedRoute'
import Layout from './components/layout/Layout'
import Loading from './components/common/Loading'
import { useAuth } from './hooks/useAuth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import EmployeeDashboard from './pages/EmployeeDashboard'
import Employees from './pages/Employees'
import EmployeeForm from './pages/EmployeeForm'
import Departments from './pages/Departments'
import Attendance from './pages/Attendance'
import Profile from './pages/Profile'
import Insights from './pages/Insights'
import AuditLogs from './pages/AuditLogs'
import Unauthorized from './pages/Unauthorized'
import RegisterEmployee from './pages/RegisterEmployee'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Payroll from './pages/Payroll'
import Leaves from './pages/Leaves'
import AIAssistant from './pages/AIAssistant'

function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <Loading />
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'admin' ? '/admin/dashboard' : '/employee/dashboard'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register-employee" element={<RegisterEmployee />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/unauthorized" element={<Unauthorized />} />
      <Route path="/" element={<HomeRedirect />} />

      <Route
        path="/admin"
        element={<ProtectedRoute roles={['admin']}><Layout /></ProtectedRoute>}
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="employees" element={<Employees />} />
        <Route path="employees/new" element={<EmployeeForm />} />
        <Route path="employees/:id/edit" element={<EmployeeForm />} />
        <Route path="departments" element={<Departments />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="payroll" element={<Payroll />} />
        <Route path="leaves" element={<Leaves />} />
        <Route path="ai-assistant" element={<AIAssistant />} />
        <Route path="insights" element={<Insights />} />
        <Route path="audit-logs" element={<AuditLogs />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      <Route
        path="/employee"
        element={<ProtectedRoute roles={['employee']}><Layout /></ProtectedRoute>}
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<EmployeeDashboard />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="salary" element={<Payroll />} />
        <Route path="leaves" element={<Leaves />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  )
}
