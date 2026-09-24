"""Crop schemas — agricultural ontology and resolution."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VarietyResponse(BaseModel):
    id: UUID
    crop_id: UUID
    name: str
    canonical_name: Optional[str] = None
    tamil_name: Optional[str] = None
    grade: Optional[str] = None
    maturity_days: Optional[int] = None
    market_unit: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CropAliasResponse(BaseModel):
    id: UUID
    crop_id: UUID
    alias: str
    source: Optional[str] = None
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class CropResponse(BaseModel):
    id: str
    name: str
    canonical_name: Optional[str] = None
    tamil_name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    unit: str
    default_unit: Optional[str] = "kg"
    market_unit: Optional[str] = "quintal"
    season_type: Optional[str] = None
    is_horticulture: Optional[bool] = False
    is_commercial: Optional[bool] = False
    is_active: Optional[bool] = True

    model_config = ConfigDict(from_attributes=True)


class CropDetailResponse(CropResponse):
    varieties: List[VarietyResponse] = []
    aliases: List[CropAliasResponse] = []


class CropListResponse(BaseModel):
    crops: List[CropResponse]


class CropResolveRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw name or alias to resolve")
    source_code: Optional[str] = None
    external_code: Optional[str] = None


class CropResolveResponse(BaseModel):
    matched: bool
    query: str
    crop: Optional[CropResponse] = None
    variety: Optional[VarietyResponse] = None
