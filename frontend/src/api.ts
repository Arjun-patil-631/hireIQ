import type { Candidate, CandidateComparisonItem, CandidateDetail, Question, Session, Summary } from './types'

const jsonHeaders = { 'Content-Type': 'application/json' }

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/api/v1/health'),
  summary: () => request<Summary>('/api/v1/dashboard/summary'),
  candidates: (page = 1, pageSize = 8) => request<{ page: number; page_size: number; total: number; items: Candidate[] }>(`/api/v1/candidates?page=${page}&page_size=${pageSize}`),
  candidateDetail: (id: string) => request<CandidateDetail>(`/api/v1/candidates/${id}`),
  compareCandidates: () => request<{ candidates: CandidateComparisonItem[] }>('/api/v1/candidates/compare'),
  demoStart: (name: string, email: string) => request<Session>('/api/v1/demo/start', { method: 'POST', headers: jsonHeaders, body: JSON.stringify({ name, email }) }),
  session: (id: string) => request<Session>(`/api/v1/sessions/${id}`),
  job: (id: string) => request<{ id: string; status: string; task_id?: string; error_message?: string; response_id?: string }>(`/api/v1/jobs/${id}`),
  submitAudio: async (sessionId: string, questionId: string, blob: Blob) => {
    const data = new FormData()
    data.append('audio', blob, 'answer.webm')
    return request<{ id: string; status: string; task_id?: string }>(`/api/v1/sessions/${sessionId}/responses/${questionId}`, { method: 'POST', body: data })
  },
  rubric: (name = 'technical') => request<{ name: string; yaml_text: string }>(`/api/v1/rubrics/${name}`),
  saveRubric: (name: string, yamlText: string) => request<{ name: string; yaml_text: string }>(`/api/v1/rubrics/${name}`, { method: 'PUT', headers: jsonHeaders, body: JSON.stringify({ name, yaml_text: yamlText }) }),
  interviews: () => request<Array<{ id: string; title: string; questions: Question[] }>>('/api/v1/interviews'),
  addQuestion: (interviewId: string, question: Omit<Question, 'id'>) => request<Question>(`/api/v1/interviews/${interviewId}/questions`, { method: 'POST', headers: jsonHeaders, body: JSON.stringify(question) }),
  deleteQuestion: (interviewId: string, questionId: string) => fetch(`/api/v1/interviews/${interviewId}/questions/${questionId}`, { method: 'DELETE' }),
  reportUrl: (sessionId: string) => `/api/v1/reports/${sessionId}.pdf`,
}

export function getCurrentQuestion(session: Session): Question | null {
  return session.questions[session.current_question_index] ?? null
}
