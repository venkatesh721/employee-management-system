import api from './api'

export const getDepartments = () => api.get('/departments')

export const normalizeDepartments = (response) => {
  const payload = response?.data ?? response
  const departments = Array.isArray(payload)
    ? payload
    : [payload?.items, payload?.departments, payload?.results, payload?.data]
        .find(Array.isArray)

  if (!departments) {
    throw new TypeError('Unexpected departments API response structure')
  }
  if (
    departments.some(
      (department) =>
        !department ||
        typeof department.id !== 'string' ||
        typeof department.name !== 'string',
    )
  ) {
    throw new TypeError('Departments API returned an invalid department')
  }
  return departments
}

export const getDepartment = (id) => api.get(`/departments/${id}`)
export const createDepartment = (data) => api.post('/departments', data)
export const updateDepartment = (id, data) => api.put(`/departments/${id}`, data)
export const deleteDepartment = (id) => api.delete(`/departments/${id}`)
