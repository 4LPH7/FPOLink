"""Admin endpoints — manual ingestion trigger, system status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.user import User
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
def trigger_ingestion(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Manually trigger price data ingestion (admin only)."""
    service = IngestionService(db)
    result = service.run_ingestion()
    return {"message": "Ingestion completed", "result": result}


@router.post("/weather/ingest")
def trigger_weather_ingest(
    district: str = "all",
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "data_operator"])),
):
    """Trigger live weather forecast ingestion from Open-Meteo for a district or statewide."""
    from app.models.geography import District
    from app.services.weather_service import WeatherService

    service = WeatherService(db)
    if district.lower() in ("all", "statewide"):
        district_rows = db.query(District.name).order_by(District.name).all()
        target_districts = [d[0] for d in district_rows] if district_rows else ["Erode"]
        total_count = 0
        for d in target_districts:
            try:
                total_count += service.ingest_forecast(district=d, days=days)
            except Exception:
                pass
        return {
            "message": f"Successfully ingested {total_count} forecast days across {len(target_districts)} districts",
            "district": "statewide",
            "days_ingested": total_count,
        }

    count = service.ingest_forecast(district=district, days=days)
    return {
        "message": f"Successfully ingested {count} forecast days for {district}",
        "district": district,
        "days_ingested": count,
    }


@router.post("/purge-testing-data")
def purge_testing_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Purge synthetic/demo test data so only real ground-truth data remains."""
    from app.models.market_price import MarketPrice
    from app.models.weather import WeatherData

    deleted_prices = (
        db.query(MarketPrice)
        .filter(
            (MarketPrice.source.in_(("seed_demo", "demo_seed")))
            | (MarketPrice.source.like("%synthetic%"))
            | (MarketPrice.source.like("%sample%"))
            | (MarketPrice.source.like("%test%"))
        )
        .delete(synchronize_session=False)
    )

    deleted_weather = (
        db.query(WeatherData)
        .filter(WeatherData.source.in_(("seed", "synthetic", "sample")))
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "status": "success",
        "purged_prices": deleted_prices,
        "purged_weather": deleted_weather,
        "message": f"Successfully purged {deleted_prices} test price records and {deleted_weather} test weather records.",
    }


@router.post("/retention/purge")
def trigger_retention_purge(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Manually trigger DPDP retention purge."""
    from app.services.retention import (
        purge_conversation_state,
        purge_inbound,
        purge_outbound,
    )

    inbound_count = purge_inbound(retention_days=7)
    state_count = purge_conversation_state(ttl_hours=24)
    outbound_count = purge_outbound(retention_months=12)

    return {
        "message": "DPDP retention purge completed",
        "purged": {
            "inbound": inbound_count,
            "conversation_state": state_count,
            "outbound": outbound_count,
        },
    }


@router.get("/data-health")
def get_data_health(
    days: int = 14,
    district: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "state_admin", "fpo_admin", "data_operator"])
    ),
):
    """System-wide data health report: rows/market/day, calendar gaps, and outlier detections."""
    from collections import defaultdict
    from datetime import date, datetime, timedelta, timezone
    from sqlalchemy import desc, func
    from app.models.data_quality import DataQualityEvent
    from app.models.market import Market
    from app.models.market_price import MarketPrice

    today = date.today()
    start_date = today - timedelta(days=days)

    query = (
        db.query(
            Market.name.label("market_name"),
            MarketPrice.district,
            MarketPrice.price_date,
            func.count(MarketPrice.id).label("row_count"),
            func.count(func.distinct(MarketPrice.crop_id)).label("crop_count"),
            func.avg(MarketPrice.quality_score).label("avg_quality"),
        )
        .join(Market, MarketPrice.market_id == Market.id)
        .filter(MarketPrice.price_date >= start_date)
    )
    if district and district.lower() not in ("all", "statewide", ""):
        query = query.filter(func.lower(MarketPrice.district) == district.lower().strip())

    rows = (
        query.group_by(Market.name, MarketPrice.district, MarketPrice.price_date)
        .order_by(desc(MarketPrice.price_date), Market.name)
        .all()
    )

    rows_per_market_per_day = [
        {
            "market_name": r.market_name,
            "district": r.district,
            "date": r.price_date.isoformat(),
            "row_count": r.row_count,
            "crop_count": r.crop_count,
            "avg_quality": round(float(r.avg_quality), 1) if r.avg_quality is not None else 100.0,
        }
        for r in rows
    ]

    # Calendar gap detection (Mon-Sat trading days)
    market_dates = defaultdict(set)
    for r in rows:
        market_dates[(r.market_name, r.district)].add(r.price_date)

    expected_trading_days = []
    curr = start_date
    while curr <= today:
        if curr.weekday() != 6:  # skip Sunday
            expected_trading_days.append(curr)
        curr += timedelta(days=1)

    gap_list = []
    for (m_name, dist), dates_seen in market_dates.items():
        missing = sorted(set(expected_trading_days) - dates_seen)
        if missing:
            gap_list.append(
                {
                    "market_name": m_name,
                    "district": dist,
                    "missing_dates": [d.isoformat() for d in missing],
                    "gap_count": len(missing),
                }
            )

    # Outliers and DataQualityEvents
    dq_since = datetime.now(timezone.utc) - timedelta(days=days)
    dq_events = (
        db.query(DataQualityEvent)
        .filter(DataQualityEvent.created_at >= dq_since)
        .order_by(desc(DataQualityEvent.created_at))
        .all()
    )
    issue_counts = defaultdict(int)
    for ev in dq_events:
        issue_counts[ev.issue_type] += 1

    # Source breakdown
    source_stats = (
        db.query(MarketPrice.source, func.count(MarketPrice.id))
        .filter(MarketPrice.price_date >= start_date)
        .group_by(MarketPrice.source)
        .all()
    )
    coverage_by_source = {src: count for src, count in source_stats}

    total_obs = sum(r["row_count"] for r in rows_per_market_per_day)
    avg_score = (
        round(
            sum(r["avg_quality"] * r["row_count"] for r in rows_per_market_per_day) / total_obs,
            1,
        )
        if total_obs > 0
        else 100.0
    )

    # Health status evaluation
    if total_obs == 0:
        health_status = "critical"
    elif gap_list and any(g["gap_count"] > len(expected_trading_days) * 0.5 for g in gap_list):
        health_status = "degraded"
    elif avg_score < 70.0:
        health_status = "degraded"
    else:
        health_status = "healthy"

    return {
        "status": health_status,
        "window_days": days,
        "summary": {
            "total_observations": total_obs,
            "active_markets_count": len(market_dates),
            "average_quality_score": avg_score,
            "total_outliers_flagged": len(dq_events),
        },
        "rows_per_market_per_day": rows_per_market_per_day,
        "gap_list": gap_list,
        "outliers": {
            "total_events": len(dq_events),
            "by_issue_type": dict(issue_counts),
            "recent_events": [
                {
                    "issue_type": ev.issue_type,
                    "penalty": ev.penalty,
                    "details": ev.details,
                    "created_at": ev.created_at.isoformat() if ev.created_at else None,
                }
                for ev in dq_events[:10]
            ],
        },
        "coverage_by_source": coverage_by_source,
    }
