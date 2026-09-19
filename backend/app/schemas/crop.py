"""Crop schemas."""

from pydantic import BaseModel
from typing import Optional, List


class CropResponse(BaseModel):
    id: str
    name: str
    tamil_name: Optional[str] = None
    category: Optional[str] = None
    unit: str

    class Config:
        from_attributes = True


class CropListResponse(BaseModel):
    crops: List[CropResponse]
