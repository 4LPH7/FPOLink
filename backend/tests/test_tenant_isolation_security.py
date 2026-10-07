import re
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import jwt
import pytest

from app.config import Settings, settings
from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.geography import District, State
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.task import Task
from app.models.user import User, UserRole
from app.services.auth import hash_password
from app.services.jwt import create_access_token
from scripts.create_admin import create_or_update_admin


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
    assert (
        len(prices_v1) == 0
    ), "demo_seed price leaked into v1 public price feed with DEMO_MODE=False!"


def test_cors_origin_regex_security():
    """Verify CORS_ORIGIN_REGEX matches project Vercel previews but blocks attacker origins."""
    pattern = re.compile(settings.CORS_ORIGIN_REGEX)

    # Valid project domains
    assert pattern.match("https://fpolink.vercel.app") is not None
    assert pattern.match("https://fpo-link.vercel.app") is not None
    assert pattern.match("https://fpolink-preview-123.vercel.app") is not None
    assert pattern.match("https://fpo-link-preview-123.vercel.app") is not None
    assert pattern.match("https://fpolink-feat-branch.vercel.app") is not None
    assert pattern.match("https://fpo-link-feat-branch.vercel.app") is not None

    # Blocked / malicious domains
    assert pattern.match("https://attacker-app.vercel.app") is None
    assert pattern.match("https://evil-fpolink.vercel.app") is None
    assert pattern.match("https://random-app.vercel.app") is None
    assert pattern.match("http://fpolink.vercel.app") is None  # Insecure HTTP
    assert pattern.match("http://fpo-link.vercel.app") is None  # Insecure HTTP
    assert pattern.match("https://fpolink.vercel.app.attacker.com") is None
    assert pattern.match("https://fpo-link.vercel.app.attacker.com") is None


def test_district_admin_boundary_isolation(client, db):
    """District administrators can access FPOs/farmers in their district but are blocked outside."""
    state = State(name=f"TN-Sec-{uuid.uuid4().hex[:4]}", code=f"S{uuid.uuid4().hex[:2].upper()}")
    db.add(state)
    db.commit()

    district_erode = District(
        state_id=state.id, name=f"Erode-{uuid.uuid4().hex[:4]}", code=f"ER-{uuid.uuid4().hex[:3]}"
    )
    district_salem = District(
        state_id=state.id, name=f"Salem-{uuid.uuid4().hex[:4]}", code=f"SL-{uuid.uuid4().hex[:3]}"
    )
    db.add_all([district_erode, district_salem])
    db.commit()

    # FPO A in Erode
    fpo_erode = FPO(
        name=f"Erode FPO {uuid.uuid4().hex[:6]}",
        registration_number=f"REG-ER-{uuid.uuid4().hex[:6]}",
        district=district_erode.name,
        district_id=district_erode.id,
        village="Erode Central",
        contact_phone=f"91{uuid.uuid4().hex[:8]}",
    )
    # FPO B in Salem
    fpo_salem = FPO(
        name=f"Salem FPO {uuid.uuid4().hex[:6]}",
        registration_number=f"REG-SL-{uuid.uuid4().hex[:6]}",
        district=district_salem.name,
        district_id=district_salem.id,
        village="Salem Central",
        contact_phone=f"92{uuid.uuid4().hex[:8]}",
    )
    db.add_all([fpo_erode, fpo_salem])
    db.commit()

    # District Admin assigned to Erode
    dist_admin_erode = User(
        name="Erode District Director",
        phone=f"93{uuid.uuid4().hex[:8]}",
        role=UserRole.DISTRICT_ADMIN,
        district_id=district_erode.id,
        hashed_password=hash_password("Pass@1234"),
        is_active=True,
    )
    db.add(dist_admin_erode)
    db.commit()

    token_erode_admin = create_access_token(dist_admin_erode.id, dist_admin_erode.role.value)
    headers = {"Authorization": f"Bearer {token_erode_admin}"}

    # 1. District Admin Erode accessing FPO A (in Erode) -> 200 OK
    res_a = client.get(f"/api/fpos/{fpo_erode.id}", headers=headers)
    assert res_a.status_code == 200

    # 2. District Admin Erode accessing FPO B (in Salem) -> 403 Forbidden
    res_b = client.get(f"/api/fpos/{fpo_salem.id}", headers=headers)
    assert res_b.status_code == 403
    assert "not authorized" in res_b.json()["detail"].lower()

    # 3. v1 endpoint: GET /api/v1/fpos/{fpo_salem.id} -> 403 Forbidden
    res_v1_b = client.get(f"/api/v1/fpos/{fpo_salem.id}", headers=headers)
    assert res_v1_b.status_code == 403

    # 4. District Admin listing farmers for FPO A (in Erode) -> 200 OK
    res_farm_a = client.get(f"/api/farmers/{fpo_erode.id}", headers=headers)
    assert res_farm_a.status_code == 200

    # 5. District Admin listing farmers for FPO B (in Salem) -> 403 Forbidden
    res_farm_b = client.get(f"/api/farmers/{fpo_salem.id}", headers=headers)
    assert res_farm_b.status_code == 403


def test_cross_tenant_bulk_csv_import_blocked(client, db):
    """FPO staff cannot import buyers or requirements for another FPO."""
    fpo_a = _create_test_fpo(db, "AlphaImport")
    fpo_b = _create_test_fpo(db, "BetaImport")

    _, token_a = _create_test_user(db, fpo_a, UserRole.FPO_STAFF)
    headers_a = {"Authorization": f"Bearer {token_a}"}

    csv_data = "Company,Contact,Phone,Location,District,Crop,Qty\nBuyer1,John,9876543210,Erode,Erode,turmeric,500\n"

    # Staff A attempts to bulk import for FPO B
    res = client.post(
        f"/api/v1/buyers/import-csv?fpo_id={fpo_b.id}",
        content=csv_data,
        headers={**headers_a, "Content-Type": "text/plain"},
    )
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_cross_tenant_matching_candidates_blocked(client, db):
    """Staff cannot inspect candidate matches for a buyer requirement belonging to another FPO."""
    fpo_a = _create_test_fpo(db, "MatchAlpha")
    fpo_b = _create_test_fpo(db, "MatchBeta")

    _, token_a = _create_test_user(db, fpo_a, UserRole.FPO_STAFF)
    user_b, _ = _create_test_user(db, fpo_b, UserRole.FPO_STAFF)

    crop = Crop(
        name=f"MatchCrop-{uuid.uuid4().hex[:4]}",
        canonical_name=f"mcrop-{uuid.uuid4().hex[:4]}",
        tamil_name="பயிர்",
    )
    buyer = Buyer(
        company_name=f"Buyer B {uuid.uuid4().hex[:4]}",
        fpo_id=fpo_b.id,
        contact_phone="9988776655",
        location="Erode Central",
        district="Erode",
    )
    db.add_all([crop, buyer])
    db.commit()

    req_b = BuyerRequirement(
        buyer_id=buyer.id,
        fpo_id=fpo_b.id,
        crop_id=crop.id,
        quantity_kg=1000.0,
        min_grade="A",
        required_date=date.today(),
        created_by_user_id=user_b.id,
    )
    db.add(req_b)
    db.commit()

    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Staff A attempts to inspect matching candidates for requirement of FPO B
    res = client.get(f"/api/v1/matching/candidates/{req_b.id}", headers=headers_a)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_wildcard_cors_rejected_in_production():
    """Verify that wildcard '*' CORS origin is strictly forbidden in production."""
    with pytest.raises(ValueError, match="wildcard CORS origin"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="A" * 32,
            DATABASE_URL="postgresql+psycopg://user:verysecurepassword12345@localhost/db",
            DEMO_MODE=False,
            CORS_ORIGINS="*",
        ).validate_production_secrets()


def test_production_bootstrap_password_hardening(monkeypatch):
    """create_admin script enforces complexity in production and defaults must_change=True."""
    monkeypatch.setenv("ENVIRONMENT", "production")

    # 1. Less than 12 chars in production
    with pytest.raises(ValueError, match="at least 12 characters"):
        create_or_update_admin(phone="8072845239", password="ShortPass@1")

    # 2. Common default password rejected in production
    with pytest.raises(ValueError, match="cannot be a common default"):
        create_or_update_admin(phone="8072845239", password="password123456")

    # 3. Valid strong password passes
    user = create_or_update_admin(
        phone="8072845239",
        password="SuperStrongProductionPassword#2026",
        must_change_password=True,
    )
    assert user.password_change_required is True
