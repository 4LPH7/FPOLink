"""Pydantic schemas for Agricultural Intelligence API v1."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ForecastPoint(BaseModel):
    crop_id: str
    market_id: str
    target_date: str
    predicted_price: float
    lower_bound: float
    upper_bound: float
    confidence: float
    signal: str
    model_type: str


class ForecastResponse(BaseModel):
    crop_id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    market_id: str
    market_name: str
    district: str
    current_modal_price: Optional[float] = None
    horizon_days: int
    input_freshness_date: Optional[str] = None
    days_since_last_observation: Optional[int] = None
    is_stale: Optional[bool] = None
    stale_warning: Optional[str] = None
    disclaimer_ta: str = "இது மதிப்பீடு மட்டுமே, கொள்முதல் அல்லது விற்பனை ஆலோசனை அல்ல."
    disclaimer_en: str = "Estimate only, not financial or trading advice."
    forecast: List[ForecastPoint]
    disclaimer: Dict[str, str] = {
        "ta": "இது மதிப்பீடு மட்டுமே, ஆலோசனை அல்ல.",
        "en": "Estimate only, not advice.",
    }


class ArbitrageOpportunity(BaseModel):
    target_market_id: str
    target_market_name: str
    district: str
    target_price: float
    price_date: str
    distance_km: float
    gross_spread: float
    transport_cost: float
    net_spread: float
    recommendation: str
    variety_name: Optional[str] = None
    variety_match: Optional[str] = None
    costs_breakdown: Optional[Dict[str, float]] = None
    date_difference_days: Optional[int] = None
    uncertainty_rating: Optional[str] = "low"
    uncertainty_reasons: Optional[List[str]] = []


class ArbitrageResponse(BaseModel):
    crop_id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    origin_market_id: str
    origin_market_name: str
    origin_district: str
    origin_price: Optional[float] = None
    origin_price_date: Optional[str] = None
    origin_variety_name: Optional[str] = None
    vehicle_profile: Optional[str] = "lcv"
    total_destinations_analyzed: int
    assumptions: Optional[Dict[str, Any]] = None
    disclaimer: Optional[str] = None
    disclaimer_ta: Optional[str] = None
    disclaimer_en: Optional[str] = None
    opportunities: List[ArbitrageOpportunity]


class SpreadPoint(BaseModel):
    market_id: str
    market_name: str
    district: str
    modal_price: float
    min_price: float
    max_price: float
    price_date: str
    quality_score: Optional[float] = None


class SpreadsResponse(BaseModel):
    crop_id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    district_filter: Optional[str] = None
    min_price: float
    max_price: float
    median_price: float
    price_spread: float
    reporting_markets_count: int
    markets: List[SpreadPoint]


class TrainModelRequest(BaseModel):
    crop_id: str
    market_id: str


class TrainModelResponse(BaseModel):
    status: str
    model_name: Optional[str] = None
    model_type: Optional[str] = None
    metrics: Optional[Dict] = None
    message: str
