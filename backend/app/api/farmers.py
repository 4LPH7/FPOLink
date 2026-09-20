"""Farmer management endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.farmer import FarmerCreate, FarmerListResponse, FarmerResponse, FarmerUpdate
from app.services.farmer_service import (
    create_farmer,
    get_farmer,
    list_farmers,
    update_farmer,
)
from app.utils.phone import normalise_phone

router = APIRouter(prefix="/api/farmers", tags=["farmers"])


@router.post("/{fpo_id}", status_code=status.HTTP_201_CREATED)
def create(
    fpo_id: str,
    data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """Register a new farmer under an FPO with normalised phone."""
    try:
        norm_phone = normalise_phone(data.phone)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Check if phone exists in users or farmers
    existing_user = db.query(User).filter(User.phone == norm_phone).first()
    existing_farmer = db.query(Farmer).filter(Farmer.phone == norm_phone).first()
    if existing_user or existing_farmer:
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
        phone=farmer.phone or user.phone,
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=user.language_preference,
        lang=farmer.lang,
        alerts_opt_in=farmer.alerts_opt_in,
        alerts_opt_in_at=farmer.alerts_opt_in_at,
        alerts_opt_out_at=farmer.alerts_opt_out_at,
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
                name=f.user.name if f.user else "",
                phone=f.phone or (f.user.phone if f.user else ""),
                village=f.village,
                taluk=f.taluk,
                district=f.district,
                farm_area_acres=f.farm_area_acres,
                language_preference=f.user.language_preference if f.user else "ta",
                lang=f.lang,
                alerts_opt_in=f.alerts_opt_in,
                alerts_opt_in_at=f.alerts_opt_in_at,
                alerts_opt_out_at=f.alerts_opt_out_at,
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
        name=farmer.user.name if farmer.user else "",
        phone=farmer.phone or (farmer.user.phone if farmer.user else ""),
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=farmer.user.language_preference if farmer.user else "ta",
        lang=farmer.lang,
        alerts_opt_in=farmer.alerts_opt_in,
        alerts_opt_in_at=farmer.alerts_opt_in_at,
        alerts_opt_out_at=farmer.alerts_opt_out_at,
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
    if data.phone:
        try:
            norm_phone = normalise_phone(data.phone)
            data.phone = norm_phone
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
        existing_farmer = (
            db.query(Farmer)
            .filter(Farmer.phone == norm_phone, Farmer.id != UUID(farmer_id))
            .first()
        )
        if existing_farmer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered to another farmer",
            )

    farmer = update_farmer(db, UUID(farmer_id), data)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return FarmerResponse(
        id=str(farmer.id),
        user_id=str(farmer.user_id),
        fpo_id=str(farmer.fpo_id),
        name=farmer.user.name if farmer.user else "",
        phone=farmer.phone or (farmer.user.phone if farmer.user else ""),
        village=farmer.village,
        taluk=farmer.taluk,
        district=farmer.district,
        farm_area_acres=farmer.farm_area_acres,
        language_preference=farmer.user.language_preference if farmer.user else "ta",
        lang=farmer.lang,
        alerts_opt_in=farmer.alerts_opt_in,
        alerts_opt_in_at=farmer.alerts_opt_in_at,
        alerts_opt_out_at=farmer.alerts_opt_out_at,
        created_at=farmer.created_at,
    )
