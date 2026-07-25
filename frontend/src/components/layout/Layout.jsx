import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

const pageTitles = {
  '/': 'Dashboard',
  '/employees': 'Employees',
  '/employees/new': 'Add Employee',
  '/departments': 'Departments',
  '/attendance': 'Attendance',
  '/profile': 'Profile',
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
