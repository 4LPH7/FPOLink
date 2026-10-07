"""Tests for OGD (Open Government Data) data source adapter and CLI harness."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import respx
import httpx

from app.config import settings
from app.data_sources.ogd import OGD_BASE_URL, OGDProvider
from scripts.ingest_ogd import check_status, load_fixture_records


@pytest.fixture
def ogd_synthetic_fixture():
    fixture_path = (
        Path(__file__).resolve().parent / "fixtures" / "ogd_turmeric_response_synthetic.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_ogd_provider_custom_resource_id():
    custom_res_id = "test-custom-resource-id-123"
    provider = OGDProvider(api_key="test-api-key", resource_id=custom_res_id)
    assert provider.resource_id == custom_res_id
    assert provider.is_available() is True


def test_ogd_provider_default_resource_id():
    provider = OGDProvider(api_key="test-api-key")
    assert provider.resource_id == settings.OGD_RESOURCE_ID


@respx.mock
def test_ogd_fetch_prices_mocked_http(ogd_synthetic_fixture):
    resource_id = "test-resource-id"
    provider = OGDProvider(api_key="test-key", resource_id=resource_id)

    respx.get(f"{OGD_BASE_URL}/{resource_id}").mock(
        return_value=httpx.Response(200, json=ogd_synthetic_fixture)
    )

    records = provider.fetch_prices(
        crop="Turmeric",
        district="Erode",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    assert len(records) == 3
    rec1 = records[0]
    assert rec1.crop_name == "turmeric"
    assert rec1.district == "Erode"
    assert rec1.market_name == "Erode"
    assert rec1.variety_name == "Finger"
    assert rec1.price_date == date(2026, 1, 15)
    # 15100 quintal -> 151 per kg
    assert rec1.modal_price == Decimal("151")
    assert rec1.source == "ogd"


def test_ogd_load_fixture_records_direct():
    fixture_path = (
        Path(__file__).resolve().parent / "fixtures" / "ogd_turmeric_response_synthetic.json"
    )
    records = load_fixture_records(fixture_path, crop="Turmeric", district="Erode")
    assert len(records) == 3
    markets = {r.market_name for r in records}
    assert "Erode" in markets
    assert "Perundurai" in markets


def test_ogd_check_status_configured():
    assert check_status(api_key="mock-key-123") is True
    assert check_status(api_key="") is False
