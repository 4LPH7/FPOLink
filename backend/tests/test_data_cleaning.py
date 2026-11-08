"""Tests for data cleaning, validation, and MAD anomaly detection."""

from decimal import Decimal

from app.services.data_cleaning import detect_anomaly_mad


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
