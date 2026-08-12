from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "stub"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    database_url: str = "sqlite+aiosqlite:///./sodio.db"
    cors_origins: str = "http://localhost:5173"
    batch_concurrency: int = 4
    extraction_prompt_version: str = "v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
