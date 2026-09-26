"""Semi-automatic matching request/response schemas — supply candidate ranking, staff confirmation, and balance summary."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MatchBreakdown(BaseModel):
    crop_match: bool = True
    distance_km: Optional[float] = None
    proximity_score: float = 0.0
    quantity_fit_ratio: float = 0.0
    timing_days_delta: Optional[int] = None
    timing_score: float = 0.0
    grade_score: float = 0.0
    composite_score: float = 0.0


class MatchCandidate(BaseModel):
    candidate_type: str = Field(..., description="'farm_plot' or 'harvest'")
    source_id: str = Field(..., description="UUID of Farm or Harvest")
    farmer_id: str
    farmer_name: str
    farmer_phone: str
    farmer_alerts_opt_in: bool = False
    village: Optional[str] = None
    district: Optional[str] = None
    crop_id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    available_quantity_kg: float
    grade: Optional[str] = None
    available_date: Optional[date] = None
    distance_km: Optional[float] = None
    match_score: float
    match_breakdown: MatchBreakdown


class MatchCandidateListResponse(BaseModel):
    requirement_id: str
    buyer_id: str
    buyer_name: str
    crop_name: str
    required_quantity_kg: float
    required_date: date
    delivery_location: Optional[str] = None
    candidates: List[MatchCandidate]
    total_candidates: int


class MatchCreate(BaseModel):
    buyer_requirement_id: UUID
    fpo_id: UUID
    farm_id: Optional[UUID] = None
    harvest_id: Optional[UUID] = None
    matched_quantity_kg: float = Field(..., gt=0.0)
    offered_price_per_kg: Optional[Decimal] = None
    match_score: float = Field(..., ge=0.0, le=100.0)
    match_breakdown: Optional[Dict[str, Any]] = None
    staff_notes: Optional[str] = None


class MatchConfirmRequest(BaseModel):
    staff_notes: Optional[str] = None
    offered_price_per_kg: Optional[Decimal] = None
    send_whatsapp_nudge: bool = False


class MatchResponse(BaseModel):
    id: str
    buyer_requirement_id: str
    buyer_name: Optional[str] = None
    farm_id: Optional[str] = None
    harvest_id: Optional[str] = None
    fpo_id: str
    farmer_id: Optional[str] = None
    farmer_name: Optional[str] = None
    farmer_phone: Optional[str] = None
    crop_name: Optional[str] = None
    matched_quantity_kg: float
    offered_price_per_kg: Optional[Decimal] = None
    match_score: float
    match_breakdown: Optional[Dict[str, Any]] = None
    status: str
    staff_notes: Optional[str] = None
    confirmed_by_name: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    notified_at: Optional[datetime] = None
    farmer_responded_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    matches: List[MatchResponse]
    total: int


class SupplyDemandCropSummary(BaseModel):
    crop_id: str
    crop_name: str
    crop_tamil_name: Optional[str] = None
    standing_acres: float
    estimated_standing_yield_kg: float
    verified_harvest_kg: float
    total_supply_kg: float
    total_demand_kg: float
    net_balance_kg: float
    active_plots_count: int
    open_requirements_count: int


class SupplyDemandSummaryResponse(BaseModel):
    fpo_id: Optional[str] = None
    district: Optional[str] = None
    commodities: List[SupplyDemandCropSummary]
    total_standing_acres: float
    total_supply_kg: float
    total_demand_kg: float
    active_plots_total: int
    open_requirements_total: int
