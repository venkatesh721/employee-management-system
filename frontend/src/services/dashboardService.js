import api from './api'

export const getStats = () => api.get('/dashboard/stats')
export const getAttendanceChart = () => api.get('/dashboard/attendance-chart')
export const getDepartmentDistribution = () => api.get('/dashboard/department-distribution')
export const getRecentEmployees = () => api.get('/dashboard/recent-employees')
