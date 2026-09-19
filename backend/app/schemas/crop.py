"""Crop schemas."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CropResponse(BaseModel):
    id: str
    name: str
    tamil_name: Optional[str] = None
    category: Optional[str] = None
    unit: str

    model_config = ConfigDict(from_attributes=True)


class CropListResponse(BaseModel):
    crops: List[CropResponse]
