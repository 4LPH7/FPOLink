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


def get_latest_prices(
    db: Session,
    district: Optional[str] = None,
    crop_id: Optional[str] = None,
    min_quality: Optional[float] = None,
) -> List[dict]:
    """Get the most recent verified price for each crop in each market."""
    from app.config import settings

    # Subquery for max date per crop/market — whitelisting real sources only
    subq_filters = [MarketPrice.source.in_(REAL_PRICE_SOURCES)]
    if district and district.lower() != "all":
        subq_filters.append(func.lower(MarketPrice.district) == district.lower().strip())
    elif not district:
        subq_filters.append(MarketPrice.district == settings.DEFAULT_DISTRICT)

    if crop_id:
        subq_filters.append(MarketPrice.crop_id == crop_id)

    subq = (
        db.query(
            MarketPrice.crop_id,
            MarketPrice.market_id,
            func.max(MarketPrice.price_date).label("max_date"),
        )
        .filter(*subq_filters)
        .group_by(MarketPrice.crop_id, MarketPrice.market_id)
        .subquery()
    )

    query = (
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
    )
    if district and district.lower() != "all":
        query = query.filter(func.lower(MarketPrice.district) == district.lower().strip())
    elif not district:
        query = query.filter(MarketPrice.district == settings.DEFAULT_DISTRICT)

    if crop_id:
        query = query.filter(MarketPrice.crop_id == crop_id)

    results = query.all()

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
        if min_quality is not None:
            score = mp.quality_score if mp.quality_score is not None else 100.0
            if score < min_quality:
                continue

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
                "quality_score": mp.quality_score,
                "quality_breakdown": mp.quality_breakdown,
                "trend": trend,
            }
        )

    prices.sort(key=lambda x: (x["crop_name"], x["market_name"]))
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
            "quality_score": mp.quality_score,
        }
        for mp in sorted(date_map.values(), key=lambda x: x.price_date)
    ]


def get_quality_summary(
    db: Session,
    district: Optional[str] = None,
    days: int = 7,
) -> dict:
    """Summarize data quality metrics for market prices over recent window."""
    start_date = date.today() - timedelta(days=days)
    query = db.query(MarketPrice).filter(MarketPrice.price_date >= start_date)
    if district and district.lower() != "all":
        query = query.filter(func.lower(MarketPrice.district) == district.lower().strip())
    records = query.all()

    total = len(records)
    if total == 0:
        return {
            "total_records": 0,
            "average_quality_score": 0.0,
            "verified_count": 0,
            "good_count": 0,
            "limited_count": 0,
            "unreliable_count": 0,
            "by_source": {},
        }

    scores = [r.quality_score if r.quality_score is not None else 100.0 for r in records]
    avg_score = round(sum(scores) / total, 1)

    verified = sum(1 for s in scores if s >= 85.0)
    good = sum(1 for s in scores if 70.0 <= s < 85.0)
    limited = sum(1 for s in scores if 50.0 <= s < 70.0)
    unreliable = sum(1 for s in scores if s < 50.0)

    by_source = {}
    for r in records:
        src = r.source or "unknown"
        if src not in by_source:
            by_source[src] = {"count": 0, "total_score": 0.0}
        by_source[src]["count"] += 1
        by_source[src]["total_score"] += (r.quality_score if r.quality_score is not None else 100.0)

    for src, data in by_source.items():
        data["average_score"] = round(data["total_score"] / data["count"], 1)
        del data["total_score"]

    return {
        "total_records": total,
        "average_quality_score": avg_score,
        "verified_count": verified,
        "good_count": good,
        "limited_count": limited,
        "unreliable_count": unreliable,
        "by_source": by_source,
    }


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
