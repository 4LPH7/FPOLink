"""Semi-Automatic Demand-Supply Matching API endpoints."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, require_role, verify_fpo_access
from app.database import get_db
from app.models.buyer import BuyerRequirement
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.harvest import Harvest
from app.models.supply_match import SupplyMatch
from app.models.user import User
from app.schemas.matching import (
    MatchCandidate,
    MatchCandidateListResponse,
    MatchConfirmRequest,
    MatchCreate,
    MatchListResponse,
    MatchResponse,
    SupplyDemandCropSummary,
    SupplyDemandSummaryResponse,
)
from app.services.matching_service import (
    confirm_match_by_staff,
    create_or_suggest_match,
    find_candidate_matches_for_requirement,
    get_supply_demand_summary,
    reject_match_by_staff,
)

router = APIRouter(prefix="/matching", tags=["matching"])


def _match_to_response(m) -> MatchResponse:
    # Resolve farmer from farm or harvest
    farmer = None
    crop_name = None
    if m.farm and m.farm.farmer:
        farmer = m.farm.farmer
        crop_name = m.farm.crop.name if m.farm.crop else None
    elif m.harvest and m.harvest.farmer:
        farmer = m.harvest.farmer
        crop_name = m.harvest.crop.name if m.harvest.crop else None

    buyer_name = m.buyer_requirement.buyer.company_name if (m.buyer_requirement and m.buyer_requirement.buyer) else None

    return MatchResponse(
        id=str(m.id),
        buyer_requirement_id=str(m.buyer_requirement_id),
        buyer_name=buyer_name,
        farm_id=str(m.farm_id) if m.farm_id else None,
        harvest_id=str(m.harvest_id) if m.harvest_id else None,
        fpo_id=str(m.fpo_id),
        farmer_id=str(farmer.id) if farmer else None,
        farmer_name=farmer.user.name if (farmer and farmer.user) else None,
        farmer_phone=farmer.user.phone if (farmer and farmer.user) else None,
        crop_name=crop_name,
        matched_quantity_kg=m.matched_quantity_kg,
        offered_price_per_kg=m.offered_price_per_kg,
        match_score=m.match_score,
        match_breakdown=m.match_breakdown,
        status=m.status,
        staff_notes=m.staff_notes,
        confirmed_by_name=m.confirmed_by.name if m.confirmed_by else None,
        confirmed_at=m.confirmed_at,
        notified_at=m.notified_at,
        farmer_responded_at=m.farmer_responded_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("/candidates/{requirement_id}", response_model=MatchCandidateListResponse)
def get_candidates(
    requirement_id: UUID,
    max_candidates: int = Query(default=15, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search and score available standing plots and verified harvests for a buyer requirement."""
    req = (
        db.query(BuyerRequirement)
        .options(joinedload(BuyerRequirement.buyer), joinedload(BuyerRequirement.crop))
        .filter(BuyerRequirement.id == requirement_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Buyer requirement not found")

    candidates_raw = find_candidate_matches_for_requirement(
        db, requirement_id, max_candidates=max_candidates
    )

    return MatchCandidateListResponse(
        requirement_id=str(req.id),
        buyer_id=str(req.buyer_id),
        buyer_name=req.buyer.company_name if req.buyer else "Buyer",
        crop_name=req.crop.name if req.crop else "Crop",
        required_quantity_kg=req.quantity_kg,
        required_date=req.required_date,
        delivery_location=req.delivery_location,
        candidates=[MatchCandidate(**c) for c in candidates_raw],
        total_candidates=len(candidates_raw),
    )


@router.post("/suggest", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def suggest_match(
    data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Record a suggested demand-supply match."""
    if not verify_fpo_access(data.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized for this FPO")

    try:
        match = create_or_suggest_match(
            db=db,
            requirement_id=data.buyer_requirement_id,
            matched_quantity_kg=data.matched_quantity_kg,
            match_score=data.match_score,
            match_breakdown=data.match_breakdown,
            farm_id=data.farm_id,
            harvest_id=data.harvest_id,
            offered_price_per_kg=data.offered_price_per_kg,
            staff_notes=data.staff_notes,
        )
        full_match = (
            db.query(SupplyMatch)
            .options(
                joinedload(SupplyMatch.buyer_requirement).joinedload(BuyerRequirement.buyer),
                joinedload(SupplyMatch.farm).joinedload(Farm.farmer).joinedload(Farmer.user),
                joinedload(SupplyMatch.farm).joinedload(Farm.crop),
                joinedload(SupplyMatch.harvest).joinedload(Harvest.farmer).joinedload(Farmer.user),
                joinedload(SupplyMatch.harvest).joinedload(Harvest.crop),
                joinedload(SupplyMatch.confirmed_by),
            )
            .filter(SupplyMatch.id == match.id)
            .first()
        )
        return _match_to_response(full_match or match)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{match_id}/confirm", response_model=MatchResponse)
def confirm_match(
    match_id: UUID,
    data: MatchConfirmRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Staff confirmation of a candidate match."""
    match = db.query(SupplyMatch).filter(SupplyMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Supply match not found")

    if not verify_fpo_access(match.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized for this FPO")

    confirmed = confirm_match_by_staff(
        db=db,
        match_id=match_id,
        staff_user_id=current_user.id,
        notes=data.staff_notes,
        offered_price=data.offered_price_per_kg,
    )

    full_match = (
        db.query(SupplyMatch)
        .options(
            joinedload(SupplyMatch.buyer_requirement).joinedload(BuyerRequirement.buyer),
            joinedload(SupplyMatch.farm).joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.farm).joinedload(Farm.crop),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.crop),
            joinedload(SupplyMatch.confirmed_by),
        )
        .filter(SupplyMatch.id == confirmed.id)
        .first()
    )
    return _match_to_response(full_match or confirmed)


@router.post("/{match_id}/reject", response_model=MatchResponse)
def reject_match(
    match_id: UUID,
    notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Reject or dismiss a suggested or confirmed match."""
    match = db.query(SupplyMatch).filter(SupplyMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Supply match not found")

    if not verify_fpo_access(match.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized for this FPO")

    rejected = reject_match_by_staff(
        db=db,
        match_id=match_id,
        staff_user_id=current_user.id,
        notes=notes,
    )

    full_match = (
        db.query(SupplyMatch)
        .options(
            joinedload(SupplyMatch.buyer_requirement).joinedload(BuyerRequirement.buyer),
            joinedload(SupplyMatch.farm).joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.farm).joinedload(Farm.crop),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.crop),
            joinedload(SupplyMatch.confirmed_by),
        )
        .filter(SupplyMatch.id == rejected.id)
        .first()
    )
    return _match_to_response(full_match or rejected)


@router.get("/summary", response_model=SupplyDemandSummaryResponse)
def summary(
    fpo_id: Optional[UUID] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Statewide or FPO-scoped supply & demand balance summary across all commodities."""
    # Scope to user FPO if restricted
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role in ("fpo_admin", "fpo_staff") and current_user.fpo_id:
        fpo_id = current_user.fpo_id

    res = get_supply_demand_summary(db, fpo_id=fpo_id, district=district)
    return SupplyDemandSummaryResponse(
        fpo_id=res.get("fpo_id"),
        district=res.get("district"),
        commodities=[SupplyDemandCropSummary(**c) for c in res.get("commodities", [])],
        total_standing_acres=res.get("total_standing_acres", 0.0),
        total_supply_kg=res.get("total_supply_kg", 0.0),
        total_demand_kg=res.get("total_demand_kg", 0.0),
        active_plots_total=res.get("active_plots_total", 0),
        open_requirements_total=res.get("open_requirements_total", 0),
    )


@router.get("/list", response_model=MatchListResponse)
def list_matches(
    fpo_id: Optional[UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List supply matches with pagination and filtering."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role in ("fpo_admin", "fpo_staff") and current_user.fpo_id:
        fpo_id = current_user.fpo_id

    query = (
        db.query(SupplyMatch)
        .options(
            joinedload(SupplyMatch.buyer_requirement).joinedload(BuyerRequirement.buyer),
            joinedload(SupplyMatch.farm).joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.farm).joinedload(Farm.crop),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.farmer).joinedload(Farmer.user),
            joinedload(SupplyMatch.harvest).joinedload(Harvest.crop),
            joinedload(SupplyMatch.confirmed_by),
        )
    )
    if fpo_id:
        query = query.filter(SupplyMatch.fpo_id == fpo_id)
    if status_filter:
        query = query.filter(SupplyMatch.status == status_filter)

    total = query.count()
    matches = query.order_by(SupplyMatch.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return MatchListResponse(
        matches=[_match_to_response(m) for m in matches],
        total=total,
    )
