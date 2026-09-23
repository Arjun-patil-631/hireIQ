from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BASE_DIR


class Settings(BaseSettings):
    app_name: str = "HireIQ"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    database_url: str = f"sqlite:///{BASE_DIR / 'hireiq.db'}"
    redis_url: str = "redis://localhost:6379/0"
    processing_mode: str = "celery"  # celery | sync

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    ai_provider: str = "gemini"  # gemini | mock
    demo_ai_fallback: bool = True

    whisper_model: str = "base"
    whisper_language: str = "en"

    upload_dir: str = str(ROOT_DIR / "runtime" / "uploads")
    config_dir: str = str(ROOT_DIR / "config")
    report_dir: str = str(ROOT_DIR / "runtime" / "reports")
    max_audio_mb: int = 25
    job_poll_interval_seconds: float = 1.5

    model_config = SettingsConfigDict(
        env_file=[str(ROOT_DIR / ".env"), ".env"],
        extra="ignore",
        case_sensitive=False
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
