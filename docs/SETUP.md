# HireIQ Setup Guide

## 1. Prerequisites

Recommended for the full stack:

- Python 3.12
- Node.js 22+
- Docker Desktop (recommended)
- FFmpeg on the host if running Whisper outside Docker
- A Gemini API key for live LLM evaluation

Whisper's upstream project requires FFmpeg and can be installed with `pip install -U openai-whisper`.

## 2. Two-minute Docker path

```bash
docker compose up --build
```

Then in another terminal:

```bash
python scripts/seed_demo.py
```

Visit `http://localhost:5173`.

## 3. Real AI path

In `.env`:

```env
GEMINI_API_KEY=YOUR_KEY
DEMO_AI_FALLBACK=false
PROCESSING_MODE=celery
WHISPER_MODEL=base
```

Restart the stack.

The first Whisper execution may download the selected model. For a CPU laptop, `base` is a sensible demo starting point; larger models trade speed for recognition quality.

## 4. Sync debugging mode

For local API debugging without Redis:

```env
PROCESSING_MODE=sync
AI_PROVIDER=mock
DEMO_AI_FALLBACK=true
```

This mode is intended for development only. The submission architecture should demonstrate the Celery + Redis path.

## 5. Troubleshooting

### Microphone does not work

Use Chrome/Edge on `localhost` or HTTPS and grant microphone access.

### Whisper fails with ffmpeg errors

Install FFmpeg and verify `ffmpeg -version` works in the same environment as Python.

### Gemini evaluation fails

Check `GEMINI_API_KEY`, the selected `GEMINI_MODEL`, and the API quota. The code validates the response against the Pydantic schema before storage.

### spaCy entities are empty

Run:

```bash
python -m spacy download en_core_web_sm
```

The app also has a lightweight token-based fallback for the demo UI.
