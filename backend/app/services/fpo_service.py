"""FPO service — business logic for FPO management."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest
from app.models.order import Order
from app.schemas.fpo import FPOCreate, FPOUpdate


def create_fpo(db: Session, data: FPOCreate) -> FPO:
    fpo = FPO(**data.model_dump())
    db.add(fpo)
    db.commit()
    db.refresh(fpo)
    return fpo


def get_fpo(db: Session, fpo_id: UUID) -> Optional[FPO]:
    return db.query(FPO).filter(FPO.id == fpo_id).first()


def list_fpos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FPO).offset(skip).limit(limit).all()


def update_fpo(db: Session, fpo_id: UUID, data: FPOUpdate) -> Optional[FPO]:
    fpo = get_fpo(db, fpo_id)
    if not fpo:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(fpo, key, value)
    db.commit()
    db.refresh(fpo)
    return fpo


def get_dashboard_stats(db: Session, fpo_id: UUID) -> dict:
    """Get dashboard statistics for an FPO."""
    # Member count
    member_count = db.query(func.count(Farmer.id)).filter(Farmer.fpo_id == fpo_id).scalar() or 0

    # Total farm area
    total_area = (
        db.query(func.sum(Farmer.farm_area_acres)).filter(Farmer.fpo_id == fpo_id).scalar() or 0.0
    )

    # Crop distribution
    crop_dist_rows = (
        db.query(Crop.name, func.count(Farm.id))
        .join(Farm, Farm.crop_id == Crop.id)
        .join(Farmer, Farm.farmer_id == Farmer.id)
        .filter(Farmer.fpo_id == fpo_id)
        .group_by(Crop.name)
        .all()
    )
    crop_distribution = {name: count for name, count in crop_dist_rows}

    # Active harvests total kg
    active_harvests = (
        db.query(func.sum(Harvest.quantity_kg))
        .join(Farmer, Harvest.farmer_id == Farmer.id)
        .filter(Farmer.fpo_id == fpo_id, Harvest.status == "submitted")
        .scalar()
    ) or 0.0

    # Revenue from completed orders
    revenue = (
        db.query(func.sum(Order.total_amount))
        .filter(Order.fpo_id == fpo_id, Order.status == "completed")
        .scalar()
    ) or 0.0

    return {
        "member_count": member_count,
        "total_farm_area_acres": float(total_area),
        "crop_distribution": crop_distribution,
        "active_harvests_kg": float(active_harvests),
        "revenue_total": float(revenue),
    }
