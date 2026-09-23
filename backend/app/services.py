from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.evaluator import evaluate_answer
from app.audio.transcriber import normalize_audio, transcribe
from app.models import Evaluation, InterviewSession, ProcessingJob, Report, Response
from app.nlp.analyzer import analyze_text
from app.reports.generator import generate_report


def process_response(db: Session, job_id: str, audio_path: str, session_id: str, question_id: str) -> Response:
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise ValueError("Processing job not found")
    job.status = "processing"
    db.commit()
    normalized_path = None
    try:
        session = db.get(InterviewSession, session_id)
        if not session:
            raise ValueError("Session not found")
        question = next((q for q in session.interview.questions if q.id == question_id), None)
        if not question:
            raise ValueError("Question not found")

        normalized_path, duration = normalize_audio(audio_path)
        transcript, language, segments = transcribe(normalized_path)
        if not transcript.strip():
            raise ValueError("Whisper returned an empty transcript")
        nlp = analyze_text(transcript)
        rubric_name = session.interview.rubric_name or "technical"
        evaluation, model_name = evaluate_answer(question.prompt, question.question_type, transcript, nlp, rubric_name=rubric_name)

        # Persist only the transcript + derived evaluation; audio is deleted below.
        response = Response(
            session_id=session_id,
            question_id=question_id,
            transcript=transcript,
            language=language,
            audio_duration_seconds=duration,
            nlp_json=nlp,
        )
        db.add(response)
        db.flush()
        db.add(Evaluation(
            response_id=response.id,
            technical_score=evaluation.technical_score,
            problem_solving_score=evaluation.problem_solving_score,
            communication_score=evaluation.communication_score,
            confidence_score=evaluation.confidence_score,
            overall_score=evaluation.overall_score,
            sentiment=evaluation.sentiment,
            strengths=evaluation.strengths,
            improvements=evaluation.improvements,
            rationale=evaluation.rationale,
            recommendation=evaluation.recommendation,
            model_name=model_name,
        ))

        session.current_question_index = min(len(session.interview.questions), session.current_question_index + 1)
        if session.current_question_index >= len(session.interview.questions):
            session.status = "completed"
            # Report generation is deterministic and local; run after evaluations persist.
            db.commit()
            session = db.get(InterviewSession, session_id)
            report_path = generate_report(session, db)
            existing = db.query(Report).filter(Report.session_id == session_id).first()
            if existing:
                existing.file_path = report_path
            else:
                db.add(Report(session_id=session_id, file_path=report_path))
        db.commit()
        db.refresh(response)
        job.status = "completed"
        job.result_json = {"response_id": response.id, "model_name": model_name}
        job.error_message = None
        db.commit()
        return response
    except Exception as exc:
        db.rollback()
        job = db.get(ProcessingJob, job_id)
        if job:
            job.status = "failed"
            job.error_message = str(exc)[:1000]
            db.commit()
        raise
    finally:
        for path in [audio_path, normalized_path]:
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except Exception:
                    pass
