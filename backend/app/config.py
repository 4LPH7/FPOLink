"""FPOLink TN — Application Configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Database
    DATABASE_URL: str = "postgresql://fpolink:fpolink@postgres:5432/fpolink"

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
