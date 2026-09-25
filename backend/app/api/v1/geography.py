"""Geography endpoints — states, districts, taluks, villages."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.geography import District, State, Taluk, Village
from app.models.user import User
from app.schemas.geography import (
    DistrictCreate,
    DistrictResponse,
    StateCreate,
    StateResponse,
    TalukCreate,
    TalukResponse,
    VillageCreate,
    VillageResponse,
)

router = APIRouter(prefix="/geography", tags=["geography"])


@router.get("/states", response_model=List[StateResponse])
def list_states(db: Session = Depends(get_db)):
    """List all states."""
    states = db.query(State).order_by(State.name).all()
    result = []
    for s in states:
        item = StateResponse.model_validate(s)
        item.districts_count = len(s.districts)
        result.append(item)
    return result


@router.post("/states", response_model=StateResponse, status_code=status.HTTP_201_CREATED)
def create_state(
    data: StateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Register a new state (admin only)."""
    existing = db.query(State).filter((State.name == data.name) | (State.code == data.code)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="State with this name or code already exists",
        )
    state = State(name=data.name, code=data.code.upper())
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


@router.get("/districts", response_model=List[DistrictResponse])
def list_districts(
    state_code: Optional[str] = Query(default=None, description="Filter by state code, e.g. TN"),
    db: Session = Depends(get_db),
):
    """List districts, optionally filtered by state."""
    query = db.query(District).join(State)
    if state_code:
        query = query.filter(State.code == state_code.upper())
    districts = query.order_by(District.name).all()
    result = []
    for d in districts:
        item = DistrictResponse.model_validate(d)
        item.taluks_count = len(d.taluks)
        result.append(item)
    return result


@router.get("/districts/{district_id}", response_model=DistrictResponse)
def get_district(district_id: UUID, db: Session = Depends(get_db)):
    """Get single district by ID."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")
    item = DistrictResponse.model_validate(district)
    item.taluks_count = len(district.taluks)
    return item


@router.post("/districts", response_model=DistrictResponse, status_code=status.HTTP_201_CREATED)
def create_district(
    data: DistrictCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Register a new district (admin only)."""
    state = db.query(State).filter(State.id == data.state_id).first()
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
    existing = db.query(District).filter(District.code == data.code.upper()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="District code already registered"
        )
    district = District(
        state_id=data.state_id,
        name=data.name,
        code=data.code.upper(),
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(district)
    db.commit()
    db.refresh(district)
    return district


@router.get("/districts/{district_id}/taluks", response_model=List[TalukResponse])
def list_taluks_for_district(district_id: UUID, db: Session = Depends(get_db)):
    """List all taluks under a district."""
    taluks = db.query(Taluk).filter(Taluk.district_id == district_id).order_by(Taluk.name).all()
    result = []
    for t in taluks:
        item = TalukResponse.model_validate(t)
        item.villages_count = len(t.villages)
        result.append(item)
    return result


@router.post("/taluks", response_model=TalukResponse, status_code=status.HTTP_201_CREATED)
def create_taluk(
    data: TalukCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Register a new taluk under a district (admin only)."""
    district = db.query(District).filter(District.id == data.district_id).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")
    taluk = Taluk(district_id=data.district_id, name=data.name)
    db.add(taluk)
    db.commit()
    db.refresh(taluk)
    return taluk


@router.get("/taluks/{taluk_id}/villages", response_model=List[VillageResponse])
def list_villages_for_taluk(taluk_id: UUID, db: Session = Depends(get_db)):
    """List all villages under a taluk."""
    return db.query(Village).filter(Village.taluk_id == taluk_id).order_by(Village.name).all()


@router.post("/villages", response_model=VillageResponse, status_code=status.HTTP_201_CREATED)
def create_village(
    data: VillageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """Register a new village under a taluk."""
    taluk = db.query(Taluk).filter(Taluk.id == data.taluk_id).first()
    if not taluk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Taluk not found")
    village = Village(taluk_id=data.taluk_id, block_id=data.block_id, name=data.name)
    db.add(village)
    db.commit()
    db.refresh(village)
    return village
