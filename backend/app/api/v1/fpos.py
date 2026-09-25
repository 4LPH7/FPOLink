"""FPO management endpoints (v1)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.fpo import FPOCreate, FPODashboardStats, FPOResponse, FPOUpdate
from app.services.fpo_service import (
    create_fpo,
    get_dashboard_stats,
    get_fpo,
    list_fpos,
    update_fpo,
)

router = APIRouter(prefix="/fpos", tags=["fpos-v1"])


@router.post("/", response_model=FPOResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: FPOCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin"])),
):
    """Create a new FPO."""
    fpo = create_fpo(db, data)
    return FPOResponse(
        id=str(fpo.id),
        name=fpo.name,
        registration_number=fpo.registration_number,
        district=fpo.district,
        village=fpo.village,
        state=fpo.state,
        contact_phone=fpo.contact_phone,
        contact_email=fpo.contact_email,
        address=fpo.address,
        created_at=fpo.created_at,
    )


@router.get("/")
def list_all(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all registered FPOs."""
    fpos = list_fpos(db, skip, limit)
    return {
        "fpos": [
            FPOResponse(
                id=str(f.id),
                name=f.name,
                registration_number=f.registration_number,
                district=f.district,
                village=f.village,
                state=f.state,
                contact_phone=f.contact_phone,
                contact_email=f.contact_email,
                address=f.address,
                created_at=f.created_at,
            )
            for f in fpos
        ]
    }


@router.get("/{fpo_id}", response_model=FPOResponse)
def get_one(fpo_id: str, db: Session = Depends(get_db)):
    """Get FPO by ID."""
    try:
        f_uuid = UUID(fpo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FPO UUID")

    fpo = get_fpo(db, f_uuid)
    if not fpo:
        raise HTTPException(status_code=404, detail="FPO not found")
    return FPOResponse(
        id=str(fpo.id),
        name=fpo.name,
        registration_number=fpo.registration_number,
        district=fpo.district,
        village=fpo.village,
        state=fpo.state,
        contact_phone=fpo.contact_phone,
        contact_email=fpo.contact_email,
        address=fpo.address,
        created_at=fpo.created_at,
    )


@router.put("/{fpo_id}", response_model=FPOResponse)
def update(
    fpo_id: str,
    data: FPOUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin"])),
):
    """Update FPO details."""
    try:
        f_uuid = UUID(fpo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FPO UUID")

    fpo = update_fpo(db, f_uuid, data)
    if not fpo:
        raise HTTPException(status_code=404, detail="FPO not found")
    return FPOResponse(
        id=str(fpo.id),
        name=fpo.name,
        registration_number=fpo.registration_number,
        district=fpo.district,
        village=fpo.village,
        state=fpo.state,
        contact_phone=fpo.contact_phone,
        contact_email=fpo.contact_email,
        address=fpo.address,
        created_at=fpo.created_at,
    )


@router.get("/{fpo_id}/stats", response_model=FPODashboardStats)
def stats(fpo_id: str, db: Session = Depends(get_db)):
    """Get aggregate statistics for an FPO dashboard."""
    try:
        f_uuid = UUID(fpo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FPO UUID")

    return get_dashboard_stats(db, f_uuid)
