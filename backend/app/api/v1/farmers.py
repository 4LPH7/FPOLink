"""Farmer management endpoints (v1)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.config import settings
from app.database import get_db
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.user import User, UserRole
from app.schemas.farmer import (
    FarmerCreate,
    FarmerListResponse,
    FarmerResponse,
    FarmerUpdate,
    WhatsAppInviteResponse,
)
from app.services.farmer_service import (
    create_farmer,
    get_farmer,
    list_farmers,
    update_farmer,
)
from app.utils.phone import normalise_phone

router = APIRouter(prefix="/farmers", tags=["farmers-v1"])


def _enforce_farmer_fpo_scope(db: Session, current_user: User, fpo_id: UUID) -> None:
    """Ensure staff can only access farmers within their permitted FPOs."""
    role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if role_val in ("admin", "state_admin"):
        return

    permitted_fpos = {
        row[0] for row in db.query(FPO.id).filter(FPO.contact_phone == current_user.phone).all()
    }
    user_fpo = getattr(current_user, "fpo_id", None)
    if user_fpo:
        permitted_fpos.add(user_fpo if isinstance(user_fpo, UUID) else UUID(str(user_fpo)))

    if fpo_id not in permitted_fpos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not authorized to access farmers outside their permitted FPO",
        )


@router.post("/{fpo_id}", status_code=status.HTTP_201_CREATED)
def create(
    fpo_id: str,
    data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Register a new farmer under an FPO with normalised phone."""
    try:
        norm_phone = normalise_phone(data.phone)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    existing_user = db.query(User).filter(User.phone == norm_phone).first()
    existing_farmer = db.query(Farmer).filter(Farmer.phone == norm_phone).first()
    if existing_user or existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    try:
        f_uuid = UUID(fpo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FPO UUID")

    _enforce_farmer_fpo_scope(db, current_user, f_uuid)
    user, farmer = create_farmer(db, f_uuid, data)

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
        notice_sent_at=farmer.notice_sent_at,
        created_at=farmer.created_at,
    )


@router.get("/{fpo_id}")
def list_all(
    fpo_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """List farmers for an FPO with pagination and search."""
    try:
        f_uuid = UUID(fpo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FPO UUID")

    _enforce_farmer_fpo_scope(db, current_user, f_uuid)
    farmers, total = list_farmers(db, f_uuid, page, page_size, search)

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
                notice_sent_at=f.notice_sent_at,
                created_at=f.created_at,
            )
            for f in farmers
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/detail/{farmer_id}", response_model=FarmerResponse)
def get_one(
    farmer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Get single farmer details."""
    try:
        f_uuid = UUID(farmer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Farmer UUID")

    farmer = get_farmer(db, f_uuid)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    _enforce_farmer_fpo_scope(db, current_user, farmer.fpo_id)

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
        notice_sent_at=farmer.notice_sent_at,
        created_at=farmer.created_at,
    )


@router.put("/{farmer_id}", response_model=FarmerResponse)
def update(
    farmer_id: str,
    data: FarmerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Update farmer details."""
    try:
        f_uuid = UUID(farmer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Farmer UUID")

    farmer = get_farmer(db, f_uuid)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    _enforce_farmer_fpo_scope(db, current_user, farmer.fpo_id)
    updated = update_farmer(db, f_uuid, data)

    return FarmerResponse(
        id=str(updated.id),
        user_id=str(updated.user_id),
        fpo_id=str(updated.fpo_id),
        name=updated.user.name if updated.user else "",
        phone=updated.phone or (updated.user.phone if updated.user else ""),
        village=updated.village,
        taluk=updated.taluk,
        district=updated.district,
        farm_area_acres=updated.farm_area_acres,
        language_preference=updated.user.language_preference if updated.user else "ta",
        lang=updated.lang,
        alerts_opt_in=updated.alerts_opt_in,
        alerts_opt_in_at=updated.alerts_opt_in_at,
        alerts_opt_out_at=updated.alerts_opt_out_at,
        notice_sent_at=updated.notice_sent_at,
        created_at=updated.created_at,
    )


@router.get("/{farmer_id}/wa-invite", response_model=WhatsAppInviteResponse)
def get_whatsapp_invite(
    farmer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Generate wa.me click-to-chat invite link for a farmer."""
    try:
        f_uuid = UUID(farmer_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Farmer UUID")

    farmer = get_farmer(db, f_uuid)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    _enforce_farmer_fpo_scope(db, current_user, farmer.fpo_id)

    raw_phone = farmer.phone or (farmer.user.phone if farmer.user else "")
    bot_number = settings.META_PHONE_NUMBER_ID or "919876543210"
    prefilled_text = "VANAKKAM" if (farmer.lang or "ta") == "ta" else "START"
    wa_link = f"https://wa.me/{bot_number}?text={prefilled_text}"

    return WhatsAppInviteResponse(
        farmer_id=str(farmer.id),
        phone=raw_phone,
        wa_link=wa_link,
        prefilled_text=prefilled_text,
    )
