"""Statewide Prices API (v1) with quality score filtering and telemetry."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market_price import MarketPrice
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


@router.get("/{price_id}/lineage")
def get_price_lineage(price_id: UUID, db: Session = Depends(get_db)):
    """Retrieve end-to-end data provenance for a normalized market price observation."""
    price = db.query(MarketPrice).filter(MarketPrice.id == price_id).first()
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price record not found")

    return {
        "price_id": str(price.id),
        "price_date": price.price_date.isoformat(),
        "crop_name": price.crop.name if price.crop else None,
        "variety_name": price.variety.name if price.variety else None,
        "market_name": price.market.name if price.market else None,
        "district": price.district,
        "modal_price": float(price.modal_price),
        "min_price": float(price.min_price),
        "max_price": float(price.max_price),
        "raw_price": float(price.raw_price) if price.raw_price is not None else None,
        "raw_unit": price.raw_unit,
        "source": price.source,
        "quality_score": price.quality_score,
        "quality_breakdown": price.quality_breakdown,
        "ingestion_run": {
            "id": str(price.ingestion_run.id),
            "source_code": price.ingestion_run.source_code,
            "status": price.ingestion_run.status,
            "district": price.ingestion_run.district,
            "started_at": price.ingestion_run.started_at.isoformat() if price.ingestion_run.started_at else None,
            "completed_at": price.ingestion_run.completed_at.isoformat() if price.ingestion_run.completed_at else None,
        } if price.ingestion_run else None,
        "raw_ingest": {
            "id": str(price.raw_ingest.id),
            "checksum": price.raw_ingest.checksum,
            "source_record_id": price.raw_ingest.source_record_id,
            "retrieved_at": price.raw_ingest.retrieved_at.isoformat() if price.raw_ingest.retrieved_at else None,
            "payload": price.raw_ingest.payload,
        } if price.raw_ingest else None,
    }

