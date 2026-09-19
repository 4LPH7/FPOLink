"""Price endpoints — latest prices, history, trends, anomalies."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.prices import (
    get_latest_prices,
    get_price_history,
    get_price_trend,
    check_anomalies,
)

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("/latest")
def latest_prices(
    district: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get latest prices for all crops in a district."""
    return {"prices": get_latest_prices(db, district)}


@router.get("/history")
def price_history(
    crop_id: str = Query(...),
    market_id: str = Query(...),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get price history for a crop in a market."""
    data = get_price_history(db, crop_id, market_id, days)
    return {"history": data, "period_days": days}


@router.get("/trend")
def price_trend(
    crop_id: str = Query(...),
    market_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Get price trend (daily/weekly/monthly change)."""
    trend = get_price_trend(db, crop_id, market_id)
    if not trend:
        return {"trend": None, "message": "Insufficient data for trend"}
    return {"trend": trend}


@router.get("/anomalies")
def price_anomalies(
    crop_id: str = Query(...),
    market_id: str = Query(...),
    window: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    """Check for price anomalies using MAD z-score."""
    anomalies = check_anomalies(db, crop_id, market_id, window)
    return {"anomalies": anomalies, "count": len(anomalies)}
