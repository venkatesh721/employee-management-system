import api from './api'

export const getAttendance = (params) => api.get('/attendance', { params })
export const checkIn = (data) => api.post('/attendance', data)
export const checkOut = (id) => api.put(`/attendance/${id}`)
export const getTodayAttendance = () => api.get('/attendance/today')
export const getAttendanceSummary = (params) => api.get('/attendance/summary', { params })
