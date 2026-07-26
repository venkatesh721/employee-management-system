import api from './api'

export const generateWorkforceInsights = (focus) =>
  api.post('/insights/workforce', { focus })

export const getAuditLogs = () => api.get('/audit-logs')
