"""Ingestion Center Telemetry and Control API (v1)."""

from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.data_quality import DataSource, IngestionRun
from app.models.geography import District
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/ingestion", tags=["ingestion-v1"])


class TriggerIngestionRequest(BaseModel):
    crops: Optional[List[str]] = None
    districts: Optional[List[str]] = None
    source: Optional[str] = None


@router.get("/runs")
def list_ingestion_runs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source: Optional[str] = None,
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    """Get paginated history of ingestion runs with telemetry metrics."""
    query = db.query(IngestionRun)
    if source:
        query = query.filter(IngestionRun.source_code == source)
    if status_filter:
        query = query.filter(IngestionRun.status == status_filter)

    total = query.count()
    runs = (
        query.order_by(desc(IngestionRun.started_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for r in runs:
        duration = None
        if r.started_at and r.completed_at:
            duration = round((r.completed_at - r.started_at).total_seconds(), 2)

        items.append(
            {
                "id": str(r.id),
                "source_code": r.source_code,
                "status": r.status,
                "district": r.district,
                "records_fetched": r.records_fetched,
                "records_ingested": r.records_ingested,
                "error_count": len(r.errors) if r.errors else 0,
                "duration_seconds": duration,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/runs/{run_id}")
def get_ingestion_run(run_id: UUID, db: Session = Depends(get_db)):
    """Get detailed telemetry breakdown for a specific ingestion run."""
    run = db.query(IngestionRun).filter(IngestionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion run not found")

    # Fetch associated prices count and quality average
    stats = (
        db.query(
            func.count(MarketPrice.id).label("price_count"),
            func.avg(MarketPrice.quality_score).label("avg_quality"),
        )
        .filter(MarketPrice.ingestion_run_id == run.id)
        .first()
    )

    duration = None
    if run.started_at and run.completed_at:
        duration = round((run.completed_at - run.started_at).total_seconds(), 2)

    return {
        "id": str(run.id),
        "source_code": run.source_code,
        "status": run.status,
        "district": run.district,
        "records_fetched": run.records_fetched,
        "records_ingested": run.records_ingested,
        "errors": run.errors or [],
        "duration_seconds": duration,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "prices_produced": stats.price_count if stats else 0,
        "average_quality_score": round(float(stats.avg_quality), 2)
        if stats and stats.avg_quality
        else 100.0,
    }


@router.get("/freshness")
def get_statewide_freshness(db: Session = Depends(get_db)):
    """Get statewide coverage and freshness telemetry across all 38 districts."""
    total_districts = db.query(District).count()
    total_markets = db.query(Market).filter(Market.is_active.is_(True)).count()

    seven_days_ago = date.today() - timedelta(days=7)

    recent_stats = db.query(
        func.count(func.distinct(MarketPrice.district)).label("reporting_districts"),
        func.count(func.distinct(MarketPrice.market_id)).label("active_markets"),
        func.count(func.distinct(MarketPrice.crop_id)).label("crops_covered"),
        func.max(MarketPrice.price_date).label("latest_date"),
        func.count(MarketPrice.id).label("total_records"),
        func.avg(MarketPrice.quality_score).label("avg_score"),
    ).first()

    recent_7d = (
        db.query(
            func.count(func.distinct(MarketPrice.district)).label("districts_7d"),
            func.count(func.distinct(MarketPrice.market_id)).label("markets_7d"),
            func.count(func.distinct(MarketPrice.crop_id)).label("crops_7d"),
        )
        .filter(MarketPrice.price_date >= seven_days_ago)
        .first()
    )

    data_sources = (
        db.query(DataSource)
        .filter(DataSource.is_active.is_(True))
        .order_by(DataSource.priority)
        .all()
    )

    return {
        "total_districts": total_districts,
        "total_canonical_markets": total_markets,
        "all_time": {
            "reporting_districts": recent_stats.reporting_districts or 0,
            "active_markets": recent_stats.active_markets or 0,
            "crops_covered": recent_stats.crops_covered or 0,
            "latest_price_date": recent_stats.latest_date.isoformat()
            if recent_stats.latest_date
            else None,
            "total_observations": recent_stats.total_records or 0,
            "average_quality_score": round(float(recent_stats.avg_score), 1)
            if recent_stats.avg_score
            else 100.0,
        },
        "recent_7d": {
            "reporting_districts": recent_7d.districts_7d or 0,
            "active_markets": recent_7d.markets_7d or 0,
            "crops_covered": recent_7d.crops_7d or 0,
        },
        "data_sources": [
            {
                "code": ds.code,
                "name": ds.name,
                "priority": ds.priority,
                "is_active": ds.is_active,
            }
            for ds in data_sources
        ],
    }


@router.post("/trigger")
def trigger_ingestion(payload: TriggerIngestionRequest, db: Session = Depends(get_db)):
    """Trigger a statewide or targeted price ingestion run."""
    service = IngestionService(db)
    summary = service.run_ingestion(
        crops=payload.crops,
        districts=payload.districts,
        source=payload.source,
    )
    return {
        "status": "completed",
        "summary": summary,
    }
