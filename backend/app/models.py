from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def uid() -> str:
    return str(uuid4())


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    sessions: Mapped[list["InterviewSession"]] = relationship(back_populates="candidate")


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    rubric_name: Mapped[str] = mapped_column(String(80), default="technical")
    timer_minutes: Mapped[int] = mapped_column(Integer, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    questions: Mapped[list["Question"]] = relationship(back_populates="interview", cascade="all, delete-orphan")
    sessions: Mapped[list["InterviewSession"]] = relationship(back_populates="interview")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(String(60), default="technical")
    prompt: Mapped[str] = mapped_column(Text)
    expected_topics: Mapped[list] = mapped_column(JSON, default=list)

    interview: Mapped[Interview] = relationship(back_populates="questions")

    __table_args__ = (UniqueConstraint("interview_id", "order_index", name="uq_question_order"),)


class InterviewSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("candidates.id"), index=True)
    interview_id: Mapped[str] = mapped_column(ForeignKey("interviews.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="in_progress")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_question_index: Mapped[int] = mapped_column(Integer, default=0)

    candidate: Mapped[Candidate] = relationship(back_populates="sessions")
    interview: Mapped[Interview] = relationship(back_populates="sessions")
    responses: Mapped[list["Response"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    report: Mapped["Report | None"] = relationship(back_populates="session", uselist=False, cascade="all, delete-orphan")


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(20), default="en")
    audio_duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    nlp_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    session: Mapped[InterviewSession] = relationship(back_populates="responses")
    evaluation: Mapped["Evaluation | None"] = relationship(back_populates="response", uselist=False, cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    response_id: Mapped[str] = mapped_column(ForeignKey("responses.id", ondelete="CASCADE"), unique=True)
    technical_score: Mapped[float] = mapped_column(Float, default=0.0)
    problem_solving_score: Mapped[float] = mapped_column(Float, default=0.0)
    communication_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    sentiment: Mapped[str] = mapped_column(String(20), default="neutral")
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    rationale: Mapped[str] = mapped_column(Text, default="")
    recommendation: Mapped[str] = mapped_column(String(30), default="Hold")
    model_name: Mapped[str] = mapped_column(String(100), default="demo")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    response: Mapped[Response] = relationship(back_populates="evaluation")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    task_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), unique=True)
    file_path: Mapped[str] = mapped_column(String(500))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    session: Mapped[InterviewSession] = relationship(back_populates="report")
