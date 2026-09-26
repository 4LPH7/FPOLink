"""Buyer and procurement requirement management service."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.schemas.buyer import (
    BuyerCreate,
    BuyerRequirementCreate,
    BuyerRequirementUpdate,
    BuyerUpdate,
)


def create_buyer(
    db: Session, data: BuyerCreate, created_by_user_id: Optional[UUID] = None
) -> Buyer:
    """Create a new commercial buyer profile (staff-mediated or self-service)."""
    buyer_dict = data.model_dump()
    if created_by_user_id:
        buyer_dict["created_by_user_id"] = created_by_user_id

    buyer = Buyer(**buyer_dict)
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def get_buyer(db: Session, buyer_id: UUID) -> Optional[Buyer]:
    """Retrieve a buyer with requirements."""
    return (
        db.query(Buyer)
        .options(
            joinedload(Buyer.requirements).joinedload(BuyerRequirement.crop),
            joinedload(Buyer.district_rel),
        )
        .filter(Buyer.id == buyer_id)
        .first()
    )


def list_buyers(
    db: Session,
    fpo_id: Optional[UUID] = None,
    district: Optional[str] = None,
    buyer_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[Buyer], int]:
    """List buyers with filtering and requirement counts."""
    query = db.query(Buyer).options(
        joinedload(Buyer.requirements),
        joinedload(Buyer.district_rel),
    )

    if fpo_id:
        query = query.filter((Buyer.fpo_id == fpo_id) | (Buyer.fpo_id.is_(None)))
    if district:
        query = query.filter(Buyer.district.ilike(f"%{district}%"))
    if buyer_type:
        query = query.filter(Buyer.buyer_type == buyer_type)

    total = query.count()
    buyers = query.order_by(Buyer.created_at.desc()).offset(skip).limit(limit).all()
    return buyers, total


def update_buyer(db: Session, buyer_id: UUID, data: BuyerUpdate) -> Optional[Buyer]:
    """Update commercial buyer profile."""
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
    if not buyer:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(buyer, key, value)

    db.commit()
    db.refresh(buyer)
    return buyer


def delete_buyer(db: Session, buyer_id: UUID) -> bool:
    """Delete a buyer record."""
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
    if not buyer:
        return False
    db.delete(buyer)
    db.commit()
    return True


def create_buyer_requirement(
    db: Session,
    data: BuyerRequirementCreate,
    created_by_user_id: Optional[UUID] = None,
) -> BuyerRequirement:
    """Post an institutional crop procurement requirement."""
    buyer = db.query(Buyer).filter(Buyer.id == data.buyer_id).first()
    if not buyer:
        raise ValueError(f"Buyer with ID {data.buyer_id} does not exist")

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise ValueError(f"Crop with ID {data.crop_id} does not exist")

    req_dict = data.model_dump()
    if created_by_user_id:
        req_dict["created_by_user_id"] = created_by_user_id

    # If delivery location missing, inherit from buyer location
    if not req_dict.get("delivery_location"):
        req_dict["delivery_location"] = buyer.location
    if not req_dict.get("fpo_id") and buyer.fpo_id:
        req_dict["fpo_id"] = buyer.fpo_id

    req = BuyerRequirement(**req_dict)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_buyer_requirement(db: Session, req_id: UUID) -> Optional[BuyerRequirement]:
    """Retrieve a single buyer requirement with full relational context."""
    return (
        db.query(BuyerRequirement)
        .options(
            joinedload(BuyerRequirement.buyer),
            joinedload(BuyerRequirement.crop),
            joinedload(BuyerRequirement.variety),
            joinedload(BuyerRequirement.district_rel),
        )
        .filter(BuyerRequirement.id == req_id)
        .first()
    )


def list_buyer_requirements(
    db: Session,
    buyer_id: Optional[UUID] = None,
    fpo_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[BuyerRequirement], int, float]:
    """List buyer requirements with pagination and total demand volume calculation."""
    query = (
        db.query(BuyerRequirement)
        .join(Buyer, BuyerRequirement.buyer_id == Buyer.id)
        .join(Crop, BuyerRequirement.crop_id == Crop.id)
        .options(
            joinedload(BuyerRequirement.buyer),
            joinedload(BuyerRequirement.crop),
            joinedload(BuyerRequirement.variety),
            joinedload(BuyerRequirement.district_rel),
        )
    )

    if buyer_id:
        query = query.filter(BuyerRequirement.buyer_id == buyer_id)
    if fpo_id:
        query = query.filter((BuyerRequirement.fpo_id == fpo_id) | (BuyerRequirement.fpo_id.is_(None)))
    if crop_id:
        query = query.filter(BuyerRequirement.crop_id == crop_id)
    if status:
        query = query.filter(BuyerRequirement.status == status)

    total_count = query.count()
    total_qty = (
        db.query(func.coalesce(func.sum(BuyerRequirement.quantity_kg), 0.0))
        .filter(
            (BuyerRequirement.buyer_id == buyer_id) if buyer_id else True,
            ((BuyerRequirement.fpo_id == fpo_id) | (BuyerRequirement.fpo_id.is_(None))) if fpo_id else True,
            (BuyerRequirement.crop_id == crop_id) if crop_id else True,
            (BuyerRequirement.status == status) if status else True,
        )
        .scalar()
        or 0.0
    )

    requirements = (
        query.order_by(BuyerRequirement.required_date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return requirements, total_count, float(total_qty)


def update_buyer_requirement(
    db: Session, req_id: UUID, data: BuyerRequirementUpdate
) -> Optional[BuyerRequirement]:
    """Update procurement requirement details."""
    req = db.query(BuyerRequirement).filter(BuyerRequirement.id == req_id).first()
    if not req:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(req, key, value)

    # Check if fulfilled
    if req.fulfilled_quantity_kg >= req.quantity_kg and req.status != "fulfilled":
        req.status = "fulfilled"

    db.commit()
    db.refresh(req)
    return req
