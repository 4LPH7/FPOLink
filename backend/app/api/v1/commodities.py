"""Commodity registry API endpoints — Canonical commodity intelligence."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.source_mapping import CropSourceMapping
from app.models.variety import Variety
from app.schemas.commodity import CommodityDetail, CommoditySummary, SourceMappingSummary

router = APIRouter(prefix="/commodities", tags=["commodities"])


@router.get("", response_model=List[CommoditySummary])
def list_commodities(
    category: Optional[str] = Query(
        default=None, description="Filter by category (spice, fruit, cereal, etc.)"
    ),
    is_active: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    """List canonical crops with counts of varieties, aliases, source mappings, and reporting markets."""
    query = db.query(Crop).filter(Crop.is_active == is_active)
    if category:
        query = query.filter(Crop.category.ilike(category))

    crops = query.order_by(Crop.name).all()

    # Pre-aggregate counts for high performance
    variety_counts = dict(
        db.query(Variety.crop_id, func.count(Variety.id)).group_by(Variety.crop_id).all()
    )

    alias_counts = dict(
        db.query(CropAlias.crop_id, func.count(CropAlias.id)).group_by(CropAlias.crop_id).all()
    )

    mapping_counts = dict(
        db.query(CropSourceMapping.crop_id, func.count(CropSourceMapping.id))
        .group_by(CropSourceMapping.crop_id)
        .all()
    )

    market_counts = dict(
        db.query(MarketPrice.crop_id, func.count(func.distinct(MarketPrice.market_id)))
        .group_by(MarketPrice.crop_id)
        .all()
    )

    summaries = []
    for c in crops:
        summaries.append(
            CommoditySummary(
                id=c.id,
                name=c.name,
                canonical_name=c.canonical_name,
                tamil_name=c.tamil_name,
                scientific_name=c.scientific_name,
                category=c.category,
                unit=c.unit,
                is_active=c.is_active,
                variety_count=variety_counts.get(c.id, 0),
                alias_count=alias_counts.get(c.id, 0),
                source_mapping_count=mapping_counts.get(c.id, 0),
                reporting_market_count=market_counts.get(c.id, 0),
            )
        )
    return summaries


@router.get("/{crop_id}", response_model=CommodityDetail)
def get_commodity_detail(crop_id: UUID, db: Session = Depends(get_db)):
    """Get rich commodity profile with varieties, aliases, source mappings, and active markets."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commodity not found")

    mappings = (
        db.query(CropSourceMapping)
        .filter(CropSourceMapping.crop_id == crop.id)
        .order_by(CropSourceMapping.source_code)
        .all()
    )

    active_market_names = [
        row[0]
        for row in (
            db.query(Market.name)
            .join(MarketPrice, Market.id == MarketPrice.market_id)
            .filter(MarketPrice.crop_id == crop.id)
            .distinct()
            .order_by(Market.name)
            .all()
        )
    ]

    return CommodityDetail(
        id=crop.id,
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
        varieties=[
            {"id": str(v.id), "name": v.name, "canonical_name": v.canonical_name, "grade": v.grade}
            for v in crop.varieties
        ],
        aliases=[
            {"id": str(a.id), "alias": a.alias, "source": a.source, "confidence": a.confidence}
            for a in crop.aliases
        ],
        source_mappings=[
            SourceMappingSummary(
                id=m.id,
                source_code=m.source_code,
                external_code=m.external_code,
                external_name=m.external_name,
                confidence=m.confidence,
            )
            for m in mappings
        ],
        active_markets=active_market_names,
    )
