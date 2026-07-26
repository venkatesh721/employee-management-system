import { useEffect, useState } from 'react'
import { getAuditLogs } from '../services/insightService'
import Loading from '../components/common/Loading'
import toast from 'react-hot-toast'

export default function AuditLogs() {
  const [logs, setLogs] = useState(null)
  useEffect(() => {
    getAuditLogs().then((response) => setLogs(response.data)).catch(() => toast.error('Failed to load audit logs'))
  }, [])
  if (!logs) return <Loading />
  return (
    <div className="page-container management-page audit-page">
      <div className="page-header"><h2>System Activity</h2></div>
      <div className="card table-responsive">
        <table className="table">
          <thead><tr><th>Time</th><th>Action</th><th>Resource</th><th>Resource ID</th></tr></thead>
          <tbody>
            {logs.length === 0
              ? <tr><td colSpan={4} className="text-center">No activity recorded yet</td></tr>
              : logs.map((log) => <tr key={log.id}><td>{new Date(log.created_at).toLocaleString()}</td><td>{log.action}</td><td>{log.resource_type}</td><td>{log.resource_id || '—'}</td></tr>)}
          </tbody>
        </table>
      </div>
    </div>
  )
}
