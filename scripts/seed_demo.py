"""Seed HireIQ with safe-to-display synthetic candidates and completed evaluations.
This does not call any external AI API and does not store audio.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.database import Base, SessionLocal, engine
from app.models import Candidate, Evaluation, Interview, InterviewSession, Question, Report, Response
from app.reports.generator import generate_report


def get_demo_interview(db):
    interview = db.query(Interview).filter(Interview.title == "AI Engineer Screening — Demo").first()
    if interview:
        return interview
    interview = Interview(title="AI Engineer Screening — Demo", description="Five-question synthetic screening dataset.", rubric_name="technical", timer_minutes=10)
    questions = [
        (0, "technical", "Explain the difference between a process and a thread, and when you would prefer one over the other."),
        (1, "technical", "How would you design a REST API for a simple task management application?"),
        (2, "problem_solving", "You have an O(n^2) algorithm over one million records. How would you investigate and improve it?"),
        (3, "technical", "What is overfitting in machine learning, and give two practical ways to reduce it?"),
        (4, "behavioral", "Tell us about a technical problem you solved and how you communicated the trade-offs to your team."),
    ]
    for idx, typ, prompt in questions:
        interview.questions.append(Question(order_index=idx, question_type=typ, prompt=prompt))
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def add_candidate(db, interview, name, email, score_bias):
    candidate = Candidate(name=name, email=email)
    db.add(candidate)
    db.flush()
    session = InterviewSession(candidate_id=candidate.id, interview_id=interview.id, status="completed", current_question_index=len(interview.questions))
    db.add(session)
    db.flush()
    base = [79, 76, 82, 73, 80]
    for idx, q in enumerate(sorted(interview.questions, key=lambda x: x.order_index)):
        s = max(35, min(96, base[idx] + score_bias))
        transcript = [
            "A process has its own address space, while threads share memory inside a process. I would choose threads for lightweight concurrent work and processes for stronger isolation.",
            "I would define resources and HTTP methods first, add request validation and authentication, and persist tasks in a relational database with pagination and clear error responses.",
            "I would profile the bottleneck first, confirm the complexity, and then look for a better algorithm or indexing strategy. For one million records I would avoid repeated nested scans and verify the improvement with measurements.",
            "Overfitting happens when a model captures training noise and performs poorly on unseen data. I would use regularization and validation, and I could also add more data or simplify the model.",
            "I had a slow data pipeline, profiled it, changed a repeated lookup into a cached structure, and explained the throughput versus memory trade-off to the team with measurements.",
        ][idx]
        response = Response(session_id=session.id, question_id=q.id, transcript=transcript, language="en", audio_duration_seconds=24 + idx * 4, nlp_json={"keywords": q.prompt.split()[:5], "entities": [], "sentiment": "positive", "sentiment_compound": 0.65, "confidence_score": s + 2, "filler_ratio": 0.01})
        db.add(response)
        db.flush()
        db.add(Evaluation(
            response_id=response.id,
            technical_score=s,
            problem_solving_score=max(0, min(100, s + 2)),
            communication_score=max(0, min(100, s - 1)),
            confidence_score=max(0, min(100, s + 2)),
            overall_score=s,
            sentiment="positive",
            strengths=["Correct core concept", "Explains a practical trade-off", "Evidence is relevant"],
            improvements=["Add one more implementation detail", "Quantify the example where possible"],
            rationale="Synthetic demo evaluation aligned to the configured rubric."
            ,recommendation="Proceed" if s >= 75 else "Hold" if s >= 55 else "Reject", model_name="seed-demo"
        ))
    db.commit()
    session = db.get(InterviewSession, session.id)
    report_path = generate_report(session, db)
    db.add(Report(session_id=session.id, file_path=report_path))
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        interview = get_demo_interview(db)
        # Avoid duplicating the synthetic set if already seeded.
        existing = {c.email for c in db.query(Candidate).all()}
        for name, email, bias in [
            ("Priya Rao", "priya.demo@hireiq.local", 5),
            ("Rohan Mehta", "rohan.demo@hireiq.local", -1),
            ("Meera Iyer", "meera.demo@hireiq.local", -10),
        ]:
            if email not in existing:
                add_candidate(db, interview, name, email, bias)
        print("HireIQ synthetic demo data is ready.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
