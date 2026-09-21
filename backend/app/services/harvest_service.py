"""Harvest service — submission, validation, idempotency, and status lifecycle."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.harvest import Harvest, HarvestGrade, HarvestStatus
from app.schemas.harvest import HarvestCreate

logger = logging.getLogger(__name__)

# Valid state machine transitions for harvests
ALLOWED_TRANSITIONS = {
    HarvestStatus.SUBMITTED: {HarvestStatus.VERIFIED},
    HarvestStatus.VERIFIED: {HarvestStatus.AGGREGATED, HarvestStatus.SUBMITTED},
    HarvestStatus.AGGREGATED: {HarvestStatus.SOLD, HarvestStatus.VERIFIED},
    HarvestStatus.SOLD: set(),  # terminal state
}

MIN_QUANTITY_KG = 1.0
MAX_QUANTITY_KG = 50_000.0
MAX_PAST_DAYS = 14


def validate_harvest_parameters(
    quantity_kg: float,
    grade: HarvestGrade | str,
    harvest_date: date,
) -> None:
    """Validate harvest entry business rules."""
    if quantity_kg < MIN_QUANTITY_KG or quantity_kg > MAX_QUANTITY_KG:
        raise ValueError(
            f"Quantity must be between {MIN_QUANTITY_KG:,.0f} and {MAX_QUANTITY_KG:,.0f} kg (got {quantity_kg})"
        )

    grade_val = grade.value if isinstance(grade, HarvestGrade) else str(grade).upper()
    if grade_val not in ("A", "B", "C"):
        raise ValueError(f"Invalid harvest grade: {grade}. Allowed grades: A, B, C")

    today = date.today()
    if harvest_date > today:
        raise ValueError(
            f"Harvest date cannot be in the future (got {harvest_date}, today is {today})"
        )

    earliest_allowed = today - timedelta(days=MAX_PAST_DAYS)
    if harvest_date < earliest_allowed:
        raise ValueError(
            f"Harvest date cannot be more than {MAX_PAST_DAYS} days in the past (got {harvest_date}, earliest is {earliest_allowed})"
        )


def create_harvest(
    db: Session,
    data: HarvestCreate,
    resolved_farmer_id: Optional[UUID] = None,
) -> Harvest:
    """Create a harvest record with idempotency via source_message_id."""
    farmer_id = resolved_farmer_id or data.farmer_id
    if not farmer_id:
        raise ValueError("farmer_id is required to submit a harvest")

    # Verify farmer exists
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise ValueError(f"Farmer with ID {farmer_id} not found")

    h_date = data.harvest_date or date.today()
    validate_harvest_parameters(data.quantity_kg, data.grade, h_date)

    # Idempotency check: if source_message_id is provided and already recorded, return existing
    if data.source_message_id:
        existing = (
            db.query(Harvest)
            .options(joinedload(Harvest.crop), joinedload(Harvest.farmer).joinedload(Farmer.user))
            .filter(Harvest.source_message_id == data.source_message_id)
            .first()
        )
        if existing:
            logger.info(
                "Idempotent harvest return for source_message_id=%s", data.source_message_id
            )
            return existing

    # Resolve Crop
    crop = None
    if data.crop_id:
        crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    elif data.crop_name:
        crop = db.query(Crop).filter(Crop.name.ilike(f"{data.crop_name.strip()}%")).first()

    if not crop:
        if not data.crop_name:
            raise ValueError("Either crop_id or crop_name must be provided")
        # Auto-create basic crop entry if not exists
        crop = Crop(
            name=data.crop_name.strip().lower(),
            tamil_name=data.crop_name.strip(),
            unit="kg",
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    grade_enum = (
        data.grade
        if isinstance(data.grade, HarvestGrade)
        else HarvestGrade(str(data.grade).upper())
    )

    harvest = Harvest(
        farmer_id=farmer_id,
        crop_id=crop.id,
        quantity_kg=float(data.quantity_kg),
        grade=grade_enum,
        harvest_date=h_date,
        status=HarvestStatus.SUBMITTED,
        source_message_id=data.source_message_id,
        notes=data.notes,
    )
    db.add(harvest)
    db.commit()
    db.refresh(harvest)
    return harvest


def list_harvests(
    db: Session,
    fpo_id: Optional[UUID] = None,
    farmer_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    status: Optional[HarvestStatus | str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Harvest], int]:
    """Retrieve filtered, paginated list of harvests."""
    query = db.query(Harvest).options(
        joinedload(Harvest.crop),
        joinedload(Harvest.farmer).joinedload(Farmer.user),
    )

    if fpo_id:
        query = query.join(Farmer, Harvest.farmer_id == Farmer.id).filter(Farmer.fpo_id == fpo_id)
    if farmer_id:
        query = query.filter(Harvest.farmer_id == farmer_id)
    if crop_id:
        query = query.filter(Harvest.crop_id == crop_id)
    if status:
        stat_enum = (
            status if isinstance(status, HarvestStatus) else HarvestStatus(str(status).upper())
        )
        query = query.filter(Harvest.status == stat_enum)
    if start_date:
        query = query.filter(Harvest.harvest_date >= start_date)
    if end_date:
        query = query.filter(Harvest.harvest_date <= end_date)

    total = query.count()
    items = (
        query.order_by(desc(Harvest.harvest_date), desc(Harvest.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_harvest_by_id(db: Session, harvest_id: UUID) -> Optional[Harvest]:
    """Fetch single harvest with relations."""
    return (
        db.query(Harvest)
        .options(
            joinedload(Harvest.crop),
            joinedload(Harvest.farmer).joinedload(Farmer.user),
        )
        .filter(Harvest.id == harvest_id)
        .first()
    )


def update_harvest_status(
    db: Session,
    harvest_id: UUID,
    new_status: HarvestStatus | str,
    notes: Optional[str] = None,
) -> Harvest:
    """Validate and update harvest lifecycle state."""
    harvest = db.query(Harvest).filter(Harvest.id == harvest_id).first()
    if not harvest:
        raise ValueError(f"Harvest {harvest_id} not found")

    target_enum = (
        new_status
        if isinstance(new_status, HarvestStatus)
        else HarvestStatus(str(new_status).upper())
    )

    # Check allowed state transitions
    allowed = ALLOWED_TRANSITIONS.get(harvest.status, set())
    if target_enum not in allowed:
        raise ValueError(
            f"Invalid status transition from {harvest.status.value} to {target_enum.value}. Allowed: {[s.value for s in allowed]}"
        )

    harvest.status = target_enum
    if notes:
        harvest.notes = f"{harvest.notes}\n{notes}".strip() if harvest.notes else notes

    db.commit()
    db.refresh(harvest)
    return harvest
