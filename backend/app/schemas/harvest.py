"""Pydantic schemas for harvest submission, updates, and listings."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.harvest import HarvestGrade, HarvestStatus


class HarvestCreate(BaseModel):
    farmer_id: Optional[UUID] = Field(
        None, description="Target farmer ID (optional if farmer user)"
    )
    crop_id: Optional[UUID] = Field(None, description="UUID of the harvested crop")
    crop_name: Optional[str] = Field(
        None, description="Crop name (e.g., turmeric, banana) if crop_id not given"
    )
    quantity_kg: float = Field(
        ..., gt=0, le=50000, description="Harvested quantity in kg (1 to 50,000)"
    )
    grade: HarvestGrade = Field(
        default=HarvestGrade.A, description="Commercial quality grade (A, B, C)"
    )
    harvest_date: Optional[date] = Field(default_factory=date.today, description="Date of harvest")
    notes: Optional[str] = Field(None, max_length=500, description="Optional harvest observations")
    source_message_id: Optional[str] = Field(
        None, max_length=128, description="WhatsApp message ID for idempotent dedup"
    )


class HarvestStatusUpdate(BaseModel):
    status: HarvestStatus = Field(
        ..., description="Target status (SUBMITTED, VERIFIED, AGGREGATED, SOLD)"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional status transition notes"
    )


class HarvestResponse(BaseModel):
    id: UUID
    farmer_id: UUID
    farmer_name: Optional[str] = None
    crop_id: UUID
    crop_name: str
    crop_tamil_name: Optional[str] = None
    quantity_kg: float
    grade: str
    harvest_date: date
    status: str
    source_message_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HarvestListResponse(BaseModel):
    harvests: List[HarvestResponse]
    total: int
    page: int
    page_size: int
