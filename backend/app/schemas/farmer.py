"""Farmer request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FarmerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    village: str = Field(..., min_length=1, max_length=100)
    taluk: str = Field(..., min_length=1, max_length=100)
    district: str = Field(default="Erode")
    farm_area_acres: float = Field(..., gt=0)
    language_preference: str = Field(default="ta")
    consent_given: bool = Field(default=False)


class FarmerUpdate(BaseModel):
    village: Optional[str] = None
    taluk: Optional[str] = None
    farm_area_acres: Optional[float] = None


class FarmerResponse(BaseModel):
    id: str
    user_id: str
    fpo_id: str
    name: str
    phone: str
    village: str
    taluk: str
    district: str
    farm_area_acres: float
    language_preference: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FarmerListResponse(BaseModel):
    farmers: List[FarmerResponse]
    total: int
    page: int
    page_size: int
