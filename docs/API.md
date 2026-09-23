# HireIQ API Reference

Base URL: `http://localhost:8000/api/v1`

## Health

`GET /health`

Returns service status and processing mode.

## Dashboard

`GET /dashboard/summary`

Returns total candidates, completed sessions, average evaluation score, and decision counts.

`GET /candidates?page=1&page_size=8`

Returns a paginated candidate list. `page_size` is capped at 100.

## Demo

`POST /demo/start`

```json
{"name":"Alex Sharma","email":"alex@example.com"}
```

Creates a synthetic demo interview session and returns the question list.

## Session

`GET /sessions/{session_id}`

Returns candidate/session metadata, completed response transcripts, evaluations, final score, recommendation and report availability.

`POST /sessions/{session_id}/responses/{question_id}`

Multipart form field: `audio`. Accepted: webm, wav, mp3, m4a, ogg, mp4. The endpoint creates a processing job and returns HTTP 202.

## Job polling

`GET /jobs/{job_id}`

Possible states: `queued`, `processing`, `completed`, `failed`.

## Reports

`GET /reports/{session_id}.pdf`

Returns the generated ReportLab PDF.

## Rubrics

`GET /rubrics/{name}`

Returns the YAML text.

`PUT /rubrics/{name}`

```json
{"name":"technical","yaml_text":"..."}
```

The server validates criterion weights and required scoring levels before writing the file.
