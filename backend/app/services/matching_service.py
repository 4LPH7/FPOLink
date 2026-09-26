"""Semi-Automatic Demand-Supply Matching Engine.

Evaluates standing farm plots and verified harvests against commercial buyer requirements,
computes multi-factor candidate match scores, and manages the staff confirmation workflow.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.geography import District
from app.models.harvest import Harvest, HarvestGrade, HarvestStatus
from app.models.supply_match import SupplyMatch
from app.models.user import User
from app.services.arbitrage import haversine_distance_km
from app.services.yield_estimator import estimate_crop_yield

# Grade values for comparison
GRADE_VALUES = {
    HarvestGrade.A: 3,
    HarvestGrade.B: 2,
    HarvestGrade.C: 1,
}


def compute_proximity_score(
    db: Session,
    delivery_district_id: Optional[UUID],
    delivery_location: Optional[str],
    farmer_district_id: Optional[UUID],
    farmer_village: Optional[str],
) -> tuple[float, Optional[float]]:
    """Compute proximity score (0-100) and approximate distance (km) between buyer and farmer."""
    # 1. If same district, high proximity
    if delivery_district_id and farmer_district_id and delivery_district_id == farmer_district_id:
        return 95.0, 18.0

    # 2. Try geospatial Haversine using District centroids
    if delivery_district_id and farmer_district_id:
        d1 = db.query(District).filter(District.id == delivery_district_id).first()
        d2 = db.query(District).filter(District.id == farmer_district_id).first()
        if d1 and d2 and d1.latitude and d1.longitude and d2.latitude and d2.longitude:
            dist_km = haversine_distance_km(d1.latitude, d1.longitude, d2.latitude, d2.longitude)
            prox_score = max(0.0, min(100.0, 100.0 - (dist_km / 300.0) * 100.0))
            return round(prox_score, 1), dist_km

    # 3. Fallback name comparison
    loc_lower = (delivery_location or "").lower()
    vil_lower = (farmer_village or "").lower()
    if loc_lower and vil_lower and (vil_lower in loc_lower or loc_lower in vil_lower):
        return 90.0, 25.0

    # Default moderate inter-district proximity baseline
    return 75.0, 65.0


def compute_candidate_score(
    crop_match: bool,
    proximity_score: float,
    distance_km: Optional[float],
    supply_qty: float,
    required_qty: float,
    available_date: Optional[date],
    required_date: date,
    candidate_grade: Optional[HarvestGrade],
    min_grade: HarvestGrade,
) -> tuple[float, Dict]:
    """Calculate composite match score (0-100) and detailed score breakdown."""
    if not crop_match or supply_qty <= 0 or required_qty <= 0:
        return 0.0, {"crop_match": False, "composite_score": 0.0}

    # 1. Crop Match Score
    s_crop = 100.0

    # 2. Proximity Score
    s_prox = max(0.0, min(100.0, proximity_score))

    # 3. Quantity Fit Ratio (1.0 = exact match)
    ratio = min(supply_qty, required_qty) / max(supply_qty, required_qty)
    s_qty = round(ratio * 100.0, 1)

    # 4. Timing Score (penalty for dates far apart)
    days_delta = 0
    if available_date:
        days_delta = abs((available_date - required_date).days)
        s_time = max(0.0, 100.0 - (days_delta * 4.0))  # 0 at 25 days delta
    else:
        s_time = 70.0  # neutral if harvest date unstated

    # 5. Grade Score
    cand_val = GRADE_VALUES.get(candidate_grade, 2) if candidate_grade else 2
    req_val = GRADE_VALUES.get(min_grade, 2)
    if cand_val >= req_val:
        s_grade = 100.0
    elif cand_val == req_val - 1:
        s_grade = 60.0
    else:
        s_grade = 20.0

    # Composite weighted average:
    # Crop (30%), Proximity (25%), Quantity (25%), Timing (15%), Grade (5%)
    composite = (
        0.30 * s_crop
        + 0.25 * s_prox
        + 0.25 * s_qty
        + 0.15 * s_time
        + 0.05 * s_grade
    )
    composite = round(composite, 1)

    breakdown = {
        "crop_match": True,
        "distance_km": distance_km,
        "proximity_score": s_prox,
        "quantity_fit_ratio": round(ratio, 2),
        "timing_days_delta": days_delta,
        "timing_score": round(s_time, 1),
        "grade_score": s_grade,
        "composite_score": composite,
    }
    return composite, breakdown


def find_candidate_matches_for_requirement(
    db: Session,
    requirement_id: UUID,
    max_candidates: int = 15,
) -> List[Dict]:
    """Search and rank available standing plots and verified harvests matching an open requirement."""
    req = (
        db.query(BuyerRequirement)
        .options(
            joinedload(BuyerRequirement.crop),
            joinedload(BuyerRequirement.buyer),
        )
        .filter(BuyerRequirement.id == requirement_id)
        .first()
    )
    if not req or req.status == "cancelled":
        return []

    unfulfilled_qty = max(0.0, req.quantity_kg - req.fulfilled_quantity_kg)
    if unfulfilled_qty <= 0:
        unfulfilled_qty = req.quantity_kg

    candidates: List[Dict] = []

    # -------------------------------------------------------------
    # 1. Search Standing Farm Plots
    # -------------------------------------------------------------
    farm_plots = (
        db.query(Farm)
        .join(Farmer, Farm.farmer_id == Farmer.id)
        .join(User, Farmer.user_id == User.id)
        .options(
            joinedload(Farm.farmer).joinedload(Farmer.user),
            joinedload(Farm.crop),
        )
        .filter(
            Farm.crop_id == req.crop_id,
            Farm.status == "active",
            (Farmer.fpo_id == req.fpo_id) if req.fpo_id else True,
        )
        .all()
    )

    for farm in farm_plots:
        avail_qty = farm.expected_yield_kg
        if not avail_qty or avail_qty <= 0:
            est = estimate_crop_yield(
                crop_name=farm.crop.name,
                area_acres=farm.area_acres,
                soil_type=farm.soil_type,
                irrigation_type=farm.irrigation_type,
                sowing_date=farm.sowing_date,
            )
            avail_qty = est["estimated_yield_kg"]

        prox_score, dist_km = compute_proximity_score(
            db,
            delivery_district_id=req.district_id or (req.buyer.district_id if req.buyer else None),
            delivery_location=req.delivery_location,
            farmer_district_id=farm.district_id,
            farmer_village=farm.village,
        )

        score, breakdown = compute_candidate_score(
            crop_match=True,
            proximity_score=prox_score,
            distance_km=dist_km,
            supply_qty=avail_qty,
            required_qty=unfulfilled_qty,
            available_date=farm.expected_harvest_date,
            required_date=req.required_date,
            candidate_grade=HarvestGrade.A,  # Default expected grade for healthy standing crop
            min_grade=req.min_grade,
        )

        candidates.append({
            "candidate_type": "farm_plot",
            "source_id": str(farm.id),
            "farmer_id": str(farm.farmer_id),
            "farmer_name": farm.farmer.user.name if farm.farmer.user else "Farmer",
            "farmer_phone": farm.farmer.user.phone if farm.farmer.user else "",
            "farmer_alerts_opt_in": bool(farm.farmer.alerts_opt_in),
            "village": farm.village or farm.farmer.village,
            "district": farm.farmer.district,
            "crop_id": str(farm.crop_id),
            "crop_name": farm.crop.name,
            "crop_tamil_name": farm.crop.tamil_name,
            "available_quantity_kg": avail_qty,
            "grade": "A",
            "available_date": farm.expected_harvest_date,
            "distance_km": dist_km,
            "match_score": score,
            "match_breakdown": breakdown,
        })

    # -------------------------------------------------------------
    # 2. Search Verified Harvest Stock
    # -------------------------------------------------------------
    harvests = (
        db.query(Harvest)
        .join(Farmer, Harvest.farmer_id == Farmer.id)
        .join(User, Farmer.user_id == User.id)
        .options(
            joinedload(Harvest.farmer).joinedload(Farmer.user),
            joinedload(Harvest.crop),
        )
        .filter(
            Harvest.crop_id == req.crop_id,
            Harvest.status.in_([HarvestStatus.SUBMITTED, HarvestStatus.VERIFIED, HarvestStatus.AGGREGATED]),
            (Farmer.fpo_id == req.fpo_id) if req.fpo_id else True,
        )
        .all()
    )

    for h in harvests:
        prox_score, dist_km = compute_proximity_score(
            db,
            delivery_district_id=req.district_id or (req.buyer.district_id if req.buyer else None),
            delivery_location=req.delivery_location,
            farmer_district_id=h.farmer.district_id,
            farmer_village=h.farmer.village,
        )

        score, breakdown = compute_candidate_score(
            crop_match=True,
            proximity_score=prox_score,
            distance_km=dist_km,
            supply_qty=h.quantity_kg,
            required_qty=unfulfilled_qty,
            available_date=h.harvest_date,
            required_date=req.required_date,
            candidate_grade=h.grade,
            min_grade=req.min_grade,
        )

        candidates.append({
            "candidate_type": "harvest",
            "source_id": str(h.id),
            "farmer_id": str(h.farmer_id),
            "farmer_name": h.farmer.user.name if h.farmer.user else "Farmer",
            "farmer_phone": h.farmer.user.phone if h.farmer.user else "",
            "farmer_alerts_opt_in": bool(h.farmer.alerts_opt_in),
            "village": h.farmer.village,
            "district": h.farmer.district,
            "crop_id": str(h.crop_id),
            "crop_name": h.crop.name,
            "crop_tamil_name": h.crop.tamil_name,
            "available_quantity_kg": h.quantity_kg,
            "grade": h.grade.value if hasattr(h.grade, "value") else str(h.grade),
            "available_date": h.harvest_date,
            "distance_km": dist_km,
            "match_score": score,
            "match_breakdown": breakdown,
        })

    # Sort descending by composite match score
    candidates.sort(key=lambda c: c["match_score"], reverse=True)
    return candidates[:max_candidates]


def create_or_suggest_match(
    db: Session,
    requirement_id: UUID,
    matched_quantity_kg: float,
    match_score: float,
    match_breakdown: Optional[Dict] = None,
    farm_id: Optional[UUID] = None,
    harvest_id: Optional[UUID] = None,
    offered_price_per_kg: Optional[Decimal] = None,
    staff_notes: Optional[str] = None,
) -> SupplyMatch:
    """Create a candidate or suggested match entry."""
    req = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
    if not req:
        raise ValueError("BuyerRequirement not found")

    # Determine FPO ID
    fpo_id = req.fpo_id
    if not fpo_id and farm_id:
        farm = db.query(Farm).join(Farmer).filter(Farm.id == farm_id).first()
        if farm and farm.farmer:
            fpo_id = farm.farmer.fpo_id
    if not fpo_id and harvest_id:
        h = db.query(Harvest).join(Farmer).filter(Harvest.id == harvest_id).first()
        if h and h.farmer:
            fpo_id = h.farmer.fpo_id

    if not fpo_id:
        fpo = db.query(Farmer).first()
        fpo_id = fpo.fpo_id if fpo else None

    match = SupplyMatch(
        buyer_requirement_id=requirement_id,
        farm_id=farm_id,
        harvest_id=harvest_id,
        fpo_id=fpo_id,
        matched_quantity_kg=matched_quantity_kg,
        offered_price_per_kg=offered_price_per_kg or req.max_price_per_kg,
        match_score=match_score,
        match_breakdown=match_breakdown,
        status="suggested",
        staff_notes=staff_notes,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def confirm_match_by_staff(
    db: Session,
    match_id: UUID,
    staff_user_id: UUID,
    notes: Optional[str] = None,
    offered_price: Optional[Decimal] = None,
) -> SupplyMatch:
    """Confirm a suggested match, update requirement fulfillment, and record audit timestamp."""
    match = (
        db.query(SupplyMatch)
        .options(joinedload(SupplyMatch.buyer_requirement))
        .filter(SupplyMatch.id == match_id)
        .first()
    )
    if not match:
        raise ValueError("SupplyMatch not found")

    match.status = "confirmed_by_staff"
    match.confirmed_by_id = staff_user_id
    match.confirmed_at = datetime.now(timezone.utc)
    if notes:
        match.staff_notes = notes
    if offered_price:
        match.offered_price_per_kg = offered_price

    # Increment fulfilled quantity on requirement
    req = match.buyer_requirement
    if req:
        req.fulfilled_quantity_kg = min(
            req.quantity_kg, req.fulfilled_quantity_kg + match.matched_quantity_kg
        )
        if req.fulfilled_quantity_kg >= req.quantity_kg:
            req.status = "fulfilled"
        elif req.fulfilled_quantity_kg > 0:
            req.status = "partially_fulfilled"

    db.commit()
    db.refresh(match)
    return match


def reject_match_by_staff(
    db: Session,
    match_id: UUID,
    staff_user_id: UUID,
    notes: Optional[str] = None,
) -> SupplyMatch:
    """Reject or dismiss a suggested or confirmed match."""
    match = (
        db.query(SupplyMatch)
        .options(joinedload(SupplyMatch.buyer_requirement))
        .filter(SupplyMatch.id == match_id)
        .first()
    )
    if not match:
        raise ValueError("SupplyMatch not found")

    # If it was confirmed, deduct fulfilled quantity
    if match.status == "confirmed_by_staff" and match.buyer_requirement:
        req = match.buyer_requirement
        req.fulfilled_quantity_kg = max(0.0, req.fulfilled_quantity_kg - match.matched_quantity_kg)
        if req.fulfilled_quantity_kg == 0:
            req.status = "open"
        else:
            req.status = "partially_fulfilled"

    match.status = "rejected"
    match.confirmed_by_id = staff_user_id
    if notes:
        match.staff_notes = notes

    db.commit()
    db.refresh(match)
    return match


def get_supply_demand_summary(
    db: Session,
    fpo_id: Optional[UUID] = None,
    district: Optional[str] = None,
) -> Dict:
    """Aggregate total standing acreage, estimated yield, harvest stock, and commercial demand by crop."""
    crops = db.query(Crop).filter(Crop.is_active == True).order_by(Crop.name.asc()).all()

    commodities_summary = []
    total_standing_acres = 0.0
    total_supply_kg = 0.0
    total_demand_kg = 0.0
    total_plots = 0
    total_reqs = 0

    for crop in crops:
        # 1. Standing farm plots
        farm_query = (
            db.query(
                func.coalesce(func.sum(Farm.area_acres), 0.0),
                func.coalesce(func.sum(Farm.expected_yield_kg), 0.0),
                func.count(Farm.id),
            )
            .join(Farmer, Farm.farmer_id == Farmer.id)
            .filter(
                Farm.crop_id == crop.id,
                Farm.status == "active",
                (Farmer.fpo_id == fpo_id) if fpo_id else True,
                (Farmer.district.ilike(f"%{district}%")) if district else True,
            )
        )
        standing_acres, standing_yield, plot_count = farm_query.first() or (0.0, 0.0, 0)
        standing_acres = float(standing_acres)
        standing_yield = float(standing_yield)

        # 2. Verified harvest stock
        harvest_query = (
            db.query(func.coalesce(func.sum(Harvest.quantity_kg), 0.0))
            .join(Farmer, Harvest.farmer_id == Farmer.id)
            .filter(
                Harvest.crop_id == crop.id,
                Harvest.status.in_([HarvestStatus.SUBMITTED, HarvestStatus.VERIFIED, HarvestStatus.AGGREGATED]),
                (Farmer.fpo_id == fpo_id) if fpo_id else True,
                (Farmer.district.ilike(f"%{district}%")) if district else True,
            )
        )
        verified_harvest = float(harvest_query.scalar() or 0.0)

        # 3. Buyer Requirements
        req_query = (
            db.query(
                func.coalesce(func.sum(BuyerRequirement.quantity_kg), 0.0),
                func.count(BuyerRequirement.id),
            )
            .filter(
                BuyerRequirement.crop_id == crop.id,
                BuyerRequirement.status.in_(["open", "partially_fulfilled"]),
                ((BuyerRequirement.fpo_id == fpo_id) | (BuyerRequirement.fpo_id.is_(None))) if fpo_id else True,
            )
        )
        demand_qty, req_count = req_query.first() or (0.0, 0)
        demand_qty = float(demand_qty)

        crop_supply = standing_yield + verified_harvest
        net_balance = crop_supply - demand_qty

        total_standing_acres += standing_acres
        total_supply_kg += crop_supply
        total_demand_kg += demand_qty
        total_plots += plot_count
        total_reqs += req_count

        if standing_acres > 0 or verified_harvest > 0 or demand_qty > 0:
            commodities_summary.append({
                "crop_id": str(crop.id),
                "crop_name": crop.name,
                "crop_tamil_name": crop.tamil_name,
                "standing_acres": round(standing_acres, 1),
                "estimated_standing_yield_kg": round(standing_yield, 1),
                "verified_harvest_kg": round(verified_harvest, 1),
                "total_supply_kg": round(crop_supply, 1),
                "total_demand_kg": round(demand_qty, 1),
                "net_balance_kg": round(net_balance, 1),
                "active_plots_count": plot_count,
                "open_requirements_count": req_count,
            })

    return {
        "fpo_id": str(fpo_id) if fpo_id else None,
        "district": district,
        "commodities": commodities_summary,
        "total_standing_acres": round(total_standing_acres, 1),
        "total_supply_kg": round(total_supply_kg, 1),
        "total_demand_kg": round(total_demand_kg, 1),
        "active_plots_total": total_plots,
        "open_requirements_total": total_reqs,
    }
