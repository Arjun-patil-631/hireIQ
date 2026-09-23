import { useEffect, useState } from 'react'
import { Plus, Save, ShieldCheck, Trash2 } from 'lucide-react'
import { api } from '../api'
import type { Question } from '../types'

export function Rubrics() {
  const [name, setName] = useState('technical')
  const [text, setText] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [interviewId, setInterviewId] = useState('')
  const [interviews, setInterviews] = useState<Array<{ id: string; title: string; questions: Question[] }>>([])
  const [newQuestion, setNewQuestion] = useState({ prompt: '', question_type: 'technical', order_index: 5 })
  const [questions, setQuestions] = useState<Question[]>([])

  useEffect(() => { void loadRubric(); void loadInterviews() }, [])
  useEffect(() => { const i = interviews.find(x => x.id === interviewId); setQuestions(i?.questions ?? []) }, [interviewId, interviews])

  async function loadRubric() { try { const r = await api.rubric(name); setText(r.yaml_text) } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load rubric') } }
  async function loadInterviews() { try { const rows = await api.interviews(); setInterviews(rows); if (rows[0]) setInterviewId(rows[0].id) } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load question bank') } }
  async function save() { setMessage(''); setError(''); try { await api.saveRubric(name, text); setMessage('Rubric saved and validated.') } catch (e) { setError(e instanceof Error ? e.message : 'Rubric validation failed') } }
  async function addQuestion() { if (!interviewId || newQuestion.prompt.length < 10) return; try { const q = await api.addQuestion(interviewId, { ...newQuestion, expected_topics: [] }); setQuestions(v => [...v, q].sort((a,b)=>a.order_index-b.order_index)); setNewQuestion(v => ({ ...v, prompt: '', order_index: v.order_index + 1 })); setMessage('Question added to the interview bank.') } catch (e) { setError(e instanceof Error ? e.message : 'Could not add question') } }
  async function deleteQuestion(qId: string) { if (!interviewId) return; try { await api.deleteQuestion(interviewId, qId); setQuestions(v => v.filter(q => q.id !== qId)); setMessage('Question deleted from the interview bank.') } catch (e) { setError(e instanceof Error ? e.message : 'Could not delete question') } }

  return <div className="page"><header className="page-head"><div><p className="eyebrow">CONFIGURATION</p><h1>Rubrics & Question Bank</h1><p className="subtitle">YAML-backed scoring rules plus interviewer-managed question sets.</p></div></header>{error && <div className="alert error">{error}</div>}{message && <div className="alert success"><ShieldCheck size={15}/>{message}</div>}
    <section className="panel"><div className="toolbar"><label>Rubric<select value={name} onChange={e => { setName(e.target.value); void loadRubric() }}><option value="technical">technical.yaml</option><option value="behavioral">behavioral.yaml</option></select></label><button className="btn primary" onClick={() => void save()}><Save size={16}/> Save & validate</button></div><textarea className="yaml-editor" value={text} onChange={e => setText(e.target.value)} spellCheck={false}/></section>
    <section className="panel question-bank"><div className="panel-head"><div><h2>Question bank</h2><p>Manage interview prompts without hardcoding them into the evaluator.</p></div></div><div className="toolbar"><label>Interview<select value={interviewId} onChange={e => setInterviewId(e.target.value)}>{interviews.map(i => <option value={i.id} key={i.id}>{i.title}</option>)}</select></label><div className="question-add"><input placeholder="New question prompt" value={newQuestion.prompt} onChange={e => setNewQuestion(v => ({...v, prompt: e.target.value}))}/><select value={newQuestion.question_type} onChange={e => setNewQuestion(v => ({...v, question_type: e.target.value}))}><option value="technical">technical</option><option value="problem_solving">problem solving</option><option value="behavioral">behavioral</option></select><input type="number" min={0} value={newQuestion.order_index} onChange={e => setNewQuestion(v => ({...v, order_index: Number(e.target.value)}))}/><button className="btn primary" onClick={() => void addQuestion()}><Plus size={15}/> Add</button></div></div><div className="question-list">{questions.map(q => <div className="question-row" key={q.id}><span>Q{q.order_index + 1}</span><strong>{q.prompt}</strong><em>{q.question_type}</em><button className="icon-button" title="Delete question" style={{ color: '#ef4444', marginLeft: 'auto' }} onClick={() => void deleteQuestion(q.id)}><Trash2 size={15}/></button></div>)}</div></section>
  </div>
}

