"""Farmer request/response schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FarmerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    village: str = Field(..., min_length=1, max_length=100)
    taluk: str = Field(..., min_length=1, max_length=100)
    district: str = Field(default="Erode")
    farm_area_acres: float = Field(..., gt=0)
    language_preference: str = Field(default="ta")
    consent_given: bool = Field(default=False)
    lang: Optional[str] = Field(default="ta", max_length=10)
    alerts_opt_in: Optional[bool] = Field(default=False)


class FarmerUpdate(BaseModel):
    phone: Optional[str] = None
    village: Optional[str] = None
    taluk: Optional[str] = None
    farm_area_acres: Optional[float] = None
    lang: Optional[str] = None
    alerts_opt_in: Optional[bool] = None


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
    lang: str = "ta"
    alerts_opt_in: bool = False
    alerts_opt_in_at: Optional[datetime] = None
    alerts_opt_out_at: Optional[datetime] = None
    notice_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WhatsAppInviteResponse(BaseModel):
    farmer_id: str
    phone: str
    bot_phone: str
    invite_url: str


class FarmerListResponse(BaseModel):
    farmers: List[FarmerResponse]
    total: int
    page: int
    page_size: int
