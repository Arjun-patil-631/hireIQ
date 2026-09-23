import os
import tempfile
from functools import lru_cache
from pathlib import Path

from pydub import AudioSegment

from app.config import settings


@lru_cache(maxsize=1)
def get_whisper_model():
    import whisper

    return whisper.load_model(settings.whisper_model)


def normalize_audio(source_path: str) -> tuple[str, float]:
    """Normalize incoming browser audio to mono 16 kHz WAV in a temporary file."""
    audio = AudioSegment.from_file(source_path)
    normalized = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    duration = len(normalized) / 1000.0
    fd, temp_path = tempfile.mkstemp(suffix=".wav", dir=settings.upload_dir)
    os.close(fd)
    normalized.export(temp_path, format="wav")
    return temp_path, duration


def transcribe(source_path: str) -> tuple[str, str, list[dict]]:
    model = get_whisper_model()
    result = model.transcribe(source_path, language=settings.whisper_language, fp16=False)
    text = (result.get("text") or "").strip()
    segments = []
    for seg in result.get("segments", []):
        segments.append({
            "start": round(float(seg.get("start", 0)), 2),
            "end": round(float(seg.get("end", 0)), 2),
            "text": (seg.get("text") or "").strip(),
        })
    return text, result.get("language", settings.whisper_language), segments
