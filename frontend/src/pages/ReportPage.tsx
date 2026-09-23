import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Download, FileText, Lightbulb, MessageSquareText, ShieldCheck } from 'lucide-react'
import { api } from '../api'
import { ScoreRing } from '../components/ScoreRing'
import type { Session } from '../types'

export function ReportPage() {
  const { sessionId = '' } = useParams()
  const [session, setSession] = useState<Session | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { api.session(sessionId).then(setSession).catch(e => setError(e instanceof Error ? e.message : 'Unable to load report')) }, [sessionId])
  const evaluated = useMemo(() => session?.responses?.filter(r => r.evaluation) ?? [], [session])
  const metrics = session ? [
    ['Technical', evaluated.reduce((a, r) => a + (r.evaluation?.technical_score ?? 0), 0) / Math.max(1, evaluated.length)],
    ['Problem solving', evaluated.reduce((a, r) => a + (r.evaluation?.problem_solving_score ?? 0), 0) / Math.max(1, evaluated.length)],
    ['Communication', evaluated.reduce((a, r) => a + (r.evaluation?.communication_score ?? 0), 0) / Math.max(1, evaluated.length)],
    ['Confidence', evaluated.reduce((a, r) => a + (r.evaluation?.confidence_score ?? 0), 0) / Math.max(1, evaluated.length)],
  ] as const : []
  if (error) return <div className="page"><div className="alert error">{error}</div></div>
  if (!session) return <div className="page centered">Loading report…</div>
  return <div className="page">
    <header className="page-head"><div><Link className="back-link" to="/"> <ArrowLeft size={15}/> Back to dashboard</Link><p className="eyebrow">EVALUATION REPORT</p><h1>{session.candidate_name}</h1><p className="subtitle">{session.interview_title} · rubric: {session.rubric_name}</p></div><div className="head-actions"><a className="btn secondary" href={api.reportUrl(session.id)} target="_blank" rel="noreferrer"><Download size={16}/> Download PDF</a></div></header>
    <section className="report-hero panel"><div><div className="status-line"><span className="pill neutral">{session.status}</span><span className="model-badge">Model: {evaluated[0]?.evaluation?.model_name ?? '—'}</span></div><h2>Evidence summary</h2><p>AI outputs are structured and validated before storage. Confidence and sentiment are supplementary signals.</p></div><ScoreRing score={session.overall_score} label="Overall"/><div className={`decision ${session.recommendation?.toLowerCase()}`}>{session.recommendation ?? 'Pending'}</div></section>
    <section className="score-grid panel"><h2>Skill dimensions</h2><div className="dimension-grid">{metrics.map(([label, value]) => <div className="dimension" key={label}><span>{label}</span><strong>{Math.round(value)}</strong><div className="bar"><i style={{ width: `${value}%` }}/></div></div>)}</div></section>
    <section className="report-layout"><div className="panel"><div className="panel-head"><div><h2>Question-by-question evidence</h2><p>Transcript + rubric-aligned evaluation.</p></div></div>{session.responses?.map((r, i) => <article className="response-card" key={r.id}><div className="response-head"><span>Q{i + 1}</span><strong>{session.questions.find(q => q.id === r.question_id)?.prompt}</strong><span className={`pill ${r.evaluation?.recommendation?.toLowerCase() ?? 'muted'}`}>{r.evaluation?.overall_score ? `${Math.round(r.evaluation.overall_score)}/100` : 'Pending'}</span></div><div className="transcript"><MessageSquareText size={16}/><div><label>Transcript</label><p>{r.transcript}</p></div></div>{r.evaluation && <><div className="insight-grid"><div><label>Strengths</label><ul>{r.evaluation.strengths.map(x => <li key={x}>{x}</li>)}</ul></div><div><label>Improve</label><ul>{r.evaluation.improvements.map(x => <li key={x}>{x}</li>)}</ul></div></div><div className="nlp-strip"><span>Sentiment: <b>{r.evaluation.sentiment}</b></span><span>Keywords: <b>{r.evaluation.nlp.keywords.slice(0,5).join(', ') || '—'}</b></span><span>Confidence heuristic: <b>{Math.round(r.evaluation.nlp.confidence_score)}</b></span></div></>}</article>)}</div><aside className="panel"><h2>Review guidance</h2><div className="guidance"><Lightbulb size={18}/><div><strong>Use evidence, not proxies</strong><p>Review transcript content against the configured rubric. Do not infer protected characteristics or use accent as a competence signal.</p></div></div><div className="guidance"><ShieldCheck size={18}/><div><strong>Human review required</strong><p>HireIQ is decision support. A hiring manager should validate the evidence and context before making an employment decision.</p></div></div><div className="guidance"><FileText size={18}/><div><strong>PDF ready</strong><p>The ReportLab generator includes a radar chart, transcripts, per-question scores, and the ethics note.</p></div></div></aside></section>
  </div>
}
