import { useCallback, useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import Loading from '../components/common/Loading'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'

const empty = { employee_id: '', date: new Date().toISOString().slice(0, 10), check_in: '', check_out: '', status: 'present', notes: '' }
export default function Attendance() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [records,setRecords]=useState([]), [summary,setSummary]=useState({}), [employees,setEmployees]=useState([])
  const [loading,setLoading]=useState(true), [form,setForm]=useState(empty), [dateFrom,setDateFrom]=useState(''), [dateTo,setDateTo]=useState('')
  const load=useCallback(async()=>{
    setLoading(true)
    try {
      const params={size:100}; if(dateFrom)params.date_from=dateFrom;if(dateTo)params.date_to=dateTo
      const requests=[api.get('/attendance',{params}),api.get('/attendance/summary',{params:{period:'monthly'}})]
      if(isAdmin)requests.push(api.get('/employees',{params:{size:100}}))
      const [list,sum,emps]=await Promise.all(requests)
      setRecords(list.data.items);setSummary(sum.data);if(emps)setEmployees(emps.data.items)
    } catch(e){toast.error(e.response?.data?.detail||'Failed to load attendance')} finally{setLoading(false)}
  },[dateFrom,dateTo,isAdmin])
  useEffect(()=>{load()},[load])
  const submit=async(e)=>{
    e.preventDefault()
    try {
      const payload={...form,check_in:form.check_in?`${form.date}T${form.check_in}:00`:null,check_out:form.check_out?`${form.date}T${form.check_out}:00`:null}
      await api.post('/attendance',payload);toast.success('Attendance saved');setForm(empty);load()
    } catch(err){toast.error(err.response?.data?.detail||'Unable to save attendance')}
  }
  if(loading&&!records.length)return <Loading/>
  const cards=[['Present','present','#22c55e'],['Absent','absent','#ef4444'],['Late','late','#f59e0b'],['Half Day','half_day','#8b5cf6'],['On Leave','on_leave','#64748b']]
  return <div className={`page-container management-page attendance-page ${isAdmin ? 'admin-attendance' : 'employee-attendance'}`}>
    <div className="attendance-summary">{cards.map(([label,key,color])=><div className="summary-card" key={key}><span className="summary-label">{label}</span><span className="summary-value" style={{color}}>{summary[key]||0}</span></div>)}</div>
    {isAdmin&&<div className="card"><div className="card-header"><h3>Record Attendance</h3><span className="text-muted">Administrator-only entry</span></div>
      <form className="form-grid" onSubmit={submit}>
        <div className="form-group"><label>Employee</label><select required value={form.employee_id} onChange={e=>setForm({...form,employee_id:e.target.value})}><option value="">Select employee</option>{employees.map(x=><option key={x.id} value={x.id}>{x.employee_id} — {x.first_name} {x.last_name}</option>)}</select></div>
        <div className="form-group"><label>Date</label><input type="date" required value={form.date} onChange={e=>setForm({...form,date:e.target.value})}/></div>
        <div className="form-group"><label>Check in</label><input type="time" value={form.check_in} onChange={e=>setForm({...form,check_in:e.target.value})}/></div>
        <div className="form-group"><label>Check out</label><input type="time" value={form.check_out} onChange={e=>setForm({...form,check_out:e.target.value})}/></div>
        <div className="form-group"><label>Status</label><select value={form.status} onChange={e=>setForm({...form,status:e.target.value})}>{cards.map(([label,key])=><option key={key} value={key}>{label}</option>)}</select></div>
        <div className="form-group"><label>Notes</label><input value={form.notes} onChange={e=>setForm({...form,notes:e.target.value})}/></div>
        <button className="btn btn-primary" type="submit">Save Attendance</button>
      </form></div>}
    <div className="card"><div className="card-header"><h3>{isAdmin?'Attendance Management':'My Attendance History'}</h3>{!isAdmin&&<span className="text-muted">Read-only personal records</span>}</div>
      <div className="search-filters"><input type="date" value={dateFrom} onChange={e=>setDateFrom(e.target.value)}/><input type="date" value={dateTo} onChange={e=>setDateTo(e.target.value)}/></div>
      <div className="table-responsive"><table className="table"><thead><tr>{isAdmin&&<th>Employee</th>}<th>Date</th><th>Check In</th><th>Check Out</th><th>Hours</th><th>Status</th><th>Notes</th></tr></thead><tbody>
        {!records.length?<tr><td colSpan={isAdmin?7:6} className="text-center">No attendance records found</td></tr>:records.map(r=><tr key={r.id}>{isAdmin&&<td>{r.employee_name||r.employee_id}</td>}<td>{r.date}</td><td>{r.check_in?new Date(r.check_in).toLocaleTimeString():'—'}</td><td>{r.check_out?new Date(r.check_out).toLocaleTimeString():'—'}</td><td>{r.working_hours?.toFixed?.(2)||'0.00'}</td><td><span className={`badge badge-${r.status}`}>{r.status.replace('_',' ')}</span></td><td>{r.notes||'—'}</td></tr>)}
      </tbody></table></div></div>
  </div>
}
