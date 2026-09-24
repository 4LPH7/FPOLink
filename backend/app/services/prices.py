"""Price service — price data retrieval, trends, and anomaly detection."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.sources import REAL_PRICE_SOURCES, get_source_priority
from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.services.data_cleaning import detect_anomaly_mad

logger = logging.getLogger(__name__)


def get_latest_prices(db: Session, district: Optional[str] = None) -> List[dict]:
    """Get the most recent verified price for each crop in each market."""
    from app.config import settings

    district = district or settings.DEFAULT_DISTRICT

    # Subquery for max date per crop/market — whitelisting real sources only
    subq = (
        db.query(
            MarketPrice.crop_id,
            MarketPrice.market_id,
            func.max(MarketPrice.price_date).label("max_date"),
        )
        .filter(
            MarketPrice.district == district,
            MarketPrice.source.in_(REAL_PRICE_SOURCES),
        )
        .group_by(MarketPrice.crop_id, MarketPrice.market_id)
        .subquery()
    )

    results = (
        db.query(MarketPrice, Crop, Market)
        .join(Crop, MarketPrice.crop_id == Crop.id)
        .join(Market, MarketPrice.market_id == Market.id)
        .join(
            subq,
            (MarketPrice.crop_id == subq.c.crop_id)
            & (MarketPrice.market_id == subq.c.market_id)
            & (MarketPrice.price_date == subq.c.max_date),
        )
        .filter(MarketPrice.source.in_(REAL_PRICE_SOURCES))
        .all()
    )

    # If both OGD and CEDA report on max_date, arbitrate using SOURCE_PRIORITY
    winner_per_pair = {}
    for mp, crop, market in results:
        pair_key = (mp.crop_id, mp.market_id)
        if pair_key not in winner_per_pair:
            winner_per_pair[pair_key] = (mp, crop, market)
        else:
            existing_mp, _, _ = winner_per_pair[pair_key]
            if get_source_priority(mp.source) < get_source_priority(existing_mp.source):
                winner_per_pair[pair_key] = (mp, crop, market)

    prices = []
    for mp, crop, market in winner_per_pair.values():
        # Calculate trend
        trend = _calculate_trend(db, mp.crop_id, mp.market_id, mp.price_date)

        prices.append(
            {
                "id": str(mp.id),
                "crop_id": str(mp.crop_id),
                "market_id": str(mp.market_id),
                "crop_name": crop.name,
                "crop_tamil_name": crop.tamil_name,
                "market_name": market.name,
                "district": mp.district,
                "min_price": mp.min_price,
                "max_price": mp.max_price,
                "modal_price": mp.modal_price,
                "price_date": mp.price_date,
                "source": mp.source,
                "arrival_quantity": mp.arrival_quantity,
                "trend": trend,
            }
        )

    return prices


def get_price_history(
    db: Session,
    crop_id: str,
    market_id: str,
    days: int = 30,
) -> List[dict]:
    """Get verified price history for a crop in a market."""
    start_date = date.today() - timedelta(days=days)

    results = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
            MarketPrice.price_date >= start_date,
            MarketPrice.source.in_(REAL_PRICE_SOURCES),
        )
        .order_by(MarketPrice.price_date)
        .all()
    )

    # Deduplicate dates if both OGD and CEDA exist for same date
    date_map = {}
    for mp in results:
        d = mp.price_date
        if d not in date_map or get_source_priority(mp.source) < get_source_priority(
            date_map[d].source
        ):
            date_map[d] = mp

    return [
        {
            "date": mp.price_date,
            "min_price": mp.min_price,
            "max_price": mp.max_price,
            "modal_price": mp.modal_price,
            "arrival_quantity": mp.arrival_quantity,
        }
        for mp in sorted(date_map.values(), key=lambda x: x.price_date)
    ]


def get_price_trend(
    db: Session,
    crop_id: str,
    market_id: str,
) -> Optional[dict]:
    """Calculate price trend (daily, weekly, monthly change)."""
    today = date.today()

    current = _get_price_on_date(db, crop_id, market_id, today)
    yesterday = _get_price_on_date(db, crop_id, market_id, today - timedelta(days=1))
    week_ago = _get_price_on_date(db, crop_id, market_id, today - timedelta(days=7))
    month_ago = _get_price_on_date(db, crop_id, market_id, today - timedelta(days=30))

    if not current:
        return None

    return {
        "current_price": current,
        "daily_change": _calc_change(current, yesterday),
        "weekly_change": _calc_change(current, week_ago),
        "monthly_change": _calc_change(current, month_ago),
    }


def check_anomalies(
    db: Session,
    crop_id: str,
    market_id: str,
    window: int = 30,
    threshold: float = 3.0,
) -> List[dict]:
    """Check for price anomalies using MAD z-score on verified records."""
    start_date = date.today() - timedelta(days=window)
    prices_rows = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
            MarketPrice.price_date >= start_date,
            MarketPrice.source.in_(REAL_PRICE_SOURCES),
        )
        .order_by(MarketPrice.price_date)
        .all()
    )

    if not prices_rows:
        return []

    prices = [row.modal_price for row in prices_rows]
    anomalies = detect_anomaly_mad(prices, threshold)

    results = []
    for row, is_anomaly in zip(prices_rows, anomalies):
        if is_anomaly:
            results.append(
                {
                    "date": row.price_date,
                    "price": row.modal_price,
                    "source": row.source,
                }
            )

    return results


def _calculate_trend(db: Session, crop_id, market_id, current_date: date) -> dict:
    """Calculate % change from previous day."""
    prev = _get_price_on_date(db, crop_id, market_id, current_date - timedelta(days=1))
    current = _get_price_on_date(db, crop_id, market_id, current_date)
    return _calc_change(current, prev)


def _get_price_on_date(db: Session, crop_id, market_id, target_date: date) -> Optional[Decimal]:
    """Get modal price on or near a date from verified sources."""
    from sqlalchemy import case

    source_precedence = case(
        (MarketPrice.source == "ogd", 1),
        (MarketPrice.source == "ceda", 2),
        else_=99,
    )

    for offset in range(4):
        d = target_date - timedelta(days=offset)
        mp = (
            db.query(MarketPrice.modal_price)
            .filter(
                MarketPrice.crop_id == crop_id,
                MarketPrice.market_id == market_id,
                MarketPrice.price_date == d,
                MarketPrice.source.in_(REAL_PRICE_SOURCES),
            )
            .order_by(source_precedence.asc())
            .first()
        )
        if mp:
            return mp[0]
    return None


def _calc_change(current: Optional[Decimal], previous: Optional[Decimal]) -> dict:
    if current is None or previous is None or previous == 0:
        return {"amount": Decimal("0"), "percent": 0.0, "direction": "stable"}
    change = current - previous
    pct = float(change / previous * 100)
    direction = "up" if change > 0 else "down" if change < 0 else "stable"
    return {"amount": change, "percent": round(pct, 2), "direction": direction}
