"""Price-related request/response schemas."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MarketPriceResponse(BaseModel):
    id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    market_name: str
    district: str
    min_price: Decimal
    max_price: Decimal
    modal_price: Decimal
    price_date: date
    source: str
    arrival_quantity: Optional[float] = None
    quality_score: Optional[float] = None
    quality_breakdown: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class QualitySummaryResponse(BaseModel):
    total_records: int
    average_quality_score: float
    verified_count: int
    good_count: int
    limited_count: int
    unreliable_count: int
    by_source: dict


class PriceTrend(BaseModel):
    crop_name: str
    market_name: str
    current_price: Decimal
    previous_price: Decimal
    change_amount: Decimal
    change_percent: float
    direction: str  # up / down / stable


class PriceHistoryPoint(BaseModel):
    date: date
    min_price: Decimal
    max_price: Decimal
    modal_price: Decimal
    arrival_quantity: Optional[float] = None


class PriceHistoryResponse(BaseModel):
    crop_name: str
    market_name: str
    period_days: int
    data: List[PriceHistoryPoint]


class ManualPriceEntry(BaseModel):
    crop_id: str
    market_id: str
    min_price: Decimal = Field(..., gt=0)
    max_price: Decimal = Field(..., gt=0)
    modal_price: Decimal = Field(..., gt=0)
    price_date: date
