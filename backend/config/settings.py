from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str
    JINA_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    PRIMARY_MODEL: str = "llama-3.3-70b-versatile"
    FALLBACK_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "jina-embeddings-v3"
    CHROMA_BACKEND: str = "cloud"
    CHROMA_HOST: str = "api.trychroma.com"
    CHROMA_PORT: int = 443
    CHROMA_SSL: bool = True
    CHROMA_API_KEY: str | None = None
    CHROMA_TENANT: str | None = None
    CHROMA_DATABASE: str | None = None
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    MAX_HISTORY_TURNS: int = 10
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_ORIGINS: str = "http://localhost:8501"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
