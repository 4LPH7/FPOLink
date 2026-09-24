"""Market request/response schemas."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MarketAliasResponse(BaseModel):
    id: UUID
    market_id: UUID
    alias: str
    source: Optional[str] = None
    confidence: float

    model_config = ConfigDict(from_attributes=True)


class MarketResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[str] = None
    district: str
    state: str = "Tamil Nadu"
    market_type: str = "mandi"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True
    district_id: Optional[UUID] = None
    taluk_id: Optional[UUID] = None
    state_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class MarketDetailResponse(MarketResponse):
    aliases: List[MarketAliasResponse] = []


class MarketResolveRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw market name or code to resolve")
    district_id: Optional[UUID] = None


class MarketResolveResponse(BaseModel):
    matched: bool
    query: str
    market: Optional[MarketResponse] = None
