import api from './api'

export const login = (identifier, password, role) =>
  api.post('/auth/login', { identifier, password, role })
export const registerEmployee = (data) => api.post('/auth/register-employee', data)
export const forgotPassword = (email) => api.post('/auth/forgot-password', { email })
export const resetPassword = (data) => api.post('/auth/reset-password', data)
export const logoutApi = () => api.post('/auth/logout')
export const getProfile = () => api.get('/auth/me')
export const updateProfile = (data) => api.put('/auth/me', data)
