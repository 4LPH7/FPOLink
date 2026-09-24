"""Commodity registry schemas."""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SourceMappingSummary(BaseModel):
    id: UUID
    source_code: str
    external_code: str
    external_name: str
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class CommoditySummary(BaseModel):
    id: UUID
    name: str
    canonical_name: Optional[str] = None
    tamil_name: Optional[str] = None
    scientific_name: Optional[str] = None
    category: Optional[str] = None
    unit: str
    is_active: bool
    variety_count: int
    alias_count: int
    source_mapping_count: int
    reporting_market_count: int = 0


class CommodityDetail(BaseModel):
    id: UUID
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
    is_active: bool
    varieties: List[dict] = []
    aliases: List[dict] = []
    source_mappings: List[SourceMappingSummary] = []
    active_markets: List[str] = []
