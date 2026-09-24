"""Harvest submission, querying, and verification endpoints."""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.farmer import Farmer
from app.models.harvest import Harvest
from app.models.user import User
from app.schemas.harvest import (
    HarvestCreate,
    HarvestListResponse,
    HarvestResponse,
    HarvestStatusUpdate,
)
from app.services import harvest_service

router = APIRouter(prefix="/api/harvest", tags=["harvest"])


def _to_response(h: Harvest) -> HarvestResponse:
    farmer_name = None
    if h.farmer and h.farmer.user:
        farmer_name = h.farmer.user.name
    crop_name = h.crop.name if h.crop else "Unknown"
    crop_tamil_name = h.crop.tamil_name if h.crop else None
    return HarvestResponse(
        id=h.id,
        farmer_id=h.farmer_id,
        farmer_name=farmer_name,
        crop_id=h.crop_id,
        crop_name=crop_name,
        crop_tamil_name=crop_tamil_name,
        quantity_kg=h.quantity_kg,
        grade=h.grade.value if hasattr(h.grade, "value") else str(h.grade),
        harvest_date=h.harvest_date,
        status=h.status.value if hasattr(h.status, "value") else str(h.status),
        source_message_id=h.source_message_id,
        notes=h.notes,
        created_at=h.created_at,
    )


@router.post(
    "",
    response_model=HarvestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new harvest",
)
def create_harvest(
    payload: HarvestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a new harvest entry.

    Farmers submit for themselves; FPO staff or admin can submit on behalf of a farmer.
    """
    user_role = (
        current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    )

    resolved_farmer_id: Optional[UUID] = None
    if user_role == "farmer":
        farmer = db.query(Farmer).filter(Farmer.user_id == current_user.id).first()
        if not farmer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Farmer profile not found for this user account",
            )
        resolved_farmer_id = farmer.id
    else:
        # Admin or staff can specify target farmer_id
        if not payload.farmer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="farmer_id is required when staff creates a harvest",
            )
        resolved_farmer_id = payload.farmer_id

    try:
        harvest = harvest_service.create_harvest(db, payload, resolved_farmer_id=resolved_farmer_id)
        return _to_response(harvest)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=HarvestListResponse,
    summary="List harvests with filtering and pagination",
)
def list_harvests(
    farmer_id: Optional[UUID] = None,
    fpo_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List harvests. Farmers see only their own harvests."""
    user_role = (
        current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    )

    if user_role == "farmer":
        farmer = db.query(Farmer).filter(Farmer.user_id == current_user.id).first()
        if farmer:
            farmer_id = farmer.id

    try:
        items, total = harvest_service.list_harvests(
            db,
            fpo_id=fpo_id,
            farmer_id=farmer_id,
            crop_id=crop_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return HarvestListResponse(
            harvests=[_to_response(h) for h in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/aggregation",
    summary="Get harvest aggregation summary by crop and grade",
)
def get_harvest_aggregation(
    fpo_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """Get aggregated harvest batches grouped by crop with grade distribution."""
    query = db.query(Harvest).options(joinedload(Harvest.crop), joinedload(Harvest.farmer))
    if fpo_id:
        query = query.join(Farmer, Harvest.farmer_id == Farmer.id).filter(Farmer.fpo_id == fpo_id)

    harvests = query.all()
    total_pooled_kg = sum(h.quantity_kg for h in harvests)

    by_crop = {}
    for h in harvests:
        cid = str(h.crop_id)
        if cid not in by_crop:
            cname = h.crop.name if h.crop else "Unknown"
            ctamil = h.crop.tamil_name if h.crop else None
            by_crop[cid] = {
                "crop_id": cid,
                "crop_name": cname,
                "crop_tamil_name": ctamil,
                "total_kg": 0.0,
                "farmer_ids": set(),
                "grade_counts": {"A": 0.0, "B": 0.0, "C": 0.0},
            }
        by_crop[cid]["total_kg"] += h.quantity_kg
        by_crop[cid]["farmer_ids"].add(str(h.farmer_id))
        grade_key = h.grade.value if hasattr(h.grade, "value") else str(h.grade).upper()
        if grade_key in by_crop[cid]["grade_counts"]:
            by_crop[cid]["grade_counts"][grade_key] += h.quantity_kg

    batches = []
    for cid, data in by_crop.items():
        total_kg = data["total_kg"]
        grade_breakdown = {}
        for g, g_kg in data["grade_counts"].items():
            pct = round((g_kg / total_kg * 100), 1) if total_kg > 0 else 0.0
            grade_breakdown[g] = {"kg": round(g_kg, 1), "pct": pct}

        c_lower = data["crop_name"].lower()
        batches.append({
            "crop_id": data["crop_id"],
            "crop_name": data["crop_name"],
            "crop_tamil_name": data["crop_tamil_name"],
            "total_kg": round(total_kg, 1),
            "farmer_count": len(data["farmer_ids"]),
            "grade_breakdown": grade_breakdown,
            "status": "Ready for Wholesale Dispatch" if "turmeric" in c_lower else "Matched with Buyer Contract",
            "warehouse": "Erode Warehouse #2" if "turmeric" in c_lower else "Kodumudi Cold Storage",
        })

    return {
        "total_pooled_kg": round(total_pooled_kg, 1),
        "batch_count": len(batches),
        "batches": batches,
    }


@router.get(
    "/{harvest_id}",
    response_model=HarvestResponse,
    summary="Get harvest details by ID",
)
def get_harvest(
    harvest_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch harvest by ID."""
    harvest = harvest_service.get_harvest_by_id(db, harvest_id)
    if not harvest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Harvest with ID {harvest_id} not found",
        )

    user_role = (
        current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    )
    if user_role == "farmer":
        farmer = db.query(Farmer).filter(Farmer.user_id == current_user.id).first()
        if not farmer or harvest.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this harvest",
            )

    return _to_response(harvest)


@router.patch(
    "/{harvest_id}/status",
    response_model=HarvestResponse,
    summary="Update harvest status (FPO Staff/Admin)",
)
def update_harvest_status(
    harvest_id: UUID,
    payload: HarvestStatusUpdate,
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
    db: Session = Depends(get_db),
):
    """Update harvest status following lifecycle rules (SUBMITTED -> VERIFIED -> AGGREGATED -> SOLD)."""
    try:
        updated = harvest_service.update_harvest_status(
            db, harvest_id, payload.status, notes=payload.notes
        )
        return _to_response(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
