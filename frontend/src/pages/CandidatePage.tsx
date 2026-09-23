import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Calendar, CheckCircle2, FileText, Play } from 'lucide-react'
import { api } from '../api'
import type { CandidateDetail } from '../types'

export function CandidatePage() {
  const { candidateId = '' } = useParams()
  const [candidate, setCandidate] = useState<CandidateDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.candidateDetail(candidateId).then(setCandidate).catch(e => setError(e instanceof Error ? e.message : 'Failed to load'))
  }, [candidateId])

  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  if (!candidate) return <div className="page centered">Loading candidate…</div>

  return (
    <div className="page">
      <Link className="back-link" to="/"><ArrowLeft size={15}/> Back to dashboard</Link>
      <section className="candidate-hero panel">
        <div className="avatar large">{candidate.name.slice(0,1).toUpperCase()}</div>
        <div>
          <p className="eyebrow">CANDIDATE PROFILE</p>
          <h1>{candidate.name}</h1>
          <p>{candidate.email}</p>
        </div>
        <div className="candidate-summary">
          <strong>{candidate.latest_score != null ? `${candidate.latest_score}/100` : '—'}</strong>
          <span>latest score</span>
        </div>
        <span className={`pill ${candidate.latest_recommendation?.toLowerCase() ?? 'muted'}`}>{candidate.latest_recommendation ?? 'Pending'}</span>
      </section>

      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Interview Sessions</h2>
            <p>{candidate.sessions?.length ?? 0} session(s) recorded for this candidate.</p>
          </div>
          <Link to="/" className="icon-link">Dashboard <ArrowRight size={15}/></Link>
        </div>

        {(!candidate.sessions || candidate.sessions.length === 0) ? (
          <div className="empty">No interview sessions found for this candidate.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Interview</th>
                  <th>Rubric</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Recommendation</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {candidate.sessions.map(s => (
                  <tr key={s.id}>
                    <td><strong>{s.interview_title}</strong></td>
                    <td><span className="pill neutral">{s.rubric_name}</span></td>
                    <td><span className={`pill ${s.status === 'completed' ? 'proceed' : 'neutral'}`}>{s.status}</span></td>
                    <td><strong>{s.overall_score != null ? `${s.overall_score}/100` : '—'}</strong></td>
                    <td><span className={`pill ${s.recommendation?.toLowerCase() ?? 'muted'}`}>{s.recommendation ?? 'Pending'}</span></td>
                    <td><small>{new Date(s.started_at).toLocaleDateString()}</small></td>
                    <td>
                      {s.status === 'completed' ? (
                        <Link to={`/report/${s.id}`} className="btn secondary" style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                          <FileText size={14}/> Report
                        </Link>
                      ) : (
                        <Link to={`/interview/${s.id}`} className="btn primary" style={{ fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                          <Play size={14}/> Continue
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

