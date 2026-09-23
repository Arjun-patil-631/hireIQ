# Deployment Guide

## Recommended architecture

For the strict internship architecture, deploy the web/API service, PostgreSQL, Redis and at least one Celery worker as separate services. Keep the worker and API pointed at the same database and Redis broker.

## Docker Compose

```bash
docker compose up --build
```

This starts:
- PostgreSQL
- Redis
- FastAPI API
- Celery worker
- Vite frontend

## Railway

The repo contains `railway.json` and a root `Dockerfile` for a single web service. Add persistent PostgreSQL and Redis services in the Railway project and set `DATABASE_URL` and `REDIS_URL`. For full async behavior, run a second service using the same image with:

```bash
celery -A app.tasks.celery_app.celery_app worker --loglevel=INFO --concurrency=1
```

## Render

`render.yaml` is supplied as a quick single-service deployment blueprint. It uses `PROCESSING_MODE=sync` because a single web service does not provide the Celery worker. For strict compliance with the brief, add a separate worker/broker setup rather than relying on this simplified mode.

## Final checks before claiming deployment

- Open the live URL in an incognito window.
- Verify microphone permission.
- Record at least one real answer.
- Confirm the job status changes from queued/processing to completed.
- Confirm the PDF is downloadable.
- Verify no `.env` or provider key is in the repository.
- Verify the worker can restart without losing application state.
