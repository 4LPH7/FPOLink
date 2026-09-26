"""Commercial Buyers and Procurement Requirements API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role, verify_fpo_access
from app.database import get_db
from app.models.user import User
from app.schemas.buyer import (
    BuyerCreate,
    BuyerListResponse,
    BuyerRequirementCreate,
    BuyerRequirementListResponse,
    BuyerRequirementResponse,
    BuyerRequirementUpdate,
    BuyerResponse,
    BuyerUpdate,
)
from app.services.buyer_service import (
    create_buyer,
    create_buyer_requirement,
    delete_buyer,
    get_buyer,
    get_buyer_requirement,
    list_buyer_requirements,
    list_buyers,
    update_buyer,
    update_buyer_requirement,
)
from app.services.csv_import import import_buyers_csv

router = APIRouter(prefix="/buyers", tags=["buyers"])


def _buyer_to_response(b) -> BuyerResponse:
    open_reqs = len([r for r in b.requirements if r.status in ("open", "partially_fulfilled")]) if hasattr(b, "requirements") and b.requirements else 0
    return BuyerResponse(
        id=str(b.id),
        company_name=b.company_name,
        buyer_type=b.buyer_type,
        contact_name=b.contact_name,
        contact_phone=b.contact_phone,
        contact_email=b.contact_email,
        location=b.location,
        district=b.district,
        district_id=str(b.district_id) if b.district_id else None,
        fpo_id=str(b.fpo_id) if b.fpo_id else None,
        gstin=b.gstin,
        verified=b.verified,
        open_requirements_count=open_reqs,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


def _req_to_response(r) -> BuyerRequirementResponse:
    return BuyerRequirementResponse(
        id=str(r.id),
        buyer_id=str(r.buyer_id),
        buyer_name=r.buyer.company_name if r.buyer else None,
        buyer_phone=r.buyer.contact_phone if r.buyer else None,
        fpo_id=str(r.fpo_id) if r.fpo_id else None,
        crop_id=str(r.crop_id),
        crop_name=r.crop.name if r.crop else None,
        crop_tamil_name=r.crop.tamil_name if r.crop else None,
        variety_id=str(r.variety_id) if r.variety_id else None,
        variety_name=r.variety.name if r.variety else None,
        quantity_kg=r.quantity_kg,
        fulfilled_quantity_kg=r.fulfilled_quantity_kg,
        min_grade=r.min_grade.value if hasattr(r.min_grade, "value") else str(r.min_grade),
        required_date=r.required_date,
        delivery_window_days=r.delivery_window_days,
        max_price_per_kg=r.max_price_per_kg,
        delivery_location=r.delivery_location,
        status=r.status,
        notes=r.notes,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


# ---------------------------------------------------------------------------
# Buyer Requirements (Defined before /{buyer_id} to prevent path shadowing)
# ---------------------------------------------------------------------------


@router.post("/requirements", response_model=BuyerRequirementResponse, status_code=status.HTTP_201_CREATED)
def post_requirement(
    data: BuyerRequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Post a commercial crop procurement requirement."""
    if data.fpo_id and not verify_fpo_access(data.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to post requirement for this FPO")

    try:
        req = create_buyer_requirement(db, data, created_by_user_id=current_user.id)
        full_req = get_buyer_requirement(db, req.id)
        return _req_to_response(full_req or req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requirements", response_model=BuyerRequirementListResponse)
def list_requirements(
    buyer_id: Optional[UUID] = None,
    fpo_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List procurement requirements with demand metrics."""
    skip = (page - 1) * page_size
    reqs, total_count, total_qty = list_buyer_requirements(
        db=db,
        buyer_id=buyer_id,
        fpo_id=fpo_id,
        crop_id=crop_id,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )
    return BuyerRequirementListResponse(
        requirements=[_req_to_response(r) for r in reqs],
        total=total_count,
        total_quantity_kg=total_qty,
    )


@router.get("/requirements/{req_id}", response_model=BuyerRequirementResponse)
def get_requirement(
    req_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of a single procurement requirement."""
    req = get_buyer_requirement(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return _req_to_response(req)


@router.put("/requirements/{req_id}", response_model=BuyerRequirementResponse)
def update_requirement(
    req_id: UUID,
    data: BuyerRequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Update procurement requirement details."""
    req = get_buyer_requirement(db, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")

    if req.fpo_id and not verify_fpo_access(req.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to modify requirement for this FPO")

    updated = update_buyer_requirement(db, req_id, data)
    full_req = get_buyer_requirement(db, req_id)
    return _req_to_response(full_req or updated)


@router.post("/import-csv")
def import_csv(
    fpo_id: Optional[UUID] = Query(None),
    csv_text: str = Body(..., media_type="text/plain"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Bulk import commercial buyers and procurement requirements via CSV."""
    if fpo_id and not verify_fpo_access(fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to import buyers for this FPO")

    res = import_buyers_csv(db, fpo_id, csv_text, created_by_user_id=current_user.id)
    return res


# ---------------------------------------------------------------------------
# Buyer Profiles
# ---------------------------------------------------------------------------


@router.post("/", response_model=BuyerResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Register a new commercial buyer (staff-mediated)."""
    if data.fpo_id and not verify_fpo_access(data.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to register buyer for this FPO")

    buyer = create_buyer(db, data, created_by_user_id=current_user.id)
    return _buyer_to_response(buyer)


@router.get("/", response_model=BuyerListResponse)
def list_all(
    fpo_id: Optional[UUID] = None,
    district: Optional[str] = None,
    buyer_type: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List commercial buyers with pagination and filters."""
    skip = (page - 1) * page_size
    buyers, total = list_buyers(
        db=db,
        fpo_id=fpo_id,
        district=district,
        buyer_type=buyer_type,
        skip=skip,
        limit=page_size,
    )
    return BuyerListResponse(
        buyers=[_buyer_to_response(b) for b in buyers],
        total=total,
    )


@router.get("/{buyer_id}", response_model=BuyerResponse)
def get_one(
    buyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of a commercial buyer."""
    buyer = get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    return _buyer_to_response(buyer)


@router.put("/{buyer_id}", response_model=BuyerResponse)
def update(
    buyer_id: UUID,
    data: BuyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Update commercial buyer profile."""
    buyer = get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    if buyer.fpo_id and not verify_fpo_access(buyer.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to modify buyer for this FPO")

    updated = update_buyer(db, buyer_id, data)
    return _buyer_to_response(updated)


@router.delete("/{buyer_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    buyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin"])),
):
    """Delete a commercial buyer profile."""
    buyer = get_buyer(db, buyer_id)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    if buyer.fpo_id and not verify_fpo_access(buyer.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete buyer for this FPO")

    delete_buyer(db, buyer_id)
    return None
