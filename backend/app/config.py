from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Database
    DATABASE_URL: str = "postgresql+psycopg://fpolink:fpolink@postgres:5432/fpolink"

    @field_validator("DATABASE_URL")
    @classmethod
    def use_psycopg3(cls, v: str) -> str:
        for old in ("postgresql://", "postgres://"):
            if v.startswith(old):
                return v.replace(old, "postgresql+psycopg://", 1)
        return v

    # Authentication
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # External Services
    TELEGRAM_BOT_TOKEN: str = ""
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OGD_API_KEY: str = ""  # data.gov.in Open Government Data API key

    # Geography & Scope
    STATE: str = "Tamil Nadu"
    DEFAULT_DISTRICT: str = "Erode"
    DEFAULT_CROPS: List[str] = ["turmeric", "banana", "coconut"]

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Sentry (optional error monitoring)
    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
