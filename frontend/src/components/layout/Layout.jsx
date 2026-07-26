import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

const pageTitles = {
  '/admin/dashboard': 'Admin Dashboard',
  '/admin/employees': 'Employees',
  '/admin/employees/new': 'Add Employee Account',
  '/admin/departments': 'Departments',
  '/admin/attendance': 'Attendance',
  '/admin/payroll': 'Payroll',
  '/admin/leaves': 'Leave Requests',
  '/admin/ai-assistant': 'AI Assistant',
  '/admin/insights': 'Workforce Insights',
  '/admin/audit-logs': 'System Activity',
  '/admin/profile': 'Profile',
  '/employee/dashboard': 'Employee Dashboard',
  '/employee/attendance': 'My Attendance',
  '/employee/salary': 'My Salary',
  '/employee/leaves': 'My Leave',
  '/employee/profile': 'My Profile',
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const getTitle = () => {
    const match = Object.keys(pageTitles).find((key) => {
      if (key.includes(':id')) {
        const pattern = key.replace(':id', '[^/]+')
        return new RegExp(`^${pattern}$`).test(location.pathname)
      }
      return location.pathname === key
    })
    if (match) {
      if (location.pathname.includes('/edit')) return 'Edit Employee'
      return pageTitles[match]
    }
    return 'Dashboard'
  }

  return (
    <div className="app-layout">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="main-wrapper">
        <Navbar title={getTitle()} onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
