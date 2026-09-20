"""Farmer service — business logic for farmer management."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.user import User, UserRole
from app.schemas.farmer import FarmerCreate, FarmerUpdate
from app.services.auth import hash_password
from app.utils.phone import normalise_phone


def create_farmer(
    db: Session,
    fpo_id: UUID,
    data: FarmerCreate,
) -> Tuple[User, Farmer]:
    """Create a new farmer with user account and normalised phone."""
    norm_phone = normalise_phone(data.phone)
    now = datetime.now(timezone.utc)
    opt_in = bool(data.alerts_opt_in or data.consent_given)

    # Create user account
    user = User(
        name=data.name,
        phone=norm_phone,
        role=UserRole.FARMER,
        hashed_password=hash_password(data.password),
        is_active=True,
        language_preference=data.language_preference,
        consent_given=opt_in,
        consent_date=now if opt_in else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create farmer profile
    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo_id,
        phone=norm_phone,
        village=data.village,
        taluk=data.taluk,
        district=data.district,
        farm_area_acres=data.farm_area_acres,
        lang=data.lang or data.language_preference or "ta",
        alerts_opt_in=opt_in,
        alerts_opt_in_at=now if opt_in else None,
        alerts_opt_out_at=None,
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
    query = db.query(Farmer).join(User, Farmer.user_id == User.id).filter(Farmer.fpo_id == fpo_id)

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

    update_dict = data.model_dump(exclude_unset=True)
    now = datetime.now(timezone.utc)

    # Handle phone normalisation and user.phone sync
    if "phone" in update_dict and update_dict["phone"]:
        norm_phone = normalise_phone(update_dict["phone"])
        farmer.phone = norm_phone
        if farmer.user:
            farmer.user.phone = norm_phone
        del update_dict["phone"]

    # Handle alerts opt-in transition timestamps
    if "alerts_opt_in" in update_dict:
        new_val = bool(update_dict["alerts_opt_in"])
        if new_val and not farmer.alerts_opt_in:
            farmer.alerts_opt_in_at = now
            farmer.alerts_opt_out_at = None
        elif not new_val and farmer.alerts_opt_in:
            farmer.alerts_opt_out_at = now
        farmer.alerts_opt_in = new_val
        if farmer.user:
            farmer.user.consent_given = new_val
            farmer.user.consent_date = now if new_val else None
        del update_dict["alerts_opt_in"]

    for key, value in update_dict.items():
        setattr(farmer, key, value)

    db.commit()
    db.refresh(farmer)
    return farmer
