from typing import List, Optional
from urllib.parse import unquote, urlsplit

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
            placeholder_markers = ("change-me", "placeholder", "example", "replace-me", "default")
            if len(self.SECRET_KEY) < 32 or any(
                marker in self.SECRET_KEY.lower() for marker in placeholder_markers
            ):
                raise ValueError(
                    "FATAL SECURITY ERROR: production SECRET_KEY must be at least 32 characters "
                    "and must not contain a placeholder value."
                )
            db_password = unquote(urlsplit(self.DATABASE_URL).password or "")
            if len(db_password) < 16 or db_password.lower() in {
                "fpolink",
                "password",
                "postgres",
                "admin",
                "changeme",
            }:
                raise ValueError(
                    "FATAL SECURITY ERROR: production database password must be at least "
                    "16 characters and must not be a common default."
                )
            if self.DEMO_MODE:
                raise ValueError(
                    "FATAL SECURITY ERROR: DEMO_MODE cannot be enabled in production. "
                    "Production environments must only serve verified market price data."
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

    # WhatsApp Cloud API (disabled by default: the MVP ships with Telegram as the farmer channel)
    WHATSAPP_ENABLED: bool = False  # Kill switch
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

    # Database pool (Render free Postgres allows few connections)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5

    # Demo mode: serve clearly-labelled demo_seed prices so a fresh test deployment is populated.
    # Never enable for a real pilot; real sources (ogd/ceda/agmarknet) always take precedence.
    DEMO_MODE: bool = False

    # Run the APScheduler jobs inside the API process (free hosts without background workers).
    RUN_SCHEDULER: bool = False

    # Telegram bot (farmer channel)
    TELEGRAM_ENABLED: bool = True
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_BOT_USERNAME: str = "Fpo_Link_Bot"
    # Secret echoed by Telegram in X-Telegram-Bot-Api-Secret-Token; derived from token if empty.
    TELEGRAM_WEBHOOK_SECRET: str = ""
    # Public HTTPS base URL of this API. On Render, RENDER_EXTERNAL_URL is used automatically.
    PUBLIC_API_URL: str = ""
    # Register the webhook with Telegram on startup when a public URL is known.
    TELEGRAM_AUTO_SET_WEBHOOK: bool = True
    # Auto-create a farmer profile when an unknown Telegram user shares their phone contact.
    TELEGRAM_AUTO_REGISTER: bool = True

    # External Services
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OGD_API_KEY: str = ""  # data.gov.in Open Government Data API key
    CEDA_API_KEY: str = ""  # Centre for Economic Data & Analysis API key

    # Geography & Scope
    STATE: str = "Tamil Nadu"
    DEFAULT_DISTRICT: str = "Erode"
    DEFAULT_CROPS: str = (
        "turmeric,banana,coconut,paddy,groundnut,tomato,small onion,onion,"
        "green chilli,red chilli,maize,cotton,sugarcane,black gram,green gram,"
        "tapioca,mango,brinjal,ladies finger,ginger"
    )

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    # Regex for additional allowed origins (scoped to FPOLink Vercel previews).
    CORS_ORIGIN_REGEX: str = r"^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$"

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

    # Admin Phone & Seed Password
    ADMIN_PHONE: str = "8072845239"
    SEED_ADMIN_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
