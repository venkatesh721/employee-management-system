import api from './api'

export const getDepartments = () =>
  api.get('/departments', {
    // Department choices must reflect records just created on the management
    // page. The timestamp also prevents intermediary/CDN caches from serving
    // an earlier empty list in production.
    params: { _fresh: Date.now() },
    headers: {
      'Cache-Control': 'no-cache',
      Pragma: 'no-cache',
    },
  })

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
