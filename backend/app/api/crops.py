"""Crop listing endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.schemas.crop import CropListResponse, CropResponse

router = APIRouter(prefix="/api/crops", tags=["crops"])


@router.get("/", response_model=CropListResponse)
def list_crops(db: Session = Depends(get_db)):
    """List all configured crops."""
    crops = db.query(Crop).order_by(Crop.name).all()
    return CropListResponse(
        crops=[
            CropResponse(
                id=str(c.id),
                name=c.name,
                tamil_name=c.tamil_name,
                category=c.category,
                unit=c.unit,
            )
            for c in crops
        ]
    )
