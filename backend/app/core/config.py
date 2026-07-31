from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed application configuration."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+asyncpg://simulator:simulator@localhost:5432/simulator"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    log_level: str = "INFO"
    model_provider: str = "disabled"
    model_api_key: str | None = None
    model_base_url: str = "https://api.openai.com"
    model_id: str = "gpt-4.1-mini-2025-04-14"
    model_timeout_seconds: float = 15.0
    model_max_attempts: int = 2
    model_max_output_tokens: int = 300
    world_runtime_enabled: bool = False
    study_enrollment_enabled: bool = False
    study_admin_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable settings instance."""
    return Settings()
