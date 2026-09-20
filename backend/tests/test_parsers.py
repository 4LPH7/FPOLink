"""Tests for data source parsers and feature generators using fixtures."""

import csv
import json
import os
import tempfile
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.data_sources.ceda import CEDAProvider
from app.data_sources.holidays_tn import (
    days_to_nearest_festival,
    get_festival_features,
    is_festival,
)
from app.data_sources.ogd import OGDProvider


def test_ceda_parser_with_sample_csv():
    # Sample CEDA CSV data with Rs/quintal
    sample_rows = [
        {
            "State": "Tamil Nadu",
            "District": "Erode",
            "Market": "Erode",
            "Commodity": "Turmeric",
            "Variety": "Finger",
            "Grade": "FAQ",
            "Min Price": "14000",
            "Max Price": "16000",
            "Modal Price": "15000",
            "Date": "2024-01-15",
            "Arrival": "120.5",
        },
        {
            "State": "Tamil Nadu",
            "District": "Erode",
            "Market": "Gobichettipalayam",
            "Commodity": "Banana",
            "Variety": "Nendran",
            "Grade": "FAQ",
            "Min Price": "3000",
            "Max Price": "3500",
            "Modal Price": "3200",
            "Date": "2024-01-16",
            "Arrival": "80",
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_file = f"{tmpdir}/turmeric_ceda_data.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(sample_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sample_rows)

        provider = CEDAProvider(data_dir=tmpdir)
        records = provider.fetch_prices("turmeric", "Erode")

        assert len(records) == 1
        record = records[0]
        assert record.crop_name == "turmeric"
        assert record.market_name == "Erode"
        assert record.district == "Erode"
        assert record.variety_name == "Finger"
        # 15000 Rs / quintal -> 150 Rs / kg
        assert record.modal_price == Decimal("150")
        assert record.min_price == Decimal("140")
        assert record.max_price == Decimal("160")
        assert record.price_date == date(2024, 1, 15)
        assert record.source == "ceda"
        assert record.raw_payload is not None


def test_ceda_parser_with_synthetic_fixture():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    provider = CEDAProvider(data_dir=fixtures_dir)

    # 1. Turmeric in Erode
    turmeric_records = provider.fetch_prices("turmeric", "Erode")
    assert len(turmeric_records) == 6

    # Verify first turmeric record
    r0 = turmeric_records[0]
    assert r0.crop_name == "turmeric"
    assert r0.market_name == "Erode"
    assert r0.variety_name == "Finger"
    assert r0.modal_price == Decimal("154")  # 15400 / 100
    assert r0.min_price == Decimal("145")
    assert r0.max_price == Decimal("162")
    assert r0.price_date == date(2024, 1, 15)
    assert r0.arrival_quantity == 125.5
    assert r0.source == "ceda_synthetic"

    # Verify variety parsing across records
    varieties = {r.variety_name for r in turmeric_records}
    assert "Finger" in varieties
    assert "Bulb" in varieties

    # Verify market parsing across records
    markets = {r.market_name for r in turmeric_records}
    assert "Erode" in markets
    assert "Perundurai" in markets

    # 2. Banana in Erode
    banana_records = provider.fetch_prices("banana", "Erode")
    assert len(banana_records) == 3
    banana_varieties = {r.variety_name for r in banana_records}
    assert "Poovan" in banana_varieties
    assert "Nendran" in banana_varieties
    assert banana_records[0].modal_price == Decimal("25")  # 2500 / 100


def test_ogd_record_parser():
    provider = OGDProvider(api_key="test_key")
    sample_record = {
        "State": "Tamil Nadu",
        "District": "Erode",
        "Market": "Erode",
        "Commodity": "Turmeric",
        "Variety": "Bulb",
        "Arrival_Date": "15/01/2026",
        "Min_x0020_Price": "13500",
        "Max_x0020_Price": "14500",
        "Modal_x0020_Price": "14000",
    }

    parsed = provider._parse_record(sample_record, "turmeric", "Erode")
    assert parsed is not None
    assert parsed.crop_name == "turmeric"
    assert parsed.variety_name == "Bulb"
    assert parsed.modal_price == Decimal("140")
    assert parsed.price_date == date(2026, 1, 15)
    assert parsed.source == "ogd"


def test_ogd_parser_with_synthetic_fixture():
    fixtures_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "ogd_turmeric_response_synthetic.json"
    )
    with open(fixtures_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    provider = OGDProvider(api_key="mock_key")
    records = []
    for raw in data.get("records", []):
        parsed = provider._parse_record(raw, "turmeric", "Erode")
        if parsed:
            records.append(parsed)

    # 3 turmeric records match
    assert len(records) == 3
    varieties = {r.variety_name for r in records}
    assert "Finger" in varieties
    assert "Bulb" in varieties
    assert "Local" in varieties

    # Check price conversion
    finger_record = next(r for r in records if r.variety_name == "Finger")
    assert finger_record.modal_price == Decimal("151")  # 15100 / 100
    assert finger_record.min_price == Decimal("142")
    assert finger_record.max_price == Decimal("158")
    assert finger_record.price_date == date(2026, 1, 15)


def test_ogd_fetch_prices_mocked():
    fixtures_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "ogd_turmeric_response_synthetic.json"
    )
    with open(fixtures_path, "r", encoding="utf-8") as f:
        fixture_data = json.load(f)

    provider = OGDProvider(api_key="real_mock_key")

    mock_resp = MagicMock()
    mock_resp.json.return_value = fixture_data
    mock_resp.raise_for_status.return_value = None

    with patch("httpx.Client.get", return_value=mock_resp):
        records = provider.fetch_prices("turmeric", "Erode")
        assert len(records) == 3
        assert all(r.district == "Erode" for r in records)
        assert all(r.source == "ogd" for r in records)


def test_tn_festival_features():
    # Pongal: Jan 15
    pongal_date = date(2026, 1, 15)
    assert is_festival(pongal_date) is True

    # Check festival features dictionary
    features = get_festival_features(pongal_date)
    assert features["is_festival"] == 1
    assert features["is_pongal_week"] == 1
    assert features["days_to_festival"] == 0

    # Date close to Pongal (Jan 10 -> 5 days to Pongal)
    pre_pongal = date(2026, 1, 10)
    assert days_to_nearest_festival(pre_pongal) <= 5
