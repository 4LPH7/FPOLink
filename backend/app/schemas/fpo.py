"""FPO request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FPOCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    registration_number: str = Field(..., min_length=1, max_length=50)
    district: str = Field(..., min_length=1, max_length=100)
    village: str = Field(..., min_length=1, max_length=100)
    state: str = Field(default="Tamil Nadu")
    contact_phone: str = Field(..., min_length=10, max_length=15)
    contact_email: Optional[str] = None
    address: Optional[str] = None


class FPOUpdate(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None


class FPOResponse(BaseModel):
    id: str
    name: str
    registration_number: str
    district: str
    village: str
    state: str
    contact_phone: str
    contact_email: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FPODashboardStats(BaseModel):
    member_count: int
    total_farm_area_acres: float
    crop_distribution: dict  # {crop_name: farmer_count}
    active_harvests_kg: float
    revenue_total: float
