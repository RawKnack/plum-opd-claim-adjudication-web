from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] = assignment package root
ASSIGNMENT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Plum OPD Claim Adjudication API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # SQLite works without Docker; set DATABASE_URL in .env for Postgres + pgvector
    database_url: str = "postgresql+psycopg2://plum:plum@localhost:5433/plum_claims"
    upload_dir: Path = Path("uploads")
    max_upload_size_mb: int = 10
    allowed_upload_extensions: set[str] = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".tiff",
    }

    policy_terms_path: Path = ASSIGNMENT_ROOT / "policy_terms.json"
    adjudication_rules_path: Path = ASSIGNMENT_ROOT / "adjudication_rules.md"

    openai_api_key: str | None = None
    google_vision_api_key: str | None = None
    gemini_api_key: str | None = None
    ocr_confidence_fallback_threshold: float = 0.60
    llm_reasoning_confidence_threshold: float = 0.70

    use_s3: bool = False
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_bucket: str | None = None
    aws_region: str = "ap-south-1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
