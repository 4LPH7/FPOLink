"""Farm and discrete plot management service."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.schemas.farm import FarmCreate, FarmUpdate
from app.services.yield_estimator import estimate_crop_yield


def create_farm(db: Session, data: FarmCreate) -> Farm:
    """Register a discrete farm plot under a farmer, computing yield defaults if missing."""
    farmer = db.query(Farmer).filter(Farmer.id == data.farmer_id).first()
    if not farmer:
        raise ValueError(f"Farmer with ID {data.farmer_id} does not exist")

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise ValueError(f"Crop with ID {data.crop_id} does not exist")

    farm_dict = data.model_dump()

    # Default village and administrative geography from farmer if missing
    if not farm_dict.get("village"):
        farm_dict["village"] = farmer.village
    if not farm_dict.get("district_id"):
        farm_dict["district_id"] = farmer.district_id
    if not farm_dict.get("taluk_id"):
        farm_dict["taluk_id"] = farmer.taluk_id
    if not farm_dict.get("village_id"):
        farm_dict["village_id"] = farmer.village_id

    # Compute rule-based expected yield if not provided
    yield_est = estimate_crop_yield(
        crop_name=crop.name,
        area_acres=data.area_acres,
        soil_type=data.soil_type,
        irrigation_type=data.irrigation_type,
        sowing_date=data.sowing_date,
    )
    farm_dict["expected_yield_kg"] = yield_est["estimated_yield_kg"]

    if not farm_dict.get("expected_harvest_date") and yield_est.get("estimated_harvest_window_start"):
        farm_dict["expected_harvest_date"] = yield_est["estimated_harvest_window_start"]

    farm = Farm(**farm_dict)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


def get_farm(db: Session, farm_id: UUID) -> Optional[Farm]:
    """Retrieve a single farm plot with related farmer and crop details."""
    return (
        db.query(Farm)
        .options(
            joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(Farm.crop),
            joinedload(Farm.district),
            joinedload(Farm.taluk),
        )
        .filter(Farm.id == farm_id)
        .first()
    )


def list_farms(
    db: Session,
    farmer_id: Optional[UUID] = None,
    fpo_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    district: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Farm], int, float]:
    """List farm plots with filtering, pagination, and total acreage calculation."""
    query = (
        db.query(Farm)
        .join(Farmer, Farm.farmer_id == Farmer.id)
        .join(Crop, Farm.crop_id == Crop.id)
        .options(
            joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(Farm.crop),
            joinedload(Farm.district),
            joinedload(Farm.taluk),
        )
    )

    if farmer_id:
        query = query.filter(Farm.farmer_id == farmer_id)
    if fpo_id:
        query = query.filter(Farmer.fpo_id == fpo_id)
    if crop_id:
        query = query.filter(Farm.crop_id == crop_id)
    if district:
        query = query.filter(Farmer.district.ilike(f"%{district}%"))
    if status:
        query = query.filter(Farm.status == status)

    total_count = query.count()
    total_acres = (
        db.query(func.coalesce(func.sum(Farm.area_acres), 0.0))
        .join(Farmer, Farm.farmer_id == Farmer.id)
        .filter(
            (Farm.farmer_id == farmer_id) if farmer_id else True,
            (Farmer.fpo_id == fpo_id) if fpo_id else True,
            (Farm.crop_id == crop_id) if crop_id else True,
            (Farmer.district.ilike(f"%{district}%")) if district else True,
            (Farm.status == status) if status else True,
        )
        .scalar()
        or 0.0
    )

    farms = query.order_by(Farm.created_at.desc()).offset(skip).limit(limit).all()
    return farms, total_count, float(total_acres)


def update_farm(db: Session, farm_id: UUID, data: FarmUpdate) -> Optional[Farm]:
    """Update details of a farm plot."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return None

    update_dict = data.model_dump(exclude_unset=True)

    # Recalculate yield estimate if area or crop or soil or irrigation changed
    needs_yield_recalc = any(
        k in update_dict for k in ("area_acres", "crop_id", "soil_type", "irrigation_type", "sowing_date")
    ) and "expected_yield_kg" not in update_dict

    for key, value in update_dict.items():
        setattr(farm, key, value)

    if needs_yield_recalc and farm.crop:
        yield_est = estimate_crop_yield(
            crop_name=farm.crop.name,
            area_acres=farm.area_acres,
            soil_type=farm.soil_type,
            irrigation_type=farm.irrigation_type,
            sowing_date=farm.sowing_date,
        )
        farm.expected_yield_kg = yield_est["estimated_yield_kg"]

    db.commit()
    db.refresh(farm)
    return farm


def delete_farm(db: Session, farm_id: UUID) -> bool:
    """Soft delete or delete a farm plot."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        return False
    db.delete(farm)
    db.commit()
    return True


def get_farmer_plots(db: Session, farmer_id: UUID) -> List[Farm]:
    """Retrieve all active plots for a given farmer."""
    return (
        db.query(Farm)
        .options(joinedload(Farm.crop))
        .filter(Farm.farmer_id == farmer_id)
        .order_by(Farm.created_at.asc())
        .all()
    )
