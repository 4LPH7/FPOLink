"""Tests for production security enforcement in configuration."""

import pytest
from pydantic_core import ValidationError

from app.config import Settings


def test_production_refuses_default_secret_key():
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="change-me-in-production",
            DATABASE_URL="postgresql+psycopg://fpolink:ci-database-password-123@localhost/fpolink",
        )
    assert "FATAL SECURITY ERROR" in str(exc_info.value)


def test_production_accepts_strong_secret_key():
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-secure-random-production-key-32-chars-long",
        DATABASE_URL="postgresql+psycopg://fpolink:ci-database-password-123@localhost/fpolink",
        WHATSAPP_ENABLED=False,
    )
    assert settings.ENVIRONMENT == "production"
    assert settings.SECRET_KEY == "a-secure-random-production-key-32-chars-long"


def test_production_rejects_example_secret_key():
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="change-me-in-production-use-a-long-random-string",
            DATABASE_URL="postgresql+psycopg://fpolink:ci-database-password-123@localhost/fpolink",
            WHATSAPP_ENABLED=False,
        )
    assert "FATAL SECURITY ERROR" in str(exc_info.value)


def test_production_rejects_default_database_password():
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 64,
            DATABASE_URL="postgresql+psycopg://fpolink:fpolink@localhost/fpolink",
            WHATSAPP_ENABLED=False,
        )
    assert "database password" in str(exc_info.value)


def test_production_rejects_demo_mode():
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="a" * 64,
            DATABASE_URL="postgresql+psycopg://fpolink:ci-database-password-123@localhost/fpolink",
            DEMO_MODE=True,
            WHATSAPP_ENABLED=False,
        )
    assert "DEMO_MODE cannot be enabled in production" in str(exc_info.value)


def test_development_allows_default_secret_key(caplog):
    settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="change-me-in-production",
    )
    assert settings.ENVIRONMENT == "development"
