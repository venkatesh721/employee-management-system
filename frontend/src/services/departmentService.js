import api from './api'

export const getDepartments = () => api.get('/departments')

export const normalizeDepartments = (response) => {
  const payload = response?.data ?? response
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.items)) return payload.items
  if (Array.isArray(payload?.departments)) return payload.departments
  return []
}

export const getDepartment = (id) => api.get(`/departments/${id}`)
export const createDepartment = (data) => api.post('/departments', data)
export const updateDepartment = (id, data) => api.put(`/departments/${id}`, data)
export const deleteDepartment = (id) => api.delete(`/departments/${id}`)
