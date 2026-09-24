"""Market API v1 endpoints — market registry and resolution."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.market import Market
from app.schemas.market import (
    MarketDetailResponse,
    MarketResolveRequest,
    MarketResolveResponse,
    MarketResponse,
)
from app.services.market_resolver import resolve_market

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=List[MarketResponse])
def list_markets(
    district_id: Optional[UUID] = Query(default=None),
    market_type: Optional[str] = Query(default=None),
    is_active: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """List markets with optional district and type filtering."""
    query = db.query(Market).filter(Market.is_active == is_active)
    if district_id:
        query = query.filter(Market.district_id == district_id)
    if market_type:
        query = query.filter(Market.market_type == market_type)
    return query.order_by(Market.name).all()


@router.get("/{market_id}", response_model=MarketDetailResponse)
def get_market(market_id: UUID, db: Session = Depends(get_db)):
    """Get single market by ID with its configured aliases."""
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return MarketDetailResponse.model_validate(market)


@router.post("/resolve", response_model=MarketResolveResponse)
def resolve_market_text(payload: MarketResolveRequest, db: Session = Depends(get_db)):
    """Resolve an incoming raw market name or code to a canonical Market."""
    market = resolve_market(
        payload.text,
        payload.district_id,
        db,
        source_code=payload.source_code,
        external_code=payload.external_code,
    )
    if not market:
        return MarketResolveResponse(matched=False, query=payload.text, market=None)
    return MarketResolveResponse(
        matched=True,
        query=payload.text,
        market=MarketResponse.model_validate(market),
    )
