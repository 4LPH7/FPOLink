"""Geography request/response schemas for State, District, Taluk, Block, Village."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VillageResponse(BaseModel):
    id: UUID
    taluk_id: UUID
    block_id: Optional[UUID] = None
    name: str

    model_config = ConfigDict(from_attributes=True)


class BlockResponse(BaseModel):
    id: UUID
    taluk_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TalukResponse(BaseModel):
    id: UUID
    district_id: UUID
    name: str
    villages_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DistrictResponse(BaseModel):
    id: UUID
    state_id: UUID
    name: str
    code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    taluks_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class StateResponse(BaseModel):
    id: UUID
    name: str
    code: str
    districts_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class StateCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)


class DistrictCreate(BaseModel):
    state_id: UUID
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class TalukCreate(BaseModel):
    district_id: UUID
    name: str = Field(..., min_length=2, max_length=100)


class VillageCreate(BaseModel):
    taluk_id: UUID
    block_id: Optional[UUID] = None
    name: str = Field(..., min_length=2, max_length=100)
