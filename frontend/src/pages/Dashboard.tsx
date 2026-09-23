import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, BarChart2, CheckCircle2, Clock3, FileText, Mic2, RefreshCw, Users, XCircle } from 'lucide-react'
import { api } from '../api'
import { ScoreRing } from '../components/ScoreRing'
import type { Candidate, CandidateComparisonItem, Summary } from '../types'

function recommendationClass(value?: string | null) {
  return value ? `pill ${value.toLowerCase()}` : 'pill muted'
}

function CandidateComparisonSection() {
  const [candidates, setCandidates] = useState<CandidateComparisonItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.compareCandidates()
      .then(res => setCandidates(res.candidates))
      .catch(() => setCandidates([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return null
  if (!candidates.length) return null

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Candidate Skill Dimension Comparison</h2>
          <p>Cross-candidate evaluation breakdown across Technical, Problem Solving, Communication, and Confidence.</p>
        </div>
        <span className="panel-count">{candidates.length} evaluated</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Overall</th>
              <th>Technical</th>
              <th>Problem Solving</th>
              <th>Communication</th>
              <th>Confidence</th>
              <th>Recommendation</th>
              <th>Report</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map(c => (
              <tr key={c.candidate_id}>
                <td>
                  <strong>{c.candidate_name}</strong>
                  <br />
                  <small style={{ color: 'var(--text-muted)' }}>{c.candidate_email}</small>
                </td>
                <td>
                  <strong>{c.overall_score != null ? `${c.overall_score}` : '—'}</strong>
                </td>
                <td>{c.technical_score != null ? `${c.technical_score}` : '—'}</td>
                <td>{c.problem_solving_score != null ? `${c.problem_solving_score}` : '—'}</td>
                <td>{c.communication_score != null ? `${c.communication_score}` : '—'}</td>
                <td>{c.confidence_score != null ? `${c.confidence_score}` : '—'}</td>
                <td>
                  <span className={recommendationClass(c.recommendation)}>
                    {c.recommendation ?? 'Pending'}
                  </span>
                </td>
                <td>
                  {c.session_id ? (
                    <Link
                      to={`/report/${c.session_id}`}
                      className="btn secondary"
                      style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem' }}
                    >
                      <FileText size={13} /> View
                    </Link>
                  ) : (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No session</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export function Dashboard() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState<Summary | null>(null)
  const [data, setData] = useState<{ total: number; items: Candidate[]; page: number } | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showStart, setShowStart] = useState(false)
  const [name, setName] = useState('Alex Sharma')
  const [email, setEmail] = useState('alex@example.com')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [s, c] = await Promise.all([api.summary(), api.candidates(page)])
      setSummary(s)
      setData({ total: c.total, items: c.items, page: c.page })
    } catch (e) { setError(e instanceof Error ? e.message : 'Failed to load dashboard') }
    finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [page])

  async function startDemo() {
    try {
      const session = await api.demoStart(name, email)
      navigate(`/interview/${session.id}`)
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not start demo') }
  }

  return <div className="page">
    <header className="page-head">
      <div><p className="eyebrow">HIRING MANAGER</p><h1>Interview Intelligence Dashboard</h1><p className="subtitle">Review evidence, compare candidates, and launch a structured AI interview.</p></div>
      <div className="head-actions"><button className="btn secondary" onClick={() => void load()}><RefreshCw size={16}/> Refresh</button><button className="btn primary" onClick={() => setShowStart(true)}><Mic2 size={16}/> Start demo interview</button></div>
    </header>

    {error && <div className="alert error">{error}</div>}

    <section className="metric-grid">
      <div className="metric"><div className="metric-icon"><Users size={17}/></div><span>Candidates</span><strong>{summary?.total_candidates ?? '—'}</strong></div>
      <div className="metric"><div className="metric-icon"><CheckCircle2 size={17}/></div><span>Completed Interviews</span><strong>{summary?.completed_interviews ?? '—'}</strong></div>
      <div className="metric"><div className="metric-icon"><Clock3 size={17}/></div><span>Average Score</span><strong>{summary ? `${summary.average_score}` : '—'}</strong></div>
      <div className="metric"><div className="metric-icon"><XCircle size={17}/></div><span>Decision Mix</span><strong>{summary ? `${summary.proceed_count}/${summary.hold_count}/${summary.reject_count}` : '—'}</strong><small>Proceed / Hold / Reject</small></div>
    </section>

    <section className="panel">
      <div className="panel-head"><div><h2>Candidate evaluations</h2><p>Paginated review list with latest evaluation evidence.</p></div><span className="panel-count">{data?.total ?? 0} total</span></div>
      {loading ? <div className="empty">Loading...</div> : <div className="table-wrap"><table><thead><tr><th>Candidate</th><th>Sessions</th><th>Latest score</th><th>Recommendation</th><th></th></tr></thead><tbody>
        {(data?.items ?? []).map(c => <tr key={c.id}><td><div className="candidate-cell"><div className="avatar">{c.name.slice(0,1).toUpperCase()}</div><div><strong>{c.name}</strong><small>{c.email}</small></div></div></td><td>{c.session_count}</td><td><div className="score-inline"><ScoreRing score={c.latest_score} label=""/><strong>{c.latest_score == null ? 'Not evaluated' : `${c.latest_score}/100`}</strong></div></td><td><span className={recommendationClass(c.latest_recommendation)}>{c.latest_recommendation ?? 'Pending'}</span></td><td className="row-action"><Link to={`/candidate/${c.id}`} className="icon-link">View <ArrowRight size={15}/></Link></td></tr>)}
      </tbody></table></div>}
      <div className="pager"><button className="btn secondary" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</button><span>Page {page}</span><button className="btn secondary" disabled={page * 8 >= (data?.total ?? 0)} onClick={() => setPage(p => p + 1)}>Next</button></div>
    </section>

    <CandidateComparisonSection />

    {showStart && <div className="modal-backdrop"><div className="modal"><div className="modal-head"><div><h2>Launch candidate interview</h2><p>Creates a demo 5-question technical/behavioral session.</p></div><button className="icon-button" onClick={() => setShowStart(false)}>×</button></div><label>Candidate name<input value={name} onChange={e => setName(e.target.value)} /></label><label>Email<input value={email} onChange={e => setEmail(e.target.value)} /></label><button className="btn primary wide" onClick={() => void startDemo()}>Open interview <ArrowRight size={16}/></button></div></div>}
  </div>
}
