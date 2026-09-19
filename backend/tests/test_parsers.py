"""Tests for data source parsers and feature generators using fixtures."""

import csv
import tempfile
from datetime import date
from decimal import Decimal

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
