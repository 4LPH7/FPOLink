from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_success():
    """Verify /api/health returns 200 and db: ok when database engine succeeds."""
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn

    with patch("app.database.engine.connect", return_value=mock_conn):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "fpolink-api"
        assert data["db"] == "ok"


def test_health_check_db_failure():
    """Verify /api/health returns 503 and db: error when database engine fails."""
    with patch("app.database.engine.connect", side_effect=Exception("Connection refused")):
        response = client.get("/api/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["db"] == "error"
        assert "Connection refused" in data["detail"]


@pytest.mark.anyio
async def test_sentry_init_in_lifespan_when_dsn_configured():
    """Verify lifespan initializes Sentry when SENTRY_DSN is set."""
    from app.main import lifespan

    mock_sentry = MagicMock()
    with patch("app.config.settings.SENTRY_DSN", "https://mock@sentry.io/123"):
        with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
            async with lifespan(app):
                mock_sentry.init.assert_called_once()
                _, kwargs = mock_sentry.init.call_args
                assert kwargs["dsn"] == "https://mock@sentry.io/123"


@pytest.mark.anyio
async def test_sentry_skipped_when_dsn_empty():
    """Verify lifespan skips Sentry when SENTRY_DSN is None or empty."""
    from app.main import lifespan

    mock_sentry = MagicMock()
    with patch("app.config.settings.SENTRY_DSN", None):
        with patch.dict("sys.modules", {"sentry_sdk": mock_sentry}):
            async with lifespan(app):
                mock_sentry.init.assert_not_called()


def test_env_example_contains_all_critical_settings():
    """Verify .env.example contains all critical Settings fields (T5.7 Nyquist check)."""
    import pathlib

    repo_root = pathlib.Path(__file__).resolve().parent.parent.parent
    candidate_paths = [
        repo_root / ".env.example",
        pathlib.Path(__file__).resolve().parent.parent / ".env.example",
        pathlib.Path("/app/.env.example"),
    ]
    env_file = next((p for p in candidate_paths if p.exists()), None)
    if not env_file:
        pytest.skip(".env.example not mounted in isolated container environment")

    env_example = env_file.read_text(encoding="utf-8")

    critical_keys = [
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "ENVIRONMENT",
        "SECRET_KEY",
        "WHATSAPP_ENABLED",
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_APP_SECRET",
        "WHATSAPP_ACCESS_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_BOT_PHONE",
        "WHATSAPP_API_VERSION",
        "WHATSAPP_RATE_SERVICE_INR",
        "WHATSAPP_RATE_UTILITY_INR",
        "WHATSAPP_RATE_MARKETING_INR",
        "WHATSAPP_RATE_AUTH_INR",
        "WHATSAPP_MONTHLY_SEND_CAP",
        "WHATSAPP_MONTHLY_BUDGET_INR",
        "WHATSAPP_MAX_CONSECUTIVE_FAILURES",
        "WHATSAPP_PRICE_MOVE_THRESHOLD_PCT",
        "SENTRY_DSN",
    ]

    for key in critical_keys:
        assert f"{key}=" in env_example, f"Missing critical setting {key} in .env.example"
