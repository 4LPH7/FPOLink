from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.forecasting import ForecastingService
from app.models.crop import Crop
from app.models.market import Market

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/forecast")
def get_forecast(
    crop_id: Optional[str] = None,
    market_id: Optional[str] = None,
    crop: Optional[str] = None,
    market: Optional[str] = None,
    days: int = Query(default=7, ge=1, le=30),
    model_type: str = Query(default="auto"),
    db: Session = Depends(get_db),
):
    """Legacy backward-compatible forecast endpoint delegating to ForecastingService."""
    c_uuid = None
    if crop_id:
        try:
            c_uuid = UUID(crop_id)
        except ValueError:
            pass
    elif crop:
        c_obj = (
            db.query(Crop)
            .filter(
                (func.lower(Crop.name) == crop.lower().strip()) | (Crop.tamil_name == crop.strip())
            )
            .first()
        )
        if c_obj:
            c_uuid = c_obj.id

    m_uuid = None
    if market_id:
        try:
            m_uuid = UUID(market_id)
        except ValueError:
            pass
    elif market:
        m_obj = db.query(Market).filter(func.lower(Market.name) == market.lower().strip()).first()
        if m_obj:
            m_uuid = m_obj.id

    if not c_uuid:
        first_crop = db.query(Crop).first()
        if first_crop:
            c_uuid = first_crop.id
    if not m_uuid:
        first_market = db.query(Market).first()
        if first_market:
            m_uuid = first_market.id

    if not c_uuid or not m_uuid:
        return {"forecast": []}

    service = ForecastingService(db)
    points = service.generate_forecast(
        crop_id=c_uuid,
        market_id=m_uuid,
        horizon_days=days,
        model_type=model_type,
        persist=False,
    )
    return {"forecast": points}
