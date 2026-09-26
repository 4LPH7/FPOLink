"""Buyer and buyer requirement request/response schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.harvest import HarvestGrade


class BuyerBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    buyer_type: str = Field(default="wholesaler", description="wholesaler, processor, exporter, retailer, trader")
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_phone: str = Field(..., min_length=10, max_length=15)
    contact_email: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=200)
    district: Optional[str] = None
    district_id: Optional[UUID] = None
    state_id: Optional[UUID] = None
    gstin: Optional[str] = Field(None, max_length=20)
    verified: bool = False


class BuyerCreate(BuyerBase):
    fpo_id: Optional[UUID] = None
    user_id: Optional[UUID] = None


class BuyerUpdate(BaseModel):
    company_name: Optional[str] = None
    buyer_type: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    district_id: Optional[UUID] = None
    gstin: Optional[str] = None
    verified: Optional[bool] = None


class BuyerResponse(BaseModel):
    id: str
    company_name: str
    buyer_type: str
    contact_name: Optional[str] = None
    contact_phone: str
    contact_email: Optional[str] = None
    location: str
    district: Optional[str] = None
    district_id: Optional[str] = None
    fpo_id: Optional[str] = None
    gstin: Optional[str] = None
    verified: bool = False
    open_requirements_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BuyerListResponse(BaseModel):
    buyers: List[BuyerResponse]
    total: int


class BuyerRequirementBase(BaseModel):
    crop_id: UUID = Field(..., description="Canonical crop UUID")
    variety_id: Optional[UUID] = None
    quantity_kg: float = Field(..., gt=0.0, description="Required quantity in kg")
    min_grade: HarvestGrade = Field(default=HarvestGrade.B, description="Minimum acceptable quality grade")
    required_date: date = Field(..., description="Target delivery date")
    delivery_window_days: int = Field(default=7, ge=1, le=60)
    max_price_per_kg: Optional[Decimal] = Field(None, gt=0.0)
    delivery_location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class BuyerRequirementCreate(BuyerRequirementBase):
    buyer_id: UUID = Field(..., description="Buyer UUID")
    fpo_id: Optional[UUID] = None
    district_id: Optional[UUID] = None


class BuyerRequirementUpdate(BaseModel):
    quantity_kg: Optional[float] = Field(None, gt=0.0)
    fulfilled_quantity_kg: Optional[float] = Field(None, ge=0.0)
    min_grade: Optional[HarvestGrade] = None
    required_date: Optional[date] = None
    delivery_window_days: Optional[int] = None
    max_price_per_kg: Optional[Decimal] = None
    delivery_location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class BuyerRequirementResponse(BaseModel):
    id: str
    buyer_id: str
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    fpo_id: Optional[str] = None
    crop_id: str
    crop_name: Optional[str] = None
    crop_tamil_name: Optional[str] = None
    variety_id: Optional[str] = None
    variety_name: Optional[str] = None
    quantity_kg: float
    fulfilled_quantity_kg: float = 0.0
    min_grade: str
    required_date: date
    delivery_window_days: int = 7
    max_price_per_kg: Optional[Decimal] = None
    delivery_location: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BuyerRequirementListResponse(BaseModel):
    requirements: List[BuyerRequirementResponse]
    total: int
    total_quantity_kg: float
