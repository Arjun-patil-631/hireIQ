# HireIQ — Multimodal AI Interview Intelligence Platform

> Code A Nova • Internship Program 2026 • Project 4

HireIQ is an end-to-end interview intelligence prototype that records candidate audio in the browser, normalizes it with PyDub, transcribes speech with OpenAI Whisper, enriches the transcript with spaCy/VADER signals, evaluates the answer against an external YAML rubric using a structured LLM response, and generates a hiring-manager report with per-question evidence and a radar chart.

## What is included

- React 18 + TypeScript + Vite interview experience
- FastAPI backend with SQLAlchemy models
- PostgreSQL-ready schema; SQLite is the default local fallback
- Celery + Redis asynchronous processing path
- OpenAI Whisper transcription with temporary audio files
- spaCy keyword/entity enrichment with VADER sentiment analysis
- Supplementary confidence heuristics based on transcript features
- Gemini structured-output evaluation with Pydantic validation
- YAML-configurable scoring rubrics and editor UI
- ReportLab PDF report with radar chart
- Hiring-manager dashboard, candidate pagination and comparison signals
- Session transcript review and report download
- Synthetic demo seed data
- Pytest + Playwright smoke tests
- Bias review, WER analysis and submission documentation
- Docker Compose for API + worker + PostgreSQL + Redis + frontend

## Architecture

```text
Browser / React
     |
     | MediaRecorder audio
     v
 FastAPI API ─────── PostgreSQL
     |
     +──── Redis broker ─── Celery worker
                              |
                              +── PyDub -> normalized WAV
                              +── Whisper -> transcript
                              +── spaCy + VADER -> NLP signals
                              +── Gemini -> rubric JSON
                              +── Pydantic -> validated evaluation
                              +── ReportLab -> PDF

Dashboard <──────────── JSON / PDF ─────────── FastAPI
```

See `docs/ARCHITECTURE.md` for the full flow and `docs/BIAS_REVIEW.md` for the AI ethics notes.

## Fastest local setup

### Option A — Docker Compose (recommended for the brief)

1. Copy environment file:

```bash
copy .env.example .env
```

2. Put your Gemini key in `.env` as `GEMINI_API_KEY=...` (or leave it blank to use the deterministic demo fallback).

3. Start services:

```bash
docker compose up --build
```

Open:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

4. Seed synthetic manager-dashboard data in a second terminal:

```bash
python scripts/seed_demo.py
```

### Option B — local Python + Node

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

For a no-Redis development smoke test, use `PROCESSING_MODE=sync` in the backend environment. For the internship architecture, use `PROCESSING_MODE=celery` with Redis + a Celery worker.

## API highlights

- `GET /api/v1/health`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/candidates?page=1&page_size=8`
- `POST /api/v1/demo/start`
- `GET /api/v1/sessions/{session_id}`
- `POST /api/v1/sessions/{session_id}/responses/{question_id}`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/reports/{session_id}.pdf`
- `GET /api/v1/rubrics/{name}`
- `PUT /api/v1/rubrics/{name}`

See `docs/API.md` for payloads.

## AI configuration

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
DEMO_AI_FALLBACK=true
WHISPER_MODEL=base
WHISPER_LANGUAGE=en
PROCESSING_MODE=celery
```

The API key is read by the backend only. Do not place provider secrets in React source or Vite variables.

## Demo data

`python scripts/seed_demo.py` adds three synthetic candidates with completed evaluations and generates PDF reports. The data is fictional and intended for screenshots/demo recording.

The `sample_data/sample_answer.wav` file is a synthetic spoken example for transcription testing; it is not a real candidate recording.

## Testing

Backend:

```bash
cd backend
pytest -q
```

Frontend smoke tests:

```bash
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

## Production/security notes

- Candidate audio is stored only in a temporary runtime directory and deleted after transcription processing.
- Candidate transcripts are never written to stdout by the pipeline.
- LLM output is validated using the `EvaluationResult` Pydantic schema before evaluation persistence.
- Rubric criteria are loaded from YAML rather than hardcoded in the scoring engine.
- Dashboard candidate listing uses `page` and `page_size` limits.
- Bias guidance is embedded in the evaluation prompt and documented in `docs/BIAS_REVIEW.md`.
- The application is decision support; hiring managers must review evidence rather than delegating the employment decision to the model.

## Submission pack

The internship brief requests a deployed URL, GitHub repo, sample session recording, sample PDF report, prompt + rubric files, Whisper WER analysis, dashboard screenshots, architecture diagram, bias review, and README. The exact checklist and suggested evidence plan are in `docs/SUBMISSION.md`.
