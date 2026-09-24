"""Tests for multi-tenant RBAC, organization scoping, and audit logging."""

import uuid
import pytest
from app.api.deps import verify_fpo_access
from app.models.audit_log import AuditLog
from app.models.fpo import FPO
from app.models.geography import District, State
from app.models.user import User, UserRole
from app.services.audit import log_audit_event
from app.services.auth import hash_password


def test_multitenant_user_roles(db):
    """Test creating users with new multi-tenant roles."""
    state = State(name=f"TN-RBAC-{uuid.uuid4().hex[:4]}", code=f"R{uuid.uuid4().hex[:2].upper()}")
    db.add(state)
    db.commit()

    district = District(state_id=state.id, name="Erode", code=f"RBAC-D-{uuid.uuid4().hex[:4]}")
    db.add(district)
    db.commit()

    fpo = FPO(
        name="RBAC FPO Test",
        registration_number=f"REG-RBAC-{uuid.uuid4().hex[:6]}",
        district="Erode",
        village="Erode",
        contact_phone="9988771122",
        district_id=district.id,
    )
    db.add(fpo)
    db.commit()

    # 1. State Admin
    state_admin = User(
        name="State Director",
        phone=f"91{uuid.uuid4().hex[:8]}",
        role=UserRole.STATE_ADMIN,
        hashed_password=hash_password("admin123"),
    )
    # 2. District Admin
    district_admin = User(
        name="Joint Director Agri",
        phone=f"92{uuid.uuid4().hex[:8]}",
        role=UserRole.DISTRICT_ADMIN,
        district_id=district.id,
        hashed_password=hash_password("admin123"),
    )
    # 3. FPO Admin
    fpo_admin = User(
        name="FPO CEO",
        phone=f"93{uuid.uuid4().hex[:8]}",
        role=UserRole.FPO_ADMIN,
        fpo_id=fpo.id,
        hashed_password=hash_password("admin123"),
    )
    db.add_all([state_admin, district_admin, fpo_admin])
    db.commit()

    assert state_admin.role == UserRole.STATE_ADMIN
    assert district_admin.district_id == district.id
    assert fpo_admin.fpo_id == fpo.id


def test_tenant_scoping_access_boundaries(db):
    """Verify tenant isolation between different FPOs."""
    fpo1_id = uuid.uuid4()
    fpo2_id = uuid.uuid4()

    state_admin = User(name="State Admin", phone="9000000001", role=UserRole.STATE_ADMIN, hashed_password="x")
    fpo1_staff = User(name="Staff 1", phone="9000000002", role=UserRole.FPO_STAFF, fpo_id=fpo1_id, hashed_password="x")
    fpo2_staff = User(name="Staff 2", phone="9000000003", role=UserRole.FPO_STAFF, fpo_id=fpo2_id, hashed_password="x")

    # State admin can access both
    assert verify_fpo_access(fpo1_id, state_admin) is True
    assert verify_fpo_access(fpo2_id, state_admin) is True

    # FPO1 staff can only access FPO1
    assert verify_fpo_access(fpo1_id, fpo1_staff) is True
    assert verify_fpo_access(fpo2_id, fpo1_staff) is False

    # FPO2 staff can only access FPO2
    assert verify_fpo_access(fpo1_id, fpo2_staff) is False
    assert verify_fpo_access(fpo2_id, fpo2_staff) is True


def test_audit_logging_and_api(client, db):
    """Test recording an audit log event and querying via API."""
    user = User(name="Auditor", phone=f"94{uuid.uuid4().hex[:8]}", role=UserRole.ADMIN, hashed_password=hash_password("admin123"))
    db.add(user)
    db.commit()

    # Log an operational audit event
    entry = log_audit_event(
        db=db,
        user_id=user.id,
        action="UPDATE_PRICE",
        target_type="market_price",
        target_id="mp-12345",
        before_state={"modal_price": 145.0},
        after_state={"modal_price": 155.0},
        ip_address="127.0.0.1",
    )

    assert entry.id is not None
    assert entry.action == "UPDATE_PRICE"
    assert entry.before_state["modal_price"] == 145.0

    # Query via API
    from app.services.jwt import create_access_token
    token = create_access_token(user_id=str(user.id), role="admin")

    r = client.get(
        "/api/v1/audit/logs?target_type=market_price",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any(log["action"] == "UPDATE_PRICE" for log in data["logs"])
