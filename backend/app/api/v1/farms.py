"""Farm plots and discrete acreage API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role, verify_fpo_access
from app.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.farm import (
    FarmCreate,
    FarmListResponse,
    FarmResponse,
    FarmUpdate,
    FarmYieldEstimateResponse,
)
from app.services.csv_import import import_farms_csv
from app.services.farm_service import (
    create_farm,
    delete_farm,
    get_farm,
    list_farms,
    update_farm,
)
from app.services.yield_estimator import estimate_farm_yield

router = APIRouter(prefix="/farms", tags=["farms"])


def _farm_to_response(farm) -> FarmResponse:
    return FarmResponse(
        id=str(farm.id),
        farmer_id=str(farm.farmer_id),
        farmer_name=farm.farmer.user.name if (farm.farmer and farm.farmer.user) else None,
        farmer_phone=farm.farmer.user.phone if (farm.farmer and farm.farmer.user) else None,
        crop_id=str(farm.crop_id),
        crop_name=farm.crop.name if farm.crop else None,
        crop_tamil_name=farm.crop.tamil_name if farm.crop else None,
        plot_name=farm.plot_name,
        area_acres=farm.area_acres,
        village=farm.village,
        soil_type=farm.soil_type,
        irrigation_type=farm.irrigation_type,
        sowing_date=farm.sowing_date,
        expected_harvest_date=farm.expected_harvest_date,
        expected_yield_kg=farm.expected_yield_kg,
        actual_yield_kg=farm.actual_yield_kg,
        status=farm.status,
        district_id=str(farm.district_id) if farm.district_id else None,
        district_name=farm.district.name if farm.district else None,
        taluk_id=str(farm.taluk_id) if farm.taluk_id else None,
        taluk_name=farm.taluk.name if farm.taluk else None,
        created_at=farm.created_at,
        updated_at=farm.updated_at,
    )


@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "state_admin", "fpo_admin", "fpo_staff", "field_agent"])
    ),
):
    """Register a new discrete farm plot under a farmer."""
    farmer = db.query(Farmer).filter(Farmer.id == data.farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    if not verify_fpo_access(farmer.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to register plot for this FPO")

    try:
        farm = create_farm(db, data)
        # Reload with relationships
        full_farm = get_farm(db, farm.id)
        return _farm_to_response(full_farm or farm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=FarmListResponse)
def list_all(
    farmer_id: Optional[UUID] = None,
    fpo_id: Optional[UUID] = None,
    crop_id: Optional[UUID] = None,
    district: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List farm plots with filtering and total acreage."""
    # Scope to FPO if current user is FPO-restricted
    user_role = (
        current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    )
    if user_role in ("fpo_admin", "fpo_staff") and current_user.fpo_id:
        fpo_id = current_user.fpo_id

    skip = (page - 1) * page_size
    farms, total, total_acres = list_farms(
        db=db,
        farmer_id=farmer_id,
        fpo_id=fpo_id,
        crop_id=crop_id,
        district=district,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )

    return FarmListResponse(
        plots=[_farm_to_response(f) for f in farms],
        total=total,
        total_area_acres=total_acres,
    )


@router.get("/{farm_id}", response_model=FarmResponse)
def get_one(
    farm_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of a single farm plot."""
    farm = get_farm(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm plot not found")
    return _farm_to_response(farm)


@router.put("/{farm_id}", response_model=FarmResponse)
def update(
    farm_id: UUID,
    data: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(["admin", "state_admin", "fpo_admin", "fpo_staff", "field_agent"])
    ),
):
    """Update details of a farm plot."""
    farm = get_farm(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm plot not found")

    if not verify_fpo_access(farm.farmer.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to modify plot for this FPO")

    updated = update_farm(db, farm_id, data)
    full_farm = get_farm(db, farm_id)
    return _farm_to_response(full_farm or updated)


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    farm_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin"])),
):
    """Delete a farm plot."""
    farm = get_farm(db, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm plot not found")

    if not verify_fpo_access(farm.farmer.fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete plot for this FPO")

    delete_farm(db, farm_id)
    return None


@router.get("/{farm_id}/yield-estimate", response_model=FarmYieldEstimateResponse)
def get_yield_estimate(
    farm_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute on-demand rule-based agro-climatic yield estimate for a plot."""
    est = estimate_farm_yield(db, farm_id)
    if not est:
        raise HTTPException(status_code=404, detail="Farm plot not found or crop undefined")
    return FarmYieldEstimateResponse(**est)


@router.post("/import-csv")
def import_csv(
    fpo_id: UUID = Query(...),
    csv_text: str = Body(..., media_type="text/plain"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "fpo_admin", "fpo_staff"])),
):
    """Bulk import farm plots for an FPO via CSV text."""
    if not verify_fpo_access(fpo_id, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to import plots for this FPO")

    res = import_farms_csv(db, fpo_id, csv_text)
    return res
