from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=255)


class CandidateOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    session_count: int = 0
    latest_score: float | None = None
    latest_recommendation: str | None = None


class CandidateSessionOut(BaseModel):
    id: str
    interview_id: str
    interview_title: str
    rubric_name: str
    status: str
    started_at: datetime
    overall_score: float | None = None
    recommendation: str | None = None
    completed_questions: int = 0
    total_questions: int = 0


class CandidateDetailOut(CandidateOut):
    sessions: list[CandidateSessionOut] = Field(default_factory=list)


class CandidateComparisonItem(BaseModel):
    candidate_id: str
    candidate_name: str
    candidate_email: str
    session_id: str | None = None
    interview_title: str | None = None
    overall_score: float | None = None
    technical_score: float | None = None
    problem_solving_score: float | None = None
    communication_score: float | None = None
    confidence_score: float | None = None
    recommendation: str | None = None
    status: str | None = None


class CandidateComparisonOut(BaseModel):
    candidates: list[CandidateComparisonItem]


class QuestionCreate(BaseModel):
    order_index: int = Field(ge=0)
    question_type: str = "technical"
    prompt: str = Field(min_length=10)
    expected_topics: list[str] = Field(default_factory=list)


class QuestionOut(QuestionCreate):
    id: str


class InterviewCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = ""
    rubric_name: str = "technical"
    timer_minutes: int = Field(default=15, ge=1, le=120)
    questions: list[QuestionCreate] = Field(default_factory=list)


class InterviewOut(BaseModel):
    id: str
    title: str
    description: str
    rubric_name: str
    timer_minutes: int
    is_active: bool
    questions: list[QuestionOut]


class DemoStartRequest(BaseModel):
    name: str = Field(default="Alex Sharma", min_length=2, max_length=120)
    email: str = Field(default="alex@example.com", min_length=3, max_length=255)


class SessionOut(BaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    interview_id: str
    interview_title: str
    rubric_name: str
    status: str
    started_at: datetime
    current_question_index: int
    questions: list[QuestionOut]
    completed_questions: int = 0


class KeywordEntityOut(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    sentiment_compound: float = 0.0
    confidence_score: float = Field(default=70.0, ge=0, le=100)
    filler_ratio: float = Field(default=0.0, ge=0, le=1)


class EvaluationResult(BaseModel):
    technical_score: float = Field(ge=0, le=100)
    problem_solving_score: float = Field(ge=0, le=100)
    communication_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    strengths: list[str] = Field(default_factory=list, min_length=1, max_length=5)
    improvements: list[str] = Field(default_factory=list, min_length=1, max_length=5)
    rationale: str = Field(min_length=10, max_length=2000)
    recommendation: Literal["Proceed", "Hold", "Reject"]

    @field_validator("strengths", "improvements")
    @classmethod
    def clean_items(cls, items: list[str]) -> list[str]:
        cleaned = [x.strip() for x in items if x and x.strip()]
        if not cleaned:
            raise ValueError("at least one item is required")
        return cleaned[:5]


class EvaluationOut(EvaluationResult):
    model_name: str
    nlp: KeywordEntityOut


class ResponseOut(BaseModel):
    id: str
    question_id: str
    transcript: str
    language: str
    audio_duration_seconds: float
    evaluation: EvaluationOut | None = None


class JobOut(BaseModel):
    id: str
    status: str
    task_id: str | None = None
    error_message: str | None = None
    response_id: str | None = None


class SessionDetailOut(SessionOut):
    responses: list[ResponseOut] = Field(default_factory=list)
    overall_score: float | None = None
    recommendation: str | None = None
    report_available: bool = False


class DashboardSummary(BaseModel):
    total_candidates: int
    completed_interviews: int
    average_score: float
    proceed_count: int
    hold_count: int
    reject_count: int


class PaginatedCandidates(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[CandidateOut]


class RubricOut(BaseModel):
    name: str
    yaml_text: str
