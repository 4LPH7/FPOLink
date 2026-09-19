"""Farmer management endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse, FarmerListResponse
from app.services.farmer_service import (
    create_farmer,
    get_farmer,
    list_farmers,
    update_farmer,
)

router = APIRouter(prefix="/api/farmers", tags=["farmers"])


@router.post("/{fpo_id}", status_code=status.HTTP_201_CREATED)
def create(
    fpo_id: str,
    data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """Register a new farmer under an FPO."""
    # Check if phone exists
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    user, farmer = create_farmer(db, UUID(fpo_id), data)
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(user.id),
        fpo_id=fpo_id,
        name=user.name,
        phone=user.phone,
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=user.language_preference,
        created_at=farmer.created_at,
    )


@router.get("/{fpo_id}")
def list_all(
    fpo_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """List farmers for an FPO with pagination and search."""
    farmers, total = list_farmers(db, UUID(fpo_id), page, page_size, search)

    return FarmerListResponse(
        farmers=[
            FarmerResponse(
                id=str(f.id),
                user_id=str(f.user_id),
                fpo_id=str(f.fpo_id),
                name=f.user.name,
                phone=f.user.phone,
                village=f.village,
                taluk=f.taluk,
                district=f.district,
                farm_area_acres=f.farm_area_acres,
                language_preference=f.user.language_preference,
                created_at=f.created_at,
            )
            for f in farmers
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/detail/{farmer_id}")
def get_one(
    farmer_id: str,
    db: Session = Depends(get_db),
):
    """Get farmer details."""
    farmer = get_farmer(db, UUID(farmer_id))
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        fpo_id=str(farmer.fpo_id),
        name=farmer.user.name,
        phone=farmer.user.phone,
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=farmer.user.language_preference,
        created_at=farmer.created_at,
    )


@router.put("/detail/{farmer_id}")
def update(
    farmer_id: str,
    data: FarmerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """Update farmer details."""
    farmer = update_farmer(db, UUID(farmer_id), data)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        fpo_id=str(farmer.fpo_id),
        name=farmer.user.name,
        phone=farmer.user.phone,
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=farmer.user.language_preference,
        created_at=farmer.created_at,
    )
