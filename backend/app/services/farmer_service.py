"""Farmer service — business logic for farmer management."""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.services.auth import hash_password
from app.schemas.farmer import FarmerCreate, FarmerUpdate


def create_farmer(
    db: Session,
    fpo_id: UUID,
    data: FarmerCreate,
) -> Tuple[User, Farmer]:
    """Create a new farmer with user account."""
    # Create user account
    user = User(
        name=data.name,
        phone=data.phone,
        role=UserRole.FARMER,
        hashed_password=hash_password(data.password),
        is_active=True,
        language_preference=data.language_preference,
        consent_given=data.consent_given,
        consent_date=datetime.now(timezone.utc) if data.consent_given else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create farmer profile
    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo_id,
        village=data.village,
        taluk=data.taluk,
        district=data.district,
        farm_area_acres=data.farm_area_acres,
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    return user, farmer


def get_farmer(db: Session, farmer_id: UUID) -> Optional[Farmer]:
    return db.query(Farmer).filter(Farmer.id == farmer_id).first()


def list_farmers(
    db: Session,
    fpo_id: UUID,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
) -> Tuple[List[Farmer], int]:
    """List farmers for an FPO with pagination and search."""
    query = (
        db.query(Farmer)
        .join(User, Farmer.user_id == User.id)
        .filter(Farmer.fpo_id == fpo_id)
    )

    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%")
            | Farmer.village.ilike(f"%{search}%")
            | User.phone.ilike(f"%{search}%")
        )

    total = query.count()
    farmers = query.offset((page - 1) * page_size).limit(page_size).all()

    return farmers, total


def update_farmer(
    db: Session,
    farmer_id: UUID,
    data: FarmerUpdate,
) -> Optional[Farmer]:
    farmer = get_farmer(db, farmer_id)
    if not farmer:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(farmer, key, value)
    db.commit()
    db.refresh(farmer)
    return farmer
