# HireIQ Architecture

## End-to-end flow

1. The React interview page displays the current question and captures browser microphone input with `MediaRecorder`.
2. The audio blob is uploaded to FastAPI using multipart form data.
3. FastAPI writes the blob to a temporary file and creates a processing job record.
4. In the full path, the job is queued to Celery through Redis; the UI polls the job endpoint.
5. The worker normalizes audio with PyDub to mono 16 kHz WAV.
6. Whisper transcribes the temporary WAV and returns text + timestamps.
7. spaCy extracts entities/keywords and VADER provides sentiment polarity. A transcript-based confidence heuristic is stored as a supplementary signal.
8. The evaluator builds a prompt from the question, question type, YAML rubric, candidate transcript, and supplementary NLP signals.
9. Gemini is requested to produce structured JSON matching the `EvaluationResult` Pydantic schema.
10. Pydantic validation is the persistence gate; invalid model output is rejected rather than stored.
11. The response transcript and evaluation are stored in PostgreSQL/SQLite.
12. On final question completion, ReportLab creates a PDF with a radar chart and per-question evidence.
13. The dashboard reads paginated candidate data and completed evaluations.

## Services

### Frontend

React 18 + TypeScript + Vite. Responsibilities: interview workflow, media capture, job polling, dashboard and rubric editing.

### API

FastAPI. Responsibilities: request validation, persistence, upload limits, job creation, session state, report delivery.

### Worker

Celery. Responsibilities: Whisper, NLP and LLM evaluation. A worker can be horizontally replicated because state is persisted in the database and the queue is external.

### Data layer

SQLAlchemy models cover Candidates, Interviews, Questions, Sessions, Responses, Evaluations, Processing Jobs and Reports.

### Retention

Only temporary audio is written to `runtime/uploads`. The processing service removes the original upload and normalized WAV in a `finally` block. Audio is not stored permanently in the database.

## Security boundaries

- API keys exist only on the backend.
- No transcript logging in the processing path.
- Candidate list endpoints paginate records.
- Uploaded file size is capped by `MAX_AUDIO_MB`.
- Rubric writes are validated before persistence to disk.
- LLM output is Pydantic-validated before DB insertion.

## Architecture diagram

See `architecture.svg` for a screenshot-ready diagram.
