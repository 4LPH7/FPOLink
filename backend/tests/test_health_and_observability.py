"""Tests for health check endpoint and observability components (T5.5)."""

from unittest.mock import MagicMock, patch

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
