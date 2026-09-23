from typing import List, Optional

from pydantic import field_validator, model_validator
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

    ENVIRONMENT: str = "development"

    # Authentication
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            if self.SECRET_KEY == "change-me-in-production":
                raise ValueError(
                    "FATAL SECURITY ERROR: SECRET_KEY is set to default 'change-me-in-production' "
                    "while ENVIRONMENT is 'production'. The application refuses to start."
                )
            if self.WHATSAPP_ENABLED:
                missing_wa = []
                if not self.WHATSAPP_VERIFY_TOKEN:
                    missing_wa.append("WHATSAPP_VERIFY_TOKEN")
                if not self.WHATSAPP_APP_SECRET:
                    missing_wa.append("WHATSAPP_APP_SECRET")
                if not self.WHATSAPP_ACCESS_TOKEN:
                    missing_wa.append("WHATSAPP_ACCESS_TOKEN")
                if not self.WHATSAPP_PHONE_NUMBER_ID:
                    missing_wa.append("WHATSAPP_PHONE_NUMBER_ID")
                if missing_wa:
                    raise ValueError(
                        f"FATAL SECURITY ERROR: WHATSAPP_ENABLED is True in production, but the following "
                        f"required secrets are missing: {', '.join(missing_wa)}. Refusing to start."
                    )
        elif self.SECRET_KEY == "change-me-in-production":
            import logging

            logging.getLogger("app.config").warning(
                "SECURITY WARNING: SECRET_KEY is set to default 'change-me-in-production'. "
                "Set a secure, long random string in production via .env or environment variable."
            )
        return self

    # WhatsApp Cloud API
    WHATSAPP_ENABLED: bool = True  # Kill switch
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BOT_PHONE: str = "919876543210"
    WHATSAPP_API_VERSION: str = "v23.0"

    # WhatsApp Pricing & Cost Control (T4.4)
    WHATSAPP_RATE_SERVICE_INR: float = 0.00
    WHATSAPP_RATE_UTILITY_INR: float = 0.35
    WHATSAPP_RATE_MARKETING_INR: float = 0.85
    WHATSAPP_RATE_AUTH_INR: float = 0.15
    WHATSAPP_MONTHLY_SEND_CAP: int = 5000
    WHATSAPP_MONTHLY_BUDGET_INR: float = 2000.0
    WHATSAPP_MAX_CONSECUTIVE_FAILURES: int = 3
    WHATSAPP_PRICE_MOVE_THRESHOLD_PCT: float = 5.0

    # External Services
    TELEGRAM_BOT_TOKEN: str = ""
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OGD_API_KEY: str = ""  # data.gov.in Open Government Data API key
    CEDA_API_KEY: str = ""  # Centre for Economic Data & Analysis API key

    # Geography & Scope
    STATE: str = "Tamil Nadu"
    DEFAULT_DISTRICT: str = "Erode"
    DEFAULT_CROPS: str = "turmeric,banana,coconut"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def default_crops_list(self) -> List[str]:
        raw = self.DEFAULT_CROPS.strip()
        if raw.startswith("[") and raw.endswith("]"):
            import json

            try:
                return json.loads(raw)
            except Exception:
                pass
        return [c.strip() for c in raw.split(",") if c.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        raw = self.CORS_ORIGINS.strip()
        if raw.startswith("[") and raw.endswith("]"):
            import json

            try:
                return json.loads(raw)
            except Exception:
                pass
        return [c.strip() for c in raw.split(",") if c.strip()]

    # Sentry (optional error monitoring)
    SENTRY_DSN: Optional[str] = None

    # Seed Admin Password
    SEED_ADMIN_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
