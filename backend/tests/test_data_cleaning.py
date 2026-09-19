"""Tests for data cleaning, validation, and MAD anomaly detection."""

from datetime import date
from decimal import Decimal

from app.data_sources.base import PriceRecord
from app.services.data_cleaning import clean_price_records, detect_anomaly_mad


def test_detect_anomaly_mad_normal():
    prices = [Decimal("140"), Decimal("142"), Decimal("141"), Decimal("143"), Decimal("140")]
    anomalies = detect_anomaly_mad(prices, threshold=3.0)
    assert not any(anomalies)


def test_detect_anomaly_mad_outlier():
    # 350 is a sharp spike compared to median ~140
    prices = [
        Decimal("140"),
        Decimal("142"),
        Decimal("141"),
        Decimal("143"),
        Decimal("140"),
        Decimal("350"),
    ]
    anomalies = detect_anomaly_mad(prices, threshold=3.0)
    assert anomalies[-1] is True
    assert not any(anomalies[:-1])


def test_detect_anomaly_mad_short_list():
    prices = [Decimal("140"), Decimal("150")]
    anomalies = detect_anomaly_mad(prices)
    assert anomalies == [False, False]


def test_detect_anomaly_mad_identical_prices():
    prices = [Decimal("150"), Decimal("150"), Decimal("150"), Decimal("150")]
    anomalies = detect_anomaly_mad(prices)
    assert anomalies == [False, False, False, False]


def test_clean_price_records_validation():
    valid_record = PriceRecord(
        crop_name="Turmeric",
        market_name="Erode",
        district="Erode",
        modal_price=Decimal("150.00"),
        min_price=Decimal("140.00"),
        max_price=Decimal("160.00"),
        price_date=date(2026, 9, 1),
        source="test",
    )
    invalid_record = PriceRecord(
        crop_name="Turmeric",
        market_name="Erode",
        district="Erode",
        modal_price=Decimal("-10.00"),  # invalid negative
        price_date=date(2026, 9, 1),
        source="test",
    )

    cleaned = clean_price_records([valid_record, invalid_record])
    assert len(cleaned) == 1
    assert cleaned[0].crop_name == "turmeric"  # normalized lowercase
