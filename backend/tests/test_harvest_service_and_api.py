"""Unit and API tests for Harvest Service and REST API (T3.1)."""

import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user, get_db
from app.api.harvest import router as harvest_router
from app.models.base import Base
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest, HarvestGrade, HarvestStatus
from app.models.user import User, UserRole
from app.schemas.harvest import HarvestCreate
from app.services import harvest_service
from app.services.harvest_service import validate_harvest_parameters


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"


@compiles(PgUUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@pytest.fixture
def db_session():
    """In-memory SQLite database session fixture."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seed_data(db_session):
    """Seed base user, fpo, farmer, and crop."""
    fpo = FPO(
        name="Erode Turmeric Farmers Producer Co",
        registration_number=f"FPO-{uuid.uuid4().hex[:6]}",
        district="Erode",
        village="Modakkurichi",
        contact_phone="9876543210",
    )
    db_session.add(fpo)
    db_session.flush()

    farmer_user = User(
        name="Periyasamy",
        phone="9876543211",
        role=UserRole.FARMER,
        hashed_password="hash",
    )
    staff_user = User(
        name="Kavitha",
        phone="9876543212",
        role=UserRole.FPO_STAFF,
        hashed_password="hash",
    )
    db_session.add_all([farmer_user, staff_user])
    db_session.flush()

    farmer = Farmer(
        user_id=farmer_user.id,
        fpo_id=fpo.id,
        phone="9876543211",
        village="Modakkurichi",
        taluk="Erode",
        district="Erode",
        farm_area_acres=3.5,
    )
    crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg")
    db_session.add_all([farmer, crop])
    db_session.commit()
    return {
        "fpo": fpo,
        "farmer_user": farmer_user,
        "staff_user": staff_user,
        "farmer": farmer,
        "crop": crop,
    }


def test_validation_rules():
    """Verify bounds, quality grades, and harvest date window."""
    today = date.today()

    # Valid parameters pass without error
    validate_harvest_parameters(100.0, "A", today)
    validate_harvest_parameters(50000.0, HarvestGrade.B, today - timedelta(days=5))

    # Quantity out of bounds
    with pytest.raises(ValueError, match="Quantity must be between"):
        validate_harvest_parameters(0.5, "A", today)
    with pytest.raises(ValueError, match="Quantity must be between"):
        validate_harvest_parameters(50001.0, "A", today)

    # Invalid quality grade
    with pytest.raises(ValueError, match="Invalid harvest grade"):
        validate_harvest_parameters(100.0, "D", today)
    with pytest.raises(ValueError, match="Invalid harvest grade"):
        validate_harvest_parameters(100.0, "X", today)

    # Future date rejected
    with pytest.raises(ValueError, match="cannot be in the future"):
        validate_harvest_parameters(100.0, "A", today + timedelta(days=1))

    # Older than 14 days rejected
    with pytest.raises(ValueError, match="cannot be more than 14 days in the past"):
        validate_harvest_parameters(100.0, "A", today - timedelta(days=15))


def test_create_harvest_and_idempotency(db_session, seed_data):
    """Test harvest creation and idempotency via source_message_id."""
    farmer = seed_data["farmer"]
    crop = seed_data["crop"]

    data = HarvestCreate(
        farmer_id=farmer.id,
        crop_id=crop.id,
        quantity_kg=250.0,
        grade=HarvestGrade.A,
        harvest_date=date.today(),
        source_message_id="wa-msg-unique-123",
        notes="First batch of season",
    )

    h1 = harvest_service.create_harvest(db_session, data)
    assert h1.id is not None
    assert h1.status == HarvestStatus.SUBMITTED
    assert h1.quantity_kg == 250.0
    assert h1.source_message_id == "wa-msg-unique-123"

    # Second submission with exact same source_message_id returns existing record
    h2 = harvest_service.create_harvest(db_session, data)
    assert h2.id == h1.id
    assert db_session.query(Harvest).count() == 1


def test_status_transitions_lifecycle(db_session, seed_data):
    """Verify strict lifecycle: SUBMITTED -> VERIFIED -> AGGREGATED -> SOLD."""
    farmer = seed_data["farmer"]
    crop = seed_data["crop"]

    data = HarvestCreate(
        farmer_id=farmer.id,
        crop_id=crop.id,
        quantity_kg=500.0,
        grade=HarvestGrade.B,
    )
    harvest = harvest_service.create_harvest(db_session, data)
    assert harvest.status == HarvestStatus.SUBMITTED

    # SUBMITTED -> SOLD directly is invalid
    with pytest.raises(ValueError, match="Invalid status transition"):
        harvest_service.update_harvest_status(db_session, harvest.id, HarvestStatus.SOLD)

    # SUBMITTED -> VERIFIED is valid
    h_verified = harvest_service.update_harvest_status(
        db_session, harvest.id, HarvestStatus.VERIFIED, notes="Quality inspected"
    )
    assert h_verified.status == HarvestStatus.VERIFIED
    assert "Quality inspected" in h_verified.notes

    # VERIFIED -> AGGREGATED is valid
    h_agg = harvest_service.update_harvest_status(db_session, harvest.id, HarvestStatus.AGGREGATED)
    assert h_agg.status == HarvestStatus.AGGREGATED

    # AGGREGATED -> SOLD is valid (terminal)
    h_sold = harvest_service.update_harvest_status(db_session, harvest.id, HarvestStatus.SOLD)
    assert h_sold.status == HarvestStatus.SOLD

    # Terminal state SOLD cannot transition back
    with pytest.raises(ValueError, match="Invalid status transition"):
        harvest_service.update_harvest_status(db_session, harvest.id, HarvestStatus.VERIFIED)


def test_harvest_api_flow(db_session, seed_data):
    """Test REST API routes /api/harvest."""
    app = FastAPI()
    app.include_router(harvest_router)

    app.dependency_overrides[get_db] = lambda: db_session

    farmer_user = seed_data["farmer_user"]
    staff_user = seed_data["staff_user"]

    # 1. Farmer submits harvest
    app.dependency_overrides[get_current_user] = lambda: farmer_user
    client = TestClient(app)

    post_resp = client.post(
        "/api/harvest",
        json={
            "crop_name": "turmeric",
            "quantity_kg": 350.0,
            "grade": "A",
            "notes": "Organic harvest",
        },
    )
    assert post_resp.status_code == status.HTTP_201_CREATED
    data = post_resp.json()
    assert data["quantity_kg"] == 350.0
    assert data["crop_name"] == "turmeric"
    assert data["status"] == "SUBMITTED"
    harvest_id = data["id"]

    # 2. Farmer lists harvests (sees their own)
    list_resp = client.get("/api/harvest")
    assert list_resp.status_code == status.HTTP_200_OK
    assert list_resp.json()["total"] == 1

    # 3. Farmer attempts to verify status (forbidden)
    patch_resp = client.patch(
        f"/api/harvest/{harvest_id}/status",
        json={"status": "VERIFIED"},
    )
    assert patch_resp.status_code == status.HTTP_403_FORBIDDEN

    # 4. Staff verifies status (allowed)
    app.dependency_overrides[get_current_user] = lambda: staff_user
    staff_patch = client.patch(
        f"/api/harvest/{harvest_id}/status",
        json={"status": "VERIFIED", "notes": "Verified by coordinator"},
    )
    assert staff_patch.status_code == status.HTTP_200_OK
    assert staff_patch.json()["status"] == "VERIFIED"

    # 5. Get detail
    detail_resp = client.get(f"/api/harvest/{harvest_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == harvest_id
