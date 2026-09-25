"""Tests for Ingestion Center Telemetry and Control API (v1)."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.data_quality import IngestionRun

client = TestClient(app)


def test_list_ingestion_runs(db):
    """Verify paginated listing of ingestion runs."""
    run = IngestionRun(
        source_code="ogd",
        status="success",
        district="Madurai",
        records_fetched=10,
        records_ingested=10,
    )
    db.add(run)
    db.commit()

    response = client.get("/api/v1/ingestion/runs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    run_ids = [item["id"] for item in data["items"]]
    assert str(run.id) in run_ids


def test_get_ingestion_run_detail(db):
    """Verify retrieving detailed telemetry for a single run."""
    run = IngestionRun(
        source_code="agmarknet",
        status="partial",
        district="Salem",
        records_fetched=5,
        records_ingested=4,
        errors=["Market resolution ambiguity for raw_name='Unknown'"],
    )
    db.add(run)
    db.commit()

    response = client.get(f"/api/v1/ingestion/runs/{run.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(run.id)
    assert data["source_code"] == "agmarknet"
    assert data["status"] == "partial"
    assert len(data["errors"]) == 1


def test_statewide_freshness_endpoint(db):
    """Verify statewide coverage and freshness telemetry."""
    response = client.get("/api/v1/ingestion/freshness")
    assert response.status_code == 200
    data = response.json()
    assert data["total_districts"] == 38
    assert data["total_canonical_markets"] >= 38
    assert "all_time" in data
    assert "recent_7d" in data
    assert len(data["data_sources"]) >= 5
