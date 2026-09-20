"""Unit and contract tests for CEDA Data Portal API provider."""

import json
from datetime import date
from decimal import Decimal

import pytest
import respx

from app.data_sources.ceda_api import CEDA_API_BASE_URL, CEDAAPIProvider


@pytest.fixture
def ceda_provider():
    return CEDAAPIProvider(api_key="test_ceda_key_12345", timeout=5.0)


@respx.mock
def test_ceda_get_commodities(ceda_provider):
    """Assert commodities endpoint returns list matching schema."""
    route = respx.get(f"{CEDA_API_BASE_URL}/agmarknet/commodities").respond(
        status_code=200,
        json={
            "commodities": [
                {"id": 1, "name": "Wheat"},
                {"id": 14, "name": "Turmeric"},
                {"id": 22, "name": "Banana"},
            ]
        },
    )

    items = ceda_provider.get_commodities()
    assert route.called
    req = route.calls.last.request
    assert req.headers["authorization"] == "Bearer test_ceda_key_12345"
    assert req.headers["accept"] == "application/json"
    assert len(items) == 3
    assert items[1]["name"] == "Turmeric"
    assert items[1]["id"] == 14


@respx.mock
def test_ceda_get_geographies(ceda_provider):
    """Assert geographies endpoint returns state and district hierarchy."""
    route = respx.get(f"{CEDA_API_BASE_URL}/agmarknet/geographies").respond(
        status_code=200,
        json={
            "geographies": [
                {
                    "state_id": 33,
                    "state_name": "Tamil Nadu",
                    "districts": [
                        {"district_id": 610, "district_name": "Erode"},
                        {"district_id": 608, "district_name": "Salem"},
                    ],
                }
            ]
        },
    )

    geos = ceda_provider.get_geographies()
    assert route.called
    assert len(geos) == 1
    assert geos[0]["state_name"] == "Tamil Nadu"
    assert len(geos[0]["districts"]) == 2


@respx.mock
def test_ceda_fetch_prices_contract(ceda_provider):
    """Assert prices endpoint posts exact schema and converts quintal to kg."""
    route = respx.post(f"{CEDA_API_BASE_URL}/agmarknet/prices").respond(
        status_code=200,
        json={
            "data": [
                {
                    "date": "2025-05-15",
                    "commodity_id": 14,
                    "census_state_id": 33,
                    "census_district_id": 610,
                    "market_id": 1205,
                    "market_name": "Erode Regulated Market",
                    "min_price": 12000,
                    "max_price": 14000,
                    "modal_price": 13000,
                }
            ]
        },
    )

    records = ceda_provider.fetch_prices(
        crop="turmeric",
        district="Erode",
        commodity_id=14,
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 31),
    )

    assert route.called
    req = route.calls.last.request
    req_body = json.loads(req.content)
    assert req_body == {
        "commodity_id": 14,
        "state_id": 33,
        "district_id": [610],
        "from_date": "2025-05-01",
        "to_date": "2025-05-31",
    }

    assert len(records) == 1
    rec = records[0]
    assert rec.crop_name == "turmeric"
    assert rec.district == "Erode"
    assert rec.market_name == "Erode Regulated Market"
    assert rec.price_date == date(2025, 5, 15)
    assert rec.source == "ceda"
    # Quintal to kg conversion: 13000 / 100 = 130
    assert rec.modal_price == Decimal("130.00")
    assert rec.min_price == Decimal("120.00")
    assert rec.max_price == Decimal("140.00")
    assert rec.raw_price == Decimal("13000")
    assert rec.raw_unit == "quintal"
