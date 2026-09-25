"""Agricultural Intelligence API v1: Forecasting, Arbitrage & Spread Analysis."""

from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.forecasting import ForecastingService
from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.schemas.intelligence import (
    ArbitrageResponse,
    ForecastResponse,
    SpreadsResponse,
    TrainModelRequest,
    TrainModelResponse,
)
from app.services.arbitrage import find_market_arbitrage

router = APIRouter(prefix="/intelligence", tags=["intelligence-v1"])


@router.get("/forecast", response_model=ForecastResponse)
def get_crop_forecast(
    crop_id: UUID = Query(..., description="Canonical Crop UUID"),
    market_id: UUID = Query(..., description="Canonical Market UUID"),
    days: int = Query(default=7, ge=1, le=30, description="Forecast horizon in days"),
    db: Session = Depends(get_db),
):
    """Generate forward price forecasts with p10/p50/p90 intervals and actionable signals."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    # Fetch latest known price
    latest_price = (
        db.query(MarketPrice)
        .filter(MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id)
        .order_by(MarketPrice.price_date.desc())
        .first()
    )
    current_modal = float(latest_price.modal_price) if latest_price else None

    service = ForecastingService(db)
    points = service.generate_forecast(crop_id=crop_id, market_id=market_id, horizon_days=days)

    return ForecastResponse(
        crop_id=str(crop.id),
        crop_name=crop.name,
        crop_tamil_name=crop.tamil_name,
        market_id=str(market.id),
        market_name=market.name,
        district=market.district,
        current_modal_price=current_modal,
        horizon_days=days,
        forecast=points,
    )


@router.get("/arbitrage", response_model=ArbitrageResponse)
def get_arbitrage_opportunities(
    crop_id: UUID = Query(..., description="Canonical Crop UUID"),
    origin_market_id: UUID = Query(..., description="Origin Market UUID"),
    max_distance_km: float = Query(
        default=300.0, ge=10.0, le=1000.0, description="Search radius in km"
    ),
    base_cost: float = Query(default=50.0, ge=0.0, description="Base loading cost per quintal (₹)"),
    rate_per_km: float = Query(default=1.20, ge=0.1, description="Freight cost ₹/km/quintal"),
    db: Session = Depends(get_db),
):
    """Evaluate inter-district market arbitrage deducting estimated freight costs."""
    result = find_market_arbitrage(
        db,
        crop_id=crop_id,
        origin_market_id=origin_market_id,
        max_distance_km=max_distance_km,
        base_transport_cost=base_cost,
        rate_per_km_quintal=rate_per_km,
    )
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.get("/spreads", response_model=SpreadsResponse)
def get_price_spreads(
    crop_id: UUID = Query(..., description="Canonical Crop UUID"),
    district: Optional[str] = Query(default=None, description="Optional district filter or 'all'"),
    days_window: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Analyze statewide price dispersion and identify highest/lowest reporting markets."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    cutoff_date = date.today() - timedelta(days=days_window)

    # Subquery for most recent price per market
    subq = (
        db.query(
            MarketPrice.market_id,
            func.max(MarketPrice.price_date).label("max_date"),
        )
        .filter(MarketPrice.crop_id == crop_id, MarketPrice.price_date >= cutoff_date)
        .group_by(MarketPrice.market_id)
        .subquery()
    )

    query = (
        db.query(MarketPrice, Market)
        .join(Market, MarketPrice.market_id == Market.id)
        .join(
            subq,
            (MarketPrice.market_id == subq.c.market_id)
            & (MarketPrice.price_date == subq.c.max_date),
        )
        .filter(MarketPrice.crop_id == crop_id)
    )

    if district and district.lower() != "all":
        query = query.filter(func.lower(MarketPrice.district) == district.strip().lower())

    results = query.all()

    if not results:
        return SpreadsResponse(
            crop_id=str(crop.id),
            crop_name=crop.name,
            crop_tamil_name=crop.tamil_name,
            district_filter=district,
            min_price=0.0,
            max_price=0.0,
            median_price=0.0,
            price_spread=0.0,
            reporting_markets_count=0,
            markets=[],
        )

    markets_list = []
    prices_list = []
    for mp, m in results:
        modal = float(mp.modal_price)
        prices_list.append(modal)
        markets_list.append(
            {
                "market_id": str(m.id),
                "market_name": m.name,
                "district": m.district,
                "modal_price": modal,
                "min_price": float(mp.min_price) if mp.min_price is not None else modal,
                "max_price": float(mp.max_price) if mp.max_price is not None else modal,
                "price_date": mp.price_date.isoformat(),
                "quality_score": float(mp.quality_score) if mp.quality_score is not None else None,
            }
        )

    prices_list.sort()
    min_p = prices_list[0]
    max_p = prices_list[-1]
    med_p = round(prices_list[len(prices_list) // 2], 2)
    spread = round(max_p - min_p, 2)

    markets_list.sort(key=lambda x: x["modal_price"], reverse=True)

    return SpreadsResponse(
        crop_id=str(crop.id),
        crop_name=crop.name,
        crop_tamil_name=crop.tamil_name,
        district_filter=district,
        min_price=min_p,
        max_price=max_p,
        median_price=med_p,
        price_spread=spread,
        reporting_markets_count=len(markets_list),
        markets=markets_list,
    )


@router.post("/train", response_model=TrainModelResponse)
def train_crop_model(
    payload: TrainModelRequest,
    db: Session = Depends(get_db),
):
    """Trigger on-demand training of LightGBM quantile regression models for a crop-market series."""
    try:
        crop_uuid = UUID(payload.crop_id)
        market_uuid = UUID(payload.market_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid crop_id or market_id UUID format")

    service = ForecastingService(db)
    mv = service.train_or_update_model(crop_uuid, market_uuid)
    if not mv:
        return TrainModelResponse(
            status="baseline_fallback",
            message="Series has fewer than 30 observations; rolling median baseline is currently active.",
        )

    return TrainModelResponse(
        status="success",
        model_name=mv.model_name,
        model_type=mv.model_type,
        metrics=mv.metrics,
        message=f"Model trained successfully on {mv.metrics.get('train_samples', 0)} samples.",
    )
