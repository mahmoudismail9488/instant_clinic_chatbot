"""Application settings loaded from backend/app/.env."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str = ""
    groq_ai_model: str = "openai/gpt-oss-120b"
    groq_base_url: str = "https://api.groq.com"

    # Local embeddings — Groq accounts do not expose an embedding model.
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    raw_guidelines_dir: Path = REPO_ROOT / "data" / "raw_guidelines"
    vector_index_dir: Path = REPO_ROOT / "data" / "index"

    chunk_size: int = 1200
    chunk_overlap: int = 200
    default_top_k: int = 5
    embed_batch_size: int = 64


@lru_cache
def get_settings() -> Settings:
    return Settings()
