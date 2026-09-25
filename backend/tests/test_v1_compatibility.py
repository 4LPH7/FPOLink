"""Tests for v1 API routing and legacy backward compatibility."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.models.crop import Crop
from app.models.fpo import FPO
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.user import User, UserRole
from app.services.jwt import create_access_token

client = TestClient(app)


def _get_admin_headers(db):
    admin_user = db.query(User).filter(User.phone == "+919999900001").first()
    if not admin_user:
        admin_user = User(
            name="System Admin",
            phone="+919999900001",
            hashed_password="hash",
            role=UserRole.ADMIN,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    token = create_access_token(admin_user.id, "admin")
    return {"Authorization": f"Bearer {token}"}


def test_fpos_compatibility(db):
    """Verify /api/fpos/ and /api/v1/fpos/ return compatible responses."""
    # Ensure test FPO exists
    fpo = db.query(FPO).filter(FPO.registration_number == "COMPAT_FPO_001").first()
    if not fpo:
        fpo = FPO(
            name="Compatibility Test FPO",
            registration_number="COMPAT_FPO_001",
            district="Erode",
            village="Kodumudi",
            contact_phone="+919444455555",
        )
        db.add(fpo)
        db.commit()
        db.refresh(fpo)

    res_legacy = client.get("/api/fpos/")
    res_v1 = client.get("/api/v1/fpos/")

    assert res_legacy.status_code == 200
    assert res_v1.status_code == 200

    legacy_fpos = res_legacy.json()["fpos"]
    v1_fpos = res_v1.json()["fpos"]

    assert len(legacy_fpos) == len(v1_fpos)
    legacy_ids = {f["id"] for f in legacy_fpos}
    v1_ids = {f["id"] for f in v1_fpos}
    assert str(fpo.id) in legacy_ids
    assert str(fpo.id) in v1_ids


def test_farmers_compatibility(db):
    """Verify /api/farmers/{fpo_id} and /api/v1/farmers/{fpo_id} work equivalently."""
    fpo = db.query(FPO).filter(FPO.registration_number == "COMPAT_FPO_001").first()
    if not fpo:
        fpo = FPO(
            name="Compatibility Test FPO",
            registration_number="COMPAT_FPO_001",
            district="Erode",
            village="Kodumudi",
            contact_phone="+919444455555",
        )
        db.add(fpo)
        db.commit()
        db.refresh(fpo)

    headers = _get_admin_headers(db)

    res_legacy = client.get(f"/api/farmers/{fpo.id}", headers=headers)
    res_v1 = client.get(f"/api/v1/farmers/{fpo.id}", headers=headers)

    assert res_legacy.status_code == 200
    assert res_v1.status_code == 200
    assert res_legacy.json()["total"] == res_v1.json()["total"]


def test_prices_compatibility(db):
    """Verify /api/prices/latest and /api/v1/prices/latest both serve verified prices."""
    crop = db.query(Crop).filter(Crop.name == "turmeric").first()
    if not crop:
        crop = Crop(name="turmeric", canonical_name="turmeric", unit="kg", is_active=True)
        db.add(crop)
        db.commit()
        db.refresh(crop)

    market = db.query(Market).filter(Market.name == "Erode Mandi").first()
    if not market:
        market = Market(name="Erode Mandi", district="Erode", is_active=True)
        db.add(market)
        db.commit()
        db.refresh(market)

    today = date.today()
    mp = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Erode",
        min_price=Decimal("120.00"),
        max_price=Decimal("140.00"),
        modal_price=Decimal("130.00"),
        price_date=today,
        source="ogd",
    )
    db.add(mp)
    db.commit()

    res_legacy = client.get("/api/prices/latest?district=Erode")
    res_v1 = client.get("/api/v1/prices/latest?district=Erode")

    assert res_legacy.status_code == 200
    assert res_v1.status_code == 200

    legacy_prices = res_legacy.json()["prices"]
    v1_prices = res_v1.json()["prices"]

    assert len(legacy_prices) >= 1
    assert len(v1_prices) >= 1
    assert legacy_prices[0]["crop_name"] == v1_prices[0]["crop_name"]
    assert legacy_prices[0]["modal_price"] == v1_prices[0]["modal_price"]
