"""Statewide Prices API (v1) with quality score filtering and telemetry."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import QualitySummaryResponse
from app.services.prices import (
    get_latest_prices,
    get_price_history,
    get_quality_summary,
)

router = APIRouter(prefix="/prices", tags=["prices-v1"])


@router.get("/latest")
def latest_prices(
    district: Optional[str] = None,
    crop_id: Optional[str] = None,
    min_quality: Optional[float] = Query(default=None, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
):
    """Get the latest verified mandi prices across districts with optional quality score filter."""
    prices = get_latest_prices(
        db,
        district=district,
        crop_id=crop_id,
        min_quality=min_quality,
    )
    return {"prices": prices}


@router.get("/history")
def price_history(
    crop_id: str = Query(..., description="Crop UUID or identifier"),
    market_id: str = Query(..., description="Market UUID or identifier"),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get historical daily prices with quality scores for a crop in a market."""
    data = get_price_history(db, crop_id=crop_id, market_id=market_id, days=days)
    return {"history": data, "period_days": days}


@router.get("/quality-summary", response_model=QualitySummaryResponse)
def quality_summary(
    district: Optional[str] = Query(default=None, description="Filter by district name or 'all'"),
    days: int = Query(default=7, ge=1, le=90, description="Recent analysis window in days"),
    db: Session = Depends(get_db),
):
    """Get statewide or district-level data quality summary metrics."""
    return get_quality_summary(db, district=district, days=days)
