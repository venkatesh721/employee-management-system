import { useCallback, useEffect, useMemo, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'

const money = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(Number(value) || 0)
const initialForm = { employee_id: '', payroll_month: new Date().toISOString().slice(0, 7) + '-01', basic_salary: '', hra: 0, allowances: 0, bonus: 0, overtime: 0, tax: 0, provident_fund: 0, insurance: 0, other_deductions: 0, status: 'draft' }
const earningFields = [['basic_salary', 'Basic salary'], ['hra', 'House rent allowance'], ['allowances', 'Allowances'], ['bonus', 'Bonus'], ['overtime', 'Overtime']]
const deductionFields = [['tax', 'Income tax'], ['provident_fund', 'Provident fund'], ['insurance', 'Insurance'], ['other_deductions', 'Other deductions']]

function MoneyField({ name, label, value, onChange, required }) {
  return <div className="form-group"><label htmlFor={`payroll-${name}`}>{label}</label><div className="money-input"><span>₹</span><input id={`payroll-${name}`} className="form-control" type="number" min="0" step="0.01" required={required} value={value} onChange={(event) => onChange(name, event.target.value)} /></div></div>
}

export default function Payroll() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'
  const [rows, setRows] = useState([])
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState(initialForm)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [payrollResponse, employeeResponse] = await Promise.all([api.get('/payroll'), ...(isAdmin ? [api.get('/employees', { params: { size: 100 } })] : [])])
      setRows(Array.isArray(payrollResponse.data) ? payrollResponse.data : [])
      if (employeeResponse) setEmployees(employeeResponse.data?.items || [])
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load payroll')
    } finally {
      setLoading(false)
    }
  }, [isAdmin])

  useEffect(() => { load() }, [load])
  const updateField = (name, value) => setForm((current) => ({ ...current, [name]: value }))
  const totals = useMemo(() => {
    const gross = earningFields.reduce((sum, [name]) => sum + (Number(form[name]) || 0), 0)
    const deductions = deductionFields.reduce((sum, [name]) => sum + (Number(form[name]) || 0), 0)
    return { gross, deductions, net: gross - deductions }
  }, [form])
  const recordsTotal = rows.reduce((sum, row) => sum + Number(row.net_salary || 0), 0)

  const submit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/payroll', form)
      toast.success('Monthly payroll generated')
      setForm(initialForm)
      load()
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Payroll generation failed')
    } finally {
      setSubmitting(false)
    }
  }

  const download = async (id) => {
    try {
      const response = await api.get(`/payroll/${id}/payslip`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'GLOBALCO-payslip.pdf'
      anchor.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Payslip download failed')
    }
  }

  return <div className="page-container payroll-page">
    <section className="payroll-hero"><div><span className="eyebrow">FINANCE & COMPENSATION</span><h2>{isAdmin ? 'Payroll Management' : 'Salary & Payslips'}</h2><p>{isAdmin ? 'Generate accurate monthly compensation and maintain a clear payment trail.' : 'Review your monthly earnings, deductions, and downloadable payslips.'}</p></div><div className="payroll-hero-total"><span>{isAdmin ? 'Records value' : 'Salary received'}</span><strong>{money(recordsTotal)}</strong><small>{rows.length} payroll records</small></div></section>

    {isAdmin && <form className="card payroll-form-card" onSubmit={submit}>
      <div className="classic-card-heading"><div><span className="eyebrow">NEW PAYROLL</span><h3>Generate Monthly Payroll</h3><p>Select an employee, enter compensation, and review the calculated net salary.</p></div><span className="secure-chip">Secure calculation</span></div>
      <div className="payroll-primary-grid">
        <div className="form-group"><label htmlFor="payroll-employee">Employee</label><select id="payroll-employee" className="form-control" required value={form.employee_id} onChange={(event) => updateField('employee_id', event.target.value)}><option value="">Choose an employee</option>{employees.map((employee) => <option key={employee.id} value={employee.id}>{employee.employee_id} — {employee.first_name} {employee.last_name}</option>)}</select></div>
        <div className="form-group"><label htmlFor="payroll-month">Payroll month</label><input id="payroll-month" className="form-control" type="month" required value={form.payroll_month.slice(0, 7)} onChange={(event) => updateField('payroll_month', `${event.target.value}-01`)} /></div>
        <div className="form-group"><label htmlFor="payroll-status">Initial status</label><select id="payroll-status" className="form-control" value={form.status} onChange={(event) => updateField('status', event.target.value)}>{['draft', 'processed', 'paid', 'cancelled'].map((status) => <option key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>)}</select></div>
      </div>
      <div className="payroll-money-sections">
        <fieldset><legend><span>+</span>Earnings</legend><div className="payroll-field-grid">{earningFields.map(([name, label]) => <MoneyField key={name} name={name} label={label} value={form[name]} onChange={updateField} required={name === 'basic_salary'} />)}</div></fieldset>
        <fieldset><legend><span>−</span>Deductions</legend><div className="payroll-field-grid">{deductionFields.map(([name, label]) => <MoneyField key={name} name={name} label={label} value={form[name]} onChange={updateField} />)}</div></fieldset>
      </div>
      <div className="payroll-calculation"><div><span>Gross earnings</span><strong>{money(totals.gross)}</strong></div><div className="deduction-total"><span>Total deductions</span><strong>− {money(totals.deductions)}</strong></div><div className="net-total"><span>Net salary</span><strong>{money(totals.net)}</strong></div><button className="btn btn-primary" disabled={submitting}>{submitting ? 'Generating…' : 'Generate Payroll'}</button></div>
    </form>}

    <section className="card payroll-records-card">
      <div className="classic-card-heading"><div><span className="eyebrow">PAYMENT HISTORY</span><h3>{isAdmin ? 'Payroll Records' : 'My Salary History'}</h3><p>Monthly gross earnings, deductions, net pay, and payment status.</p></div><span className="record-count">{rows.length} records</span></div>
      <div className="table-responsive"><table className="table payroll-table"><thead><tr><th>Payroll month</th><th>Gross earnings</th><th>Deductions</th><th>Net salary</th><th>Status</th><th>Payslip</th></tr></thead><tbody>{loading ? <tr><td colSpan="6" className="text-center">Loading salary history…</td></tr> : !rows.length ? <tr><td colSpan="6"><div className="polished-empty"><span>₹</span><strong>No payroll records</strong><p>Generated payroll will appear here.</p></div></td></tr> : rows.map((row) => <tr key={row.id}><td><div className="month-cell"><strong>{new Date(`${row.payroll_month}T00:00:00`).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</strong><small>Monthly payroll</small></div></td><td>{money(row.gross_salary)}</td><td className="deduction-value">− {money(row.total_deductions)}</td><td className="net-value">{money(row.net_salary)}</td><td><span className={`payroll-status ${row.status}`}>{row.status}</span></td><td><button className="payslip-button" onClick={() => download(row.id)}>↓ Download PDF</button></td></tr>)}</tbody></table></div>
    </section>
  </div>
}
