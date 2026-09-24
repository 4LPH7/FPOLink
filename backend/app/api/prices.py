"""Price endpoints — latest prices, history, trends, anomalies."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import ManualPriceEntry
from app.services.prices import (
    check_anomalies,
    get_latest_prices,
    get_price_history,
    get_price_trend,
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


@router.get("/markets")
def list_markets(db: Session = Depends(get_db)):
    """Get all registered markets."""
    from app.models.market import Market

    markets = db.query(Market).order_by(Market.name).all()
    return {
        "markets": [
            {
                "id": str(m.id),
                "name": m.name,
                "district": m.district,
                "state": m.state,
                "market_type": m.market_type,
            }
            for m in markets
        ]
    }


@router.post("/manual", status_code=201)
def record_manual_price(
    entry: "ManualPriceEntry",
    db: Session = Depends(get_db),
):
    """Record a verified manual mandi price quote."""
    from uuid import UUID
    from fastapi import HTTPException
    from app.models.market import Market
    from app.models.market_price import MarketPrice

    try:
        c_uuid = UUID(entry.crop_id)
        m_uuid = UUID(entry.market_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid crop_id or market_id UUID")

    market = db.query(Market).filter(Market.id == m_uuid).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    existing = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == c_uuid,
            MarketPrice.market_id == m_uuid,
            MarketPrice.price_date == entry.price_date,
        )
        .first()
    )

    if existing:
        existing.min_price = entry.min_price
        existing.max_price = entry.max_price
        existing.modal_price = entry.modal_price
        existing.source = "agmarknet"
        db.commit()
        db.refresh(existing)
        return {"message": "Price updated successfully", "id": str(existing.id)}

    mp = MarketPrice(
        crop_id=c_uuid,
        market_id=m_uuid,
        district=market.district,
        min_price=entry.min_price,
        max_price=entry.max_price,
        modal_price=entry.modal_price,
        price_date=entry.price_date,
        source="agmarknet",
    )
    db.add(mp)
    db.commit()
    db.refresh(mp)
    return {"message": "Price recorded successfully", "id": str(mp.id)}
