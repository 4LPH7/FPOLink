"""Missed-run check behind the daily price catch-up on hosts that sleep (Render free plan)."""

from datetime import datetime, timedelta

import pytest

from app.config import settings
from app.models.data_quality import IngestionRun
from app.worker import IST, price_run_missed

# A far-future day keeps these rows clear of real runs other tests may leave behind.
SEVEN_AM = datetime(2099, 1, 2, 7, 0, tzinfo=IST)


@pytest.fixture(autouse=True)
def six_am_slot(monkeypatch):
    monkeypatch.setattr(settings, "PRICE_INGEST_HOUR_IST", 6)
    monkeypatch.setattr(settings, "PRICE_INGEST_MINUTE_IST", 0)


def add_run(db, started_at, completed=True, district="statewide"):
    finished = started_at + timedelta(minutes=10) if completed else None
    db.add(
        IngestionRun(
            source_code="auto",
            status="success" if completed else "running",
            district=district,
            started_at=started_at,
            completed_at=finished,
        )
    )
    db.flush()


def test_missed_when_last_run_was_yesterday(db):
    add_run(db, SEVEN_AM - timedelta(days=1))
    assert price_run_missed(db, now=SEVEN_AM) is True


def test_not_missed_after_todays_completed_run(db):
    add_run(db, SEVEN_AM - timedelta(minutes=45))  # 06:15
    assert price_run_missed(db, now=SEVEN_AM) is False


def test_run_cut_off_by_sleep_does_not_count(db):
    add_run(db, SEVEN_AM - timedelta(minutes=45), completed=False)
    assert price_run_missed(db, now=SEVEN_AM) is True


def test_single_district_run_does_not_count(db):
    add_run(db, SEVEN_AM - timedelta(minutes=45), district="Erode")
    assert price_run_missed(db, now=SEVEN_AM) is True


def test_before_todays_slot_checks_yesterdays(db):
    add_run(db, SEVEN_AM - timedelta(days=1))  # yesterday 07:00
    assert price_run_missed(db, now=SEVEN_AM - timedelta(hours=2)) is False  # 05:00
