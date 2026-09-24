"""Crop API v1 endpoints — agricultural ontology and resolution."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.models.variety import Variety
from app.schemas.crop import (
    CropDetailResponse,
    CropListResponse,
    CropResolveRequest,
    CropResolveResponse,
    CropResponse,
    VarietyResponse,
)
from app.services.crop_resolver import resolve_crop, resolve_variety

router = APIRouter(prefix="/crops", tags=["crops"])


@router.get("", response_model=CropListResponse)
def list_crops(
    category: Optional[str] = Query(default=None, description="Filter by crop category"),
    is_active: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """List crops in the agricultural ontology."""
    query = db.query(Crop).filter(Crop.is_active == is_active)
    if category:
        query = query.filter(Crop.category.ilike(category))
    crops = query.order_by(Crop.name).all()
    return CropListResponse(
        crops=[
            CropResponse(
                id=str(c.id),
                name=c.name,
                canonical_name=c.canonical_name,
                tamil_name=c.tamil_name,
                scientific_name=c.scientific_name,
                category=c.category,
                subcategory=c.subcategory,
                unit=c.unit,
                default_unit=c.default_unit,
                market_unit=c.market_unit,
                season_type=c.season_type,
                is_horticulture=c.is_horticulture,
                is_commercial=c.is_commercial,
                is_active=c.is_active,
            )
            for c in crops
        ]
    )


@router.get("/{crop_id}", response_model=CropDetailResponse)
def get_crop(crop_id: UUID, db: Session = Depends(get_db)):
    """Get full details of a crop including varieties and aliases."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return CropDetailResponse(
        id=str(crop.id),
        name=crop.name,
        canonical_name=crop.canonical_name,
        tamil_name=crop.tamil_name,
        scientific_name=crop.scientific_name,
        category=crop.category,
        subcategory=crop.subcategory,
        unit=crop.unit,
        default_unit=crop.default_unit,
        market_unit=crop.market_unit,
        season_type=crop.season_type,
        is_horticulture=crop.is_horticulture,
        is_commercial=crop.is_commercial,
        is_active=crop.is_active,
        varieties=[VarietyResponse.model_validate(v) for v in crop.varieties],
        aliases=[
            {
                "id": a.id,
                "crop_id": a.crop_id,
                "alias": a.alias,
                "source": a.source,
                "confidence": a.confidence,
            }
            for a in crop.aliases
        ],
    )


@router.get("/{crop_id}/varieties", response_model=List[VarietyResponse])
def list_crop_varieties(crop_id: UUID, db: Session = Depends(get_db)):
    """List varieties for a specific crop."""
    varieties = db.query(Variety).filter(Variety.crop_id == crop_id).order_by(Variety.name).all()
    return [VarietyResponse.model_validate(v) for v in varieties]


@router.post("/resolve", response_model=CropResolveResponse)
def resolve_crop_text(payload: CropResolveRequest, db: Session = Depends(get_db)):
    """Resolve an incoming raw string (e.g. from mandi feed or chat) to a canonical Crop."""
    crop = resolve_crop(payload.text, db)
    if not crop:
        return CropResolveResponse(matched=False, query=payload.text, crop=None, variety=None)

    variety = resolve_variety(crop.id, payload.text, db)
    return CropResolveResponse(
        matched=True,
        query=payload.text,
        crop=CropResponse(
            id=str(crop.id),
            name=crop.name,
            canonical_name=crop.canonical_name,
            tamil_name=crop.tamil_name,
            scientific_name=crop.scientific_name,
            category=crop.category,
            subcategory=crop.subcategory,
            unit=crop.unit,
            default_unit=crop.default_unit,
            market_unit=crop.market_unit,
            season_type=crop.season_type,
            is_horticulture=crop.is_horticulture,
            is_commercial=crop.is_commercial,
            is_active=crop.is_active,
        ),
        variety=VarietyResponse.model_validate(variety) if variety else None,
    )
