export type Recommendation = 'Proceed' | 'Hold' | 'Reject'
export type Sentiment = 'positive' | 'neutral' | 'negative'

export interface Question {
  id: string
  order_index: number
  question_type: string
  prompt: string
  expected_topics: string[]
}

export interface Evaluation {
  technical_score: number
  problem_solving_score: number
  communication_score: number
  confidence_score: number
  overall_score: number
  sentiment: Sentiment
  strengths: string[]
  improvements: string[]
  rationale: string
  recommendation: Recommendation
  model_name: string
  nlp: {
    keywords: string[]
    entities: string[]
    sentiment: Sentiment
    sentiment_compound: number
    confidence_score: number
    filler_ratio: number
  }
}

export interface ResponseItem {
  id: string
  question_id: string
  transcript: string
  language: string
  audio_duration_seconds: number
  evaluation?: Evaluation | null
}

export interface Session {
  id: string
  candidate_id: string
  candidate_name: string
  interview_id: string
  interview_title: string
  rubric_name: string
  status: string
  started_at: string
  current_question_index: number
  questions: Question[]
  completed_questions: number
  responses?: ResponseItem[]
  overall_score?: number | null
  recommendation?: Recommendation | null
  report_available?: boolean
}

export interface Candidate {
  id: string
  name: string
  email: string
  created_at: string
  session_count: number
  latest_score?: number | null
  latest_recommendation?: Recommendation | null
}

export interface CandidateSession {
  id: string
  interview_id: string
  interview_title: string
  rubric_name: string
  status: string
  started_at: string
  overall_score?: number | null
  recommendation?: Recommendation | null
  completed_questions: number
  total_questions: number
}

export interface CandidateDetail extends Candidate {
  sessions: CandidateSession[]
}

export interface CandidateComparisonItem {
  candidate_id: string
  candidate_name: string
  candidate_email: string
  session_id?: string | null
  interview_title?: string | null
  overall_score?: number | null
  technical_score?: number | null
  problem_solving_score?: number | null
  communication_score?: number | null
  confidence_score?: number | null
  recommendation?: Recommendation | null
  status?: string | null
}

export interface Summary {
  total_candidates: number
  completed_interviews: number
  average_score: number
  proceed_count: number
  hold_count: number
  reject_count: number
}
