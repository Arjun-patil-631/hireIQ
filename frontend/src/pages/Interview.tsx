import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { CheckCircle2, CircleStop, Mic, RotateCcw, Timer, UploadCloud, Volume2 } from 'lucide-react'
import { api, getCurrentQuestion } from '../api'
import type { Session } from '../types'

export function Interview() {
  const { sessionId = '' } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState<Session | null>(null)
  const [recording, setRecording] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [blob, setBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunks = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)

  useEffect(() => { api.session(sessionId).then(setSession).catch(e => setError(e instanceof Error ? e.message : 'Could not load session')) }, [sessionId])
  useEffect(() => () => { if (timerRef.current) window.clearInterval(timerRef.current) }, [])

  function startTimer() {
    timerRef.current = window.setInterval(() => setSeconds(s => s + 1), 1000)
  }
  function stopTimer() { if (timerRef.current) window.clearInterval(timerRef.current); timerRef.current = null }

  async function startRecording() {
    setError(''); setBlob(null); setAudioUrl(null); setSeconds(0); chunks.current = []
    if (!navigator.mediaDevices?.getUserMedia) { setError('This browser does not expose MediaRecorder. Try Chrome/Edge over localhost or HTTPS.'); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      mediaRef.current = recorder
      recorder.ondataavailable = e => { if (e.data.size) chunks.current.push(e.data) }
      recorder.onstop = () => {
        const audio = new Blob(chunks.current, { type: recorder.mimeType || 'audio/webm' })
        setBlob(audio)
        setAudioUrl(URL.createObjectURL(audio))
        stream.getTracks().forEach(t => t.stop())
      }
      recorder.start(250)
      setRecording(true); startTimer()
    } catch (e) { setError(e instanceof Error ? e.message : 'Microphone permission failed') }
  }

  function stopRecording() { mediaRef.current?.stop(); setRecording(false); stopTimer() }

  async function submit() {
    if (!session || !blob) return
    const question = getCurrentQuestion(session)
    if (!question) return
    setProcessing(true); setMessage('Audio queued — Whisper + NLP + LLM evaluation running…'); setError('')
    try {
      const job = await api.submitAudio(session.id, question.id, blob)
      for (let attempt = 0; attempt < 180; attempt++) {
        const status = await api.job(job.id)
        if (status.status === 'completed') {
          const updated = await api.session(session.id)
          setSession(updated); setBlob(null); setSeconds(0); setMessage('Answer evaluated successfully.')
          if (updated.status === 'completed') { setTimeout(() => navigate(`/report/${updated.id}`), 700) }
          break
        }
        if (status.status === 'failed') throw new Error(status.error_message || 'Processing failed')
        await new Promise(r => window.setTimeout(r, 1500))
      }
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not process answer') }
    finally { setProcessing(false) }
  }

  if (!session) return <div className="page centered">{error ? <div className="alert error">{error}</div> : <div className="loading-card">Loading interview…</div>}</div>
  const question = getCurrentQuestion(session)
  const complete = session.status === 'completed' || !question
  const mins = String(Math.floor(seconds / 60)).padStart(2, '0'), secs = String(seconds % 60).padStart(2, '0')

  return <div className="page interview-page">
    <header className="page-head compact"><div><p className="eyebrow">CANDIDATE SESSION</p><h1>{session.interview_title}</h1><p className="subtitle">Candidate: {session.candidate_name}</p></div><div className="progress-chip">{Math.min(session.completed_questions + (blob ? 1 : 0), session.questions.length)} / {session.questions.length}</div></header>
    <div className="interview-grid">
      <section className="panel question-card">
        <div className="question-meta"><span className="pill neutral">Question {session.current_question_index + 1}</span><span className="question-type">{question?.question_type ?? 'complete'}</span></div>
        {complete ? <div className="complete-state"><CheckCircle2 size={42}/><h2>Interview complete</h2><p>Your evaluation report is ready.</p><button className="btn primary" onClick={() => navigate(`/report/${session.id}`)}>Open report</button></div> : <>
          <h2 className="question-text">{question.prompt}</h2>
          <div className="timer"><Timer size={17}/><strong>{mins}:{secs}</strong><span>recording timer</span></div>
          <div className="record-area">
            {!recording ? <button className="record-button" disabled={processing} onClick={() => void startRecording()}><Mic size={28}/><span>Start recording</span><small>Browser microphone</small></button> : <button className="record-button recording" onClick={stopRecording}><CircleStop size={28}/><span>Stop recording</span><small>Speak clearly — no accent scoring</small></button>}
            <div className="audio-hint"><Volume2 size={16}/><span>Tip: explain your reasoning and include a concrete example.</span></div>
          </div>
          {blob && !processing && (
            <div className="ready-box" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}><UploadCloud size={17}/> Answer captured ({Math.max(1, Math.round(seconds))}s)</span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn secondary" onClick={() => void startRecording()}><RotateCcw size={15}/> Re-record</button>
                  <button className="btn primary" onClick={() => void submit()}>Submit & evaluate</button>
                </div>
              </div>
              {audioUrl && <audio controls src={audioUrl} style={{ width: '100%', height: '36px' }} />}
            </div>
          )}
          {processing && <div className="processing-box"><div className="spinner"/><div><strong>AI evaluation in progress</strong><span>{message}</span></div></div>}
          {message && !processing && <div className="success-note"><CheckCircle2 size={16}/>{message}</div>}
          {error && <div className="alert error">{error}</div>}
        </>}
      </section>
      <aside className="panel side-card"><h3>Session flow</h3><div className="step-list">{session.questions.map((q, idx) => <div className={idx < session.completed_questions ? 'step done' : idx === session.current_question_index ? 'step current' : 'step'} key={q.id}><span>{idx < session.completed_questions ? '✓' : idx + 1}</span><div><strong>Q{idx + 1}</strong><small>{q.question_type}</small></div></div>)}</div><div className="ethics-card"><ShieldIcon/><strong>Evidence-first evaluation</strong><p>Scores are based on answer content and the configured rubric. Demographic traits and accent are excluded.</p></div></aside>
    </div>
  </div>
}

function ShieldIcon() { return <span className="shield-mini">✓</span> }
