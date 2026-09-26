"""Farm plot request/response schemas — discrete agricultural plots and yield estimates."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmBase(BaseModel):
    crop_id: UUID = Field(..., description="Canonical crop UUID")
    plot_name: Optional[str] = Field(None, max_length=100, description="Plot identifier/name")
    area_acres: float = Field(..., gt=0.0, description="Plot area in acres")
    village: Optional[str] = Field(None, max_length=100, description="Revenue village name")
    soil_type: Optional[str] = Field(None, max_length=50, description="e.g. Red Loam, Clay Loam, Black Cotton")
    irrigation_type: Optional[str] = Field(None, max_length=50, description="e.g. Drip, Canal, Borewell, Rainfed")
    sowing_date: Optional[date] = Field(None, description="Planting date")
    expected_harvest_date: Optional[date] = Field(None, description="Expected harvest completion date")
    status: str = Field(default="active", description="active, harvested, fallow, abandoned")
    district_id: Optional[UUID] = None
    taluk_id: Optional[UUID] = None
    village_id: Optional[UUID] = None


class FarmCreate(FarmBase):
    farmer_id: UUID = Field(..., description="Farmer UUID who owns this plot")


class FarmUpdate(BaseModel):
    crop_id: Optional[UUID] = None
    plot_name: Optional[str] = None
    area_acres: Optional[float] = Field(None, gt=0.0)
    village: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    expected_yield_kg: Optional[float] = None
    actual_yield_kg: Optional[float] = None
    status: Optional[str] = None
    district_id: Optional[UUID] = None
    taluk_id: Optional[UUID] = None
    village_id: Optional[UUID] = None


class FarmResponse(BaseModel):
    id: str
    farmer_id: str
    farmer_name: Optional[str] = None
    farmer_phone: Optional[str] = None
    crop_id: str
    crop_name: Optional[str] = None
    crop_tamil_name: Optional[str] = None
    plot_name: Optional[str] = None
    area_acres: float
    village: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    expected_yield_kg: Optional[float] = None
    actual_yield_kg: Optional[float] = None
    status: str
    district_id: Optional[str] = None
    district_name: Optional[str] = None
    taluk_id: Optional[str] = None
    taluk_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FarmListResponse(BaseModel):
    plots: List[FarmResponse]
    total: int
    total_area_acres: float


class FarmYieldEstimateResponse(BaseModel):
    farm_id: str
    crop_name: str
    area_acres: float
    base_yield_kg_per_acre: float
    soil_factor: float
    irrigation_factor: float
    estimated_yield_kg: float
    estimated_harvest_window_start: Optional[date] = None
    estimated_harvest_window_end: Optional[date] = None
    confidence_note: str


class FarmCSVRow(BaseModel):
    farmer_phone: str = Field(..., min_length=10, max_length=15)
    crop_name: str = Field(..., min_length=2)
    plot_name: Optional[str] = None
    area_acres: float = Field(..., gt=0.0)
    village: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
