from __future__ import annotations

import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "AI Interview Studio"
    app_env: str = "development"
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/interview_studio"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = 180.0

    cors_origins: list[str] | str = Field(default_factory=lambda: ["http://localhost:3000"])
    sql_echo: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, list):
            return value
        raw_value = value.strip()
        if not raw_value:
            return []
        if raw_value.startswith("["):
            return json.loads(raw_value)
        return [item.strip() for item in raw_value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
