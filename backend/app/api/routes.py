import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.ai.rubric import load_rubric, rubric_path, save_rubric
from app.config import settings
from app.database import get_db
from app.models import Candidate, Evaluation, Interview, InterviewSession, ProcessingJob, Question, Report, Response
from app.schemas import (
    CandidateComparisonItem, CandidateComparisonOut, CandidateCreate, CandidateDetailOut, CandidateOut,
    CandidateSessionOut, DashboardSummary, DemoStartRequest, EvaluationOut, InterviewCreate, QuestionCreate,
    InterviewOut, JobOut, PaginatedCandidates, QuestionOut, ResponseOut, RubricOut, SessionDetailOut, SessionOut,
)
from app.services import process_response

router = APIRouter()


def interview_out(interview: Interview) -> InterviewOut:
    return InterviewOut(
        id=interview.id,
        title=interview.title,
        description=interview.description,
        rubric_name=interview.rubric_name,
        timer_minutes=interview.timer_minutes,
        is_active=interview.is_active,
        questions=[QuestionOut(id=q.id, order_index=q.order_index, question_type=q.question_type, prompt=q.prompt, expected_topics=q.expected_topics or []) for q in sorted(interview.questions, key=lambda x: x.order_index)],
    )


def session_out(session: InterviewSession) -> SessionOut:
    completed = len([r for r in session.responses if r.evaluation])
    return SessionOut(
        id=session.id, candidate_id=session.candidate_id, candidate_name=session.candidate.name,
        interview_id=session.interview_id, interview_title=session.interview.title, rubric_name=session.interview.rubric_name,
        status=session.status, started_at=session.started_at, current_question_index=session.current_question_index,
        questions=[QuestionOut(id=q.id, order_index=q.order_index, question_type=q.question_type, prompt=q.prompt, expected_topics=q.expected_topics or []) for q in sorted(session.interview.questions, key=lambda x: x.order_index)],
        completed_questions=completed,
    )


def eval_out(response: Response) -> EvaluationOut | None:
    if not response.evaluation:
        return None
    e = response.evaluation
    return EvaluationOut(
        technical_score=e.technical_score, problem_solving_score=e.problem_solving_score,
        communication_score=e.communication_score, confidence_score=e.confidence_score,
        overall_score=e.overall_score, sentiment=e.sentiment, strengths=e.strengths or [], improvements=e.improvements or [],
        rationale=e.rationale, recommendation=e.recommendation, model_name=e.model_name,
        nlp=response.nlp_json or {},
    )


@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(func.count(Candidate.id)).scalar()
    return {"status": "ok", "service": settings.app_name, "processing_mode": settings.processing_mode, "ai_provider": settings.ai_provider}


@router.post("/candidates", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(name=payload.name.strip(), email=payload.email.strip().lower())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return CandidateOut(id=candidate.id, name=candidate.name, email=candidate.email, created_at=candidate.created_at)


@router.get("/candidates", response_model=PaginatedCandidates)
def list_candidates(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.query(Candidate).count()
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for c in candidates:
        sessions = sorted(c.sessions, key=lambda s: s.started_at, reverse=True)
        latest = sessions[0] if sessions else None
        latest_score = None
        latest_recommendation = None
        if latest:
            latest_evals = [r.evaluation for r in latest.responses if r.evaluation]
            if latest_evals:
                latest_score = round(sum(e.overall_score for e in latest_evals) / len(latest_evals), 1)
                latest_recommendation = "Proceed" if latest_score >= 75 else "Hold" if latest_score >= 55 else "Reject"
        items.append(CandidateOut(
            id=c.id, name=c.name, email=c.email, created_at=c.created_at,
            session_count=len(sessions), latest_score=latest_score, latest_recommendation=latest_recommendation,
        ))
    return PaginatedCandidates(page=page, page_size=page_size, total=total, items=items)


@router.get("/candidates/compare", response_model=CandidateComparisonOut)
def compare_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).order_by(Candidate.name.asc()).all()
    items = []
    for c in candidates:
        sessions = sorted(c.sessions, key=lambda s: s.started_at, reverse=True)
        latest = sessions[0] if sessions else None
        if latest:
            evals = [r.evaluation for r in latest.responses if r.evaluation]
            overall = round(sum(e.overall_score for e in evals) / len(evals), 1) if evals else None
            tech = round(sum(e.technical_score for e in evals) / len(evals), 1) if evals else None
            prob = round(sum(e.problem_solving_score for e in evals) / len(evals), 1) if evals else None
            comm = round(sum(e.communication_score for e in evals) / len(evals), 1) if evals else None
            conf = round(sum(e.confidence_score for e in evals) / len(evals), 1) if evals else None
            rec = "Proceed" if overall and overall >= 75 else "Hold" if overall and overall >= 55 else "Reject" if overall else None
            items.append(CandidateComparisonItem(
                candidate_id=c.id, candidate_name=c.name, candidate_email=c.email,
                session_id=latest.id, interview_title=latest.interview.title,
                overall_score=overall, technical_score=tech, problem_solving_score=prob,
                communication_score=comm, confidence_score=conf, recommendation=rec, status=latest.status,
            ))
        else:
            items.append(CandidateComparisonItem(
                candidate_id=c.id, candidate_name=c.name, candidate_email=c.email,
            ))
    return CandidateComparisonOut(candidates=items)


@router.get("/candidates/{candidate_id}", response_model=CandidateDetailOut)
def candidate_detail(candidate_id: str, db: Session = Depends(get_db)):
    c = db.get(Candidate, candidate_id)
    if not c:
        raise HTTPException(404, "Candidate not found")
    sessions = sorted(c.sessions, key=lambda s: s.started_at, reverse=True)
    latest = sessions[0] if sessions else None
    latest_score = None
    latest_recommendation = None
    session_items = []
    for s in sessions:
        s_evals = [r.evaluation for r in s.responses if r.evaluation]
        s_score = round(sum(e.overall_score for e in s_evals) / len(s_evals), 1) if s_evals else None
        s_rec = "Proceed" if s_score and s_score >= 75 else "Hold" if s_score and s_score >= 55 else "Reject" if s_score else None
        session_items.append(CandidateSessionOut(
            id=s.id, interview_id=s.interview_id, interview_title=s.interview.title,
            rubric_name=s.interview.rubric_name, status=s.status, started_at=s.started_at,
            overall_score=s_score, recommendation=s_rec,
            completed_questions=len(s_evals), total_questions=len(s.interview.questions),
        ))
    if latest:
        latest_evals = [r.evaluation for r in latest.responses if r.evaluation]
        if latest_evals:
            latest_score = round(sum(e.overall_score for e in latest_evals) / len(latest_evals), 1)
            latest_recommendation = "Proceed" if latest_score >= 75 else "Hold" if latest_score >= 55 else "Reject"
    return CandidateDetailOut(
        id=c.id, name=c.name, email=c.email, created_at=c.created_at,
        session_count=len(c.sessions), latest_score=latest_score,
        latest_recommendation=latest_recommendation, sessions=session_items,
    )


@router.post("/interviews", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    interview = Interview(title=payload.title, description=payload.description, rubric_name=payload.rubric_name, timer_minutes=payload.timer_minutes)
    for q in payload.questions:
        interview.questions.append(Question(order_index=q.order_index, question_type=q.question_type, prompt=q.prompt, expected_topics=q.expected_topics))
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview_out(interview)


@router.get("/interviews", response_model=list[InterviewOut])
def list_interviews(db: Session = Depends(get_db)):
    return [interview_out(i) for i in db.query(Interview).order_by(Interview.created_at.desc()).all()]


@router.get("/interviews/{interview_id}", response_model=InterviewOut)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    i = db.get(Interview, interview_id)
    if not i:
        raise HTTPException(404, "Interview not found")
    return interview_out(i)


@router.get("/interviews/{interview_id}/questions", response_model=list[QuestionOut])
def list_questions(interview_id: str, db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    return [QuestionOut(id=q.id, order_index=q.order_index, question_type=q.question_type, prompt=q.prompt, expected_topics=q.expected_topics or []) for q in sorted(interview.questions, key=lambda x: x.order_index)]


@router.post("/interviews/{interview_id}/questions", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def add_question(interview_id: str, payload: QuestionCreate, db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    q = Question(interview_id=interview_id, order_index=payload.order_index, question_type=payload.question_type, prompt=payload.prompt, expected_topics=payload.expected_topics)
    db.add(q)
    db.commit()
    db.refresh(q)
    return QuestionOut(id=q.id, order_index=q.order_index, question_type=q.question_type, prompt=q.prompt, expected_topics=q.expected_topics or [])


@router.delete("/interviews/{interview_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(interview_id: str, question_id: str, db: Session = Depends(get_db)):
    q = db.get(Question, question_id)
    if not q or q.interview_id != interview_id:
        raise HTTPException(404, "Question not found")
    db.delete(q)
    db.commit()
    return None


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(candidate_id: str, interview_id: str, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    interview = db.get(Interview, interview_id)
    if not candidate or not interview:
        raise HTTPException(404, "Candidate or interview not found")
    session = InterviewSession(candidate_id=candidate_id, interview_id=interview_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session_out(session)


@router.get("/sessions/{session_id}", response_model=SessionDetailOut)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).options(joinedload(InterviewSession.responses).joinedload(Response.evaluation), joinedload(InterviewSession.candidate), joinedload(InterviewSession.interview).joinedload(Interview.questions)).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    evaluations = [r.evaluation for r in session.responses if r.evaluation]
    overall = sum(e.overall_score for e in evaluations) / len(evaluations) if evaluations else None
    recommendation = None
    if overall is not None:
        recommendation = "Proceed" if overall >= 75 else "Hold" if overall >= 55 else "Reject"
    return SessionDetailOut(
        **session_out(session).model_dump(),
        responses=[ResponseOut(id=r.id, question_id=r.question_id, transcript=r.transcript, language=r.language, audio_duration_seconds=r.audio_duration_seconds, evaluation=eval_out(r)) for r in session.responses],
        overall_score=round(overall, 1) if overall is not None else None,
        recommendation=recommendation,
        report_available=bool(session.report and Path(session.report.file_path).exists()),
    )


@router.post("/sessions/{session_id}/responses/{question_id}", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def submit_response(session_id: str, question_id: str, audio: UploadFile = File(...), db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    question = db.get(Question, question_id)
    if not session or not question or question.interview_id != session.interview_id:
        raise HTTPException(404, "Session or question not found")
    suffix = Path(audio.filename or "answer.webm").suffix or ".webm"
    if suffix.lower() not in {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4"}:
        raise HTTPException(400, "Unsupported audio format")
    job_id = str(uuid4())
    dest = Path(settings.upload_dir) / f"{job_id}{suffix}"
    size = 0
    with dest.open("wb") as f:
        while chunk := audio.file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_audio_mb * 1024 * 1024:
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "Audio file too large")
            f.write(chunk)
    job = ProcessingJob(id=job_id, session_id=session_id, question_id=question_id)
    db.add(job)
    db.commit()

    if settings.processing_mode == "sync":
        try:
            process_response(db, job_id, str(dest), session_id, question_id)
        except Exception as exc:
            db.refresh(job)
            return JobOut(id=job.id, status=job.status, error_message=str(exc))
        db.refresh(job)
        return JobOut(id=job.id, status=job.status, response_id=job.result_json.get("response_id"))

    try:
        from app.tasks.process_response import process_response_task
        task = process_response_task.delay(job_id, str(dest), session_id, question_id)
        job.task_id = task.id
        db.commit()
    except Exception as exc:
        job.status = "failed"
        job.error_message = f"Celery enqueue failed: {exc}"
        db.commit()
        dest.unlink(missing_ok=True)
    return JobOut(id=job.id, status=job.status, task_id=job.task_id)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return JobOut(id=job.id, status=job.status, task_id=job.task_id, error_message=job.error_message, response_id=(job.result_json or {}).get("response_id"))


@router.get("/reports/{session_id}.pdf")
def report_pdf(session_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.session_id == session_id).first()
    if not report or not Path(report.file_path).exists():
        raise HTTPException(404, "Report not available")
    return FileResponse(report.file_path, media_type="application/pdf", filename=Path(report.file_path).name)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).count()
    completed = db.query(InterviewSession).filter(InterviewSession.status == "completed").count()
    recommendation_counts = {"Proceed": 0, "Hold": 0, "Reject": 0}
    session_scores = []
    sessions = db.query(InterviewSession).filter(InterviewSession.status == "completed").all()
    for s in sessions:
        se = [r.evaluation for r in s.responses if r.evaluation]
        if not se:
            continue
        score = sum(x.overall_score for x in se) / len(se)
        session_scores.append(score)
        rec = "Proceed" if score >= 75 else "Hold" if score >= 55 else "Reject"
        recommendation_counts[rec] += 1
    avg = sum(session_scores) / len(session_scores) if session_scores else 0
    return DashboardSummary(total_candidates=candidates, completed_interviews=completed, average_score=round(avg, 1), proceed_count=recommendation_counts["Proceed"], hold_count=recommendation_counts["Hold"], reject_count=recommendation_counts["Reject"])


@router.get("/rubrics/{name}", response_model=RubricOut)
def get_rubric(name: str):
    path = rubric_path(name)
    if not path.exists():
        raise HTTPException(404, "Rubric not found")
    load_rubric(name)
    return RubricOut(name=name, yaml_text=path.read_text(encoding="utf-8"))


@router.put("/rubrics/{name}", response_model=RubricOut)
def put_rubric(name: str, payload: RubricOut):
    if payload.name != name:
        raise HTTPException(400, "Payload name must match URL name")
    try:
        save_rubric(name, payload.yaml_text)
    except Exception as exc:
        raise HTTPException(422, str(exc)) from exc
    return payload


@router.post("/demo/start", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def demo_start(payload: DemoStartRequest, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.title == "AI Engineer Screening — Demo").first()
    if not interview:
        interview = Interview(title="AI Engineer Screening — Demo", description="Five-question technical screening for the HireIQ demo.", rubric_name="technical", timer_minutes=10)
        prompts = [
            ("technical", "Explain the difference between a process and a thread, and when you would prefer one over the other.", ["process", "thread", "memory"]),
            ("technical", "How would you design a REST API for a simple task management application?", ["REST", "HTTP", "database", "validation"]),
            ("problem_solving", "You have an O(n^2) algorithm over one million records. How would you investigate and improve it?", ["complexity", "profiling", "optimization"]),
            ("technical", "What is overfitting in machine learning, and give two practical ways to reduce it?", ["overfitting", "regularization", "validation"]),
            ("behavioral", "Tell us about a technical problem you solved and how you communicated the trade-offs to your team.", ["example", "trade-off", "communication"]),
        ]
        for idx, (typ, prompt, topics) in enumerate(prompts):
            interview.questions.append(Question(order_index=idx, question_type=typ, prompt=prompt, expected_topics=topics))
        db.add(interview)
        db.commit()
        db.refresh(interview)
    candidate = Candidate(name=payload.name.strip(), email=payload.email.strip().lower())
    db.add(candidate)
    db.flush()
    session = InterviewSession(candidate_id=candidate.id, interview_id=interview.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session_out(session)
