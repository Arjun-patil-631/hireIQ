from app.database import SessionLocal
from app.services import process_response
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=2)
def process_response_task(self, job_id: str, audio_path: str, session_id: str, question_id: str):
    db = SessionLocal()
    try:
        response = process_response(db, job_id, audio_path, session_id, question_id)
        return {"response_id": response.id}
    finally:
        db.close()
