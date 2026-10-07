"""Automated tests for tenant isolation, authorization boundaries, and production security."""

import re
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import jwt

from app.config import settings
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.task import Task
from app.models.user import User, UserRole
from app.services.auth import hash_password
from app.services.jwt import create_access_token


def _create_test_fpo(db, name_prefix: str) -> FPO:
    fpo = FPO(
        name=f"{name_prefix} FPO {uuid.uuid4().hex[:6]}",
        registration_number=f"REG-{uuid.uuid4().hex[:8]}",
        district="Erode",
        village="Erode",
        contact_phone=f"91{uuid.uuid4().hex[:8]}",
    )
    db.add(fpo)
    db.commit()
    db.refresh(fpo)
    return fpo


def _create_test_user(db, fpo: FPO, role: UserRole) -> tuple[User, str]:
    phone = f"91{uuid.uuid4().hex[:8]}"
    user = User(
        name=f"Staff {fpo.name[:10]}",
        phone=phone,
        role=role,
        fpo_id=fpo.id,
        hashed_password=hash_password("Pass@1234"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role.value)
    return user, token


def test_cross_fpo_farmer_access_blocked(client, db):
    """An FPO user attempting to read or modify another FPO's records must be blocked."""
    fpo_a = _create_test_fpo(db, "Alpha")
    fpo_b = _create_test_fpo(db, "Beta")

    user_a, token_a = _create_test_user(db, fpo_a, UserRole.FPO_STAFF)
    user_b, token_b = _create_test_user(db, fpo_b, UserRole.FPO_STAFF)

    # Register farmer under FPO B
    farmer_b_phone = f"98{uuid.uuid4().hex[:8]}"
    user_fb = User(
        name="Farmer B",
        phone=farmer_b_phone,
        role=UserRole.FARMER,
        fpo_id=fpo_b.id,
        hashed_password=hash_password("Farmer@123"),
        is_active=True,
    )
    db.add(user_fb)
    db.commit()
    farmer_b = Farmer(
        user_id=user_fb.id,
        fpo_id=fpo_b.id,
        village="B Village",
        taluk="B Taluk",
        district="Erode",
        farm_area_acres=Decimal("2.5"),
        phone=farmer_b_phone,
    )
    db.add(farmer_b)
    db.commit()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 1. Staff A attempts to list farmers for FPO B -> 403 Forbidden
    res = client.get(f"/api/farmers/{fpo_b.id}", headers=headers_a)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()

    # 2. Staff A attempts to get farmer B details -> 403 Forbidden
    res = client.get(f"/api/farmers/detail/{farmer_b.id}", headers=headers_a)
    assert res.status_code == 403

    # 3. Staff A attempts to register farmer under FPO B -> 403 Forbidden
    new_farmer_payload = {
        "name": "Intruder Farmer",
        "phone": f"97{uuid.uuid4().hex[:8]}",
        "password": "FarmerPassword@123",
        "village": "Ghost Village",
        "taluk": "Ghost Taluk",
        "district": "Erode",
        "farm_area_acres": 2.5,
    }
    res = client.post(f"/api/farmers/{fpo_b.id}", json=new_farmer_payload, headers=headers_a)
    assert res.status_code == 403


def test_cross_fpo_task_isolation_and_modification_blocked(client, db):
    """An FPO staff user cannot view, update, or delete tasks belonging to another FPO."""
    fpo_a = _create_test_fpo(db, "Alpha")
    fpo_b = _create_test_fpo(db, "Beta")

    user_a, token_a = _create_test_user(db, fpo_a, UserRole.FPO_STAFF)
    user_b, token_b = _create_test_user(db, fpo_b, UserRole.FPO_STAFF)

    # Create task belonging to FPO B
    task_b = Task(
        fpo_id=fpo_b.id,
        title="Beta Task",
        status="todo",
        priority="high",
        created_by_id=user_b.id,
    )
    db.add(task_b)
    db.commit()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 1. Listing tasks as Staff A must NOT include Task B
    res = client.get("/api/tasks", headers=headers_a)
    assert res.status_code == 200
    task_ids = [t["id"] for t in res.json()]
    assert str(task_b.id) not in task_ids

    # 2. Staff A attempts to update Task B -> 404 (scoped query hides it)
    res = client.patch(
        f"/api/tasks/{task_b.id}",
        json={"title": "Hacked Title"},
        headers=headers_a,
    )
    assert res.status_code == 404

    # 3. Staff A attempts to delete Task B -> 404
    res = client.delete(f"/api/tasks/{task_b.id}", headers=headers_a)
    assert res.status_code == 404


def test_expired_and_invalid_tokens_rejected(client):
    """Authentication rejects expired, corrupted, or signature-mismatched tokens."""
    # 1. Expired token
    expired_payload = {
        "sub": str(uuid.uuid4()),
        "role": "admin",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10),
    }
    expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm="HS256")
    res = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == 401
    assert "invalid or expired token" in res.json()["detail"].lower()

    # 2. Tampered / invalid signature token
    tampered_token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "admin", "type": "access"},
        "wrong-secret-key-signature",
        algorithm="HS256",
    )
    res = client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert res.status_code == 401

    # 3. Missing authorization header
    res = client.get("/api/tasks")
    assert res.status_code == 401


def test_password_rotation_workflow_enforced(client, db):
    """Users with password_change_required cannot access protected APIs until password is changed."""
    phone = f"99{uuid.uuid4().hex[:8]}"
    user = User(
        name="Rotation Required Admin",
        phone=phone,
        role=UserRole.ADMIN,
        hashed_password=hash_password("OldPassword@123"),
        password_change_required=True,
        is_active=True,
    )
    db.add(user)
    db.commit()

    # 1. Login with temporary password
    login_res = client.post("/api/auth/login", json={"phone": phone, "password": "OldPassword@123"})
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["password_change_required"] is True
    temp_token = data["access_token"]

    # 2. Protected endpoint MUST reject this restricted password-change token
    headers_temp = {"Authorization": f"Bearer {temp_token}"}
    prot_res = client.get("/api/fpos/", headers=headers_temp)
    # Token type is 'password_change', not 'access'
    assert prot_res.status_code in (401, 403)

    # 3. Rotate password using change-password endpoint
    rotate_res = client.post(
        "/api/auth/change-password",
        json={"current_password": "OldPassword@123", "new_password": "NewStrongPassword@2026"},
        headers=headers_temp,
    )
    assert rotate_res.status_code == 200
    new_tokens = rotate_res.json()
    assert new_tokens.get("password_change_required", False) is False
    new_access_token = new_tokens["access_token"]

    # 4. Now protected endpoint succeeds with the rotated credential access token
    headers_new = {"Authorization": f"Bearer {new_access_token}"}
    prot_success = client.get("/api/fpos/", headers=headers_new)
    assert prot_success.status_code == 200


def test_demo_data_isolation_when_demo_mode_false(client, db, monkeypatch):
    """demo_seed records must NEVER leak to prices API when DEMO_MODE=False."""
    monkeypatch.setattr(settings, "DEMO_MODE", False)

    crop = Crop(
        name=f"IsoCrop-{uuid.uuid4().hex[:4]}",
        canonical_name=f"isocrop-{uuid.uuid4().hex[:4]}",
        tamil_name="பயிர்",
    )
    market = Market(name=f"IsoMarket-{uuid.uuid4().hex[:4]}", district="Erode", state="Tamil Nadu")
    db.add_all([crop, market])
    db.commit()

    demo_price = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Erode",
        min_price=Decimal("40.00"),
        max_price=Decimal("50.00"),
        modal_price=Decimal("45.00"),
        price_date=date.today(),
        source="demo_seed",
    )
    db.add(demo_price)
    db.commit()

    # Query latest prices with DEMO_MODE=False
    res = client.get("/api/prices/latest?district=Erode")
    assert res.status_code == 200
    prices = res.json()["prices"]
    matching = [p for p in prices if p["crop_name"] == crop.name]
    assert len(matching) == 0, "demo_seed price leaked into public price feed with DEMO_MODE=False!"

    # Query v1 latest prices
    res_v1 = client.get(f"/api/v1/prices/latest?crop_id={crop.id}")
    assert res_v1.status_code == 200
    prices_v1 = res_v1.json()["prices"]
    assert len(prices_v1) == 0, (
        "demo_seed price leaked into v1 public price feed with DEMO_MODE=False!"
    )


def test_cors_origin_regex_security():
    """Verify CORS_ORIGIN_REGEX matches project Vercel previews but blocks attacker origins."""
    pattern = re.compile(settings.CORS_ORIGIN_REGEX)

    # Valid project domains
    assert pattern.match("https://fpolink.vercel.app") is not None
    assert pattern.match("https://fpolink-preview-123.vercel.app") is not None
    assert pattern.match("https://fpolink-feat-branch.vercel.app") is not None

    # Blocked / malicious domains
    assert pattern.match("https://attacker-app.vercel.app") is None
    assert pattern.match("https://evil-fpolink.vercel.app") is None
    assert pattern.match("https://random-app.vercel.app") is None
    assert pattern.match("http://fpolink.vercel.app") is None  # Insecure HTTP
    assert pattern.match("https://fpolink.vercel.app.attacker.com") is None
