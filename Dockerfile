# Single-container deployment option: FastAPI serves the compiled React SPA.
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY backend/ ./
COPY --from=frontend-builder /frontend/dist /app/frontend_dist
RUN mkdir -p /app/runtime/uploads /app/runtime/reports /app/config/rubrics
COPY config/ /app/config/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
