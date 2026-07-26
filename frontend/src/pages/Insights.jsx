import { useState } from 'react'
import { generateWorkforceInsights } from '../services/insightService'
import toast from 'react-hot-toast'

export default function Insights() {
  const [focus, setFocus] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const generate = async (event) => {
    event.preventDefault()
    setLoading(true)
    try {
      const response = await generateWorkforceInsights(focus.trim())
      setResult(response.data)
      toast.success('Workforce insights generated')
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unable to generate insights')
    } finally {
      setLoading(false)
    }
  }

  const metrics = result?.metrics
  const attendanceRate = metrics?.attendance_records ? Math.round((metrics.present_records / metrics.attendance_records) * 100) : 0
  const activeEmployees = metrics ? metrics.total_employees - metrics.inactive_employees : 0

  return <div className="page-container insights-page">
    <section className="insights-hero"><div><span className="eyebrow">AI-ASSISTED DECISION SUPPORT</span><h2>Workforce Insights</h2><p>Turn current workforce and attendance metrics into clear, reviewable recommendations.</p></div><div className="insight-shield"><span>✦</span><div><strong>Human-reviewed</strong><small>Advisory insights only</small></div></div></section>

    <section className="card insight-prompt-card">
      <div className="classic-card-heading"><div><span className="eyebrow">ANALYSIS BRIEF</span><h3>What would you like to understand?</h3><p>Describe a business concern or leave blank for a general workforce-health review.</p></div></div>
      <form onSubmit={generate}>
        <div className="insight-textarea-wrap"><textarea id="business-focus" className="form-control" maxLength={300} rows="4" value={focus} onChange={(event) => setFocus(event.target.value)} placeholder="For example: Review attendance risk, repeated late arrivals, and workforce capacity…" /><span>{focus.length}/300</span></div>
        <div className="focus-suggestions"><span>Suggested focus:</span>{['Attendance risk', 'Workforce capacity', 'Late-arrival patterns'].map((item) => <button type="button" key={item} onClick={() => setFocus(item)}>{item}</button>)}</div>
        <button className="classic-generate-button" disabled={loading}><span>{loading ? '◌' : '✦'}</span>{loading ? 'Analysing workforce…' : 'Generate Workforce Insights'}</button>
      </form>
    </section>

    {result ? <>
      <div className="insight-metrics-grid">
        <article><span>Total employees</span><strong>{metrics?.total_employees || 0}</strong><small>Current workforce</small></article>
        <article><span>Active employees</span><strong>{activeEmployees}</strong><small>Available workforce</small></article>
        <article><span>Attendance rate</span><strong>{attendanceRate}%</strong><small>Last {metrics?.period_days || 30} days</small></article>
        <article><span>Records analysed</span><strong>{metrics?.attendance_records || 0}</strong><small>Attendance entries</small></article>
      </div>
      <section className="card insight-results-card">
        <div className="classic-card-heading"><div><span className="eyebrow">RECOMMENDATIONS</span><h3>Workforce Observations</h3><p>Use these findings as decision support and confirm context with HR teams.</p></div><span className={`insight-source ${result.source === 'ai' ? 'ai' : 'rules'}`}>{result.source === 'ai' ? '✦ AI generated' : '✓ Rules-based analysis'}</span></div>
        <div className="recommendation-list">{result.insights.map((item, index) => <article key={item}><span>{String(index + 1).padStart(2, '0')}</span><div><strong>{index === result.insights.length - 1 ? 'Recommended action' : 'Workforce observation'}</strong><p>{item}</p></div></article>)}</div>
        <div className="insight-notice"><span>i</span><p><strong>Decision-support notice:</strong> These insights identify patterns, not disciplinary conclusions. Review individual context before taking action.</p></div>
      </section>
    </> : <section className="insight-empty"><span>✦</span><h3>Your analysis will appear here</h3><p>Generate insights to view workforce metrics and structured recommendations.</p></section>}
  </div>
}
