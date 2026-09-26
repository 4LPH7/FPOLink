"""Integration tests for Wave 3: REST API v1 endpoints and WhatsApp Bot Inbound Buyers intent."""

import contextlib
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.messaging.base import Button, InboundMessage
from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.geography import District, State
from app.models.harvest import HarvestGrade
from app.models.supply_match import SupplyMatch
from app.models.user import User, UserRole
from app.services.auth import hash_password
from app.services.bot import BotEngine
from app.services.db_bot_services import DbBotServices
from app.services.jwt import create_access_token


class MockChannel:
    """Mock WhatsApp channel capturing outgoing messages."""

    def __init__(self):
        self.sent_messages = []

    async def send_text(self, to: str, body: str) -> bool:
        self.sent_messages.append({"to": to, "text": body})
        return True

    async def send_buttons(self, to: str, body: str, buttons: list[Button]) -> bool:
        self.sent_messages.append({"to": to, "text": body, "buttons": buttons})
        return True

    async def send_template(self, to: str, name: str, lang: str, params: list[str]) -> bool:
        self.sent_messages.append({"to": to, "template": name, "params": params})
        return True


@pytest.fixture
def auth_context(db):
    """Create test State, District, FPO, Admin, FPO Staff, and Farmer."""
    suffix = uuid.uuid4().hex[:6]
    state = State(name=f"TN-SD-{suffix}", code=f"S{suffix[:2].upper()}")
    db.add(state)
    db.commit()

    district = District(state_id=state.id, name=f"Erode-{suffix}", code=f"ERD-{suffix[:4]}")
    db.add(district)
    db.commit()

    import random

    rand_digits = f"{random.randint(10000000, 99999999)}"

    fpo = FPO(
        name=f"Erode Collective {suffix}",
        registration_number=f"REG-SD-{suffix}",
        district=district.name,
        village="Perundurai",
        contact_phone=f"98{rand_digits}",
        district_id=district.id,
    )
    db.add(fpo)
    db.commit()

    # Admin User
    admin = User(
        name="SD Admin",
        phone=f"90{rand_digits}",
        role=UserRole.ADMIN,
        hashed_password=hash_password("admin123"),
        is_active=True,
    )
    # FPO Staff User
    staff = User(
        name="SD Staff",
        phone=f"91{rand_digits}",
        role=UserRole.FPO_STAFF,
        fpo_id=fpo.id,
        hashed_password=hash_password("staff123"),
        is_active=True,
    )
    # Farmer User
    farmer_user = User(
        name="SD Farmer",
        phone=f"92{rand_digits}",
        role=UserRole.FARMER,
        fpo_id=fpo.id,
        hashed_password=hash_password("farmer123"),
        is_active=True,
        language_preference="ta",
    )
    db.add_all([admin, staff, farmer_user])
    db.commit()

    farmer = Farmer(
        user_id=farmer_user.id,
        fpo_id=fpo.id,
        phone=farmer_user.phone,
        village="Perundurai",
        taluk="Perundurai",
        district=district.name,
        district_id=district.id,
        farm_area_acres=6.0,
        lang="ta",
        notice_sent_at=datetime.now(timezone.utc),
    )
    db.add(farmer)

    # Turmeric crop
    crop = db.query(Crop).filter(Crop.name == "turmeric").first()
    if not crop:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg", category="spice")
        db.add(crop)
    db.commit()

    admin_token = create_access_token(admin.id, role="admin")
    staff_token = create_access_token(staff.id, role="fpo_staff")
    farmer_token = create_access_token(farmer_user.id, role="farmer")

    return {
        "admin": admin,
        "staff": staff,
        "farmer_user": farmer_user,
        "farmer": farmer,
        "fpo": fpo,
        "district": district,
        "crop": crop,
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "staff_headers": {"Authorization": f"Bearer {staff_token}"},
        "farmer_headers": {"Authorization": f"Bearer {farmer_token}"},
    }


# ---------------------------------------------------------------------------
# 1. Farms API Tests
# ---------------------------------------------------------------------------


def test_farms_api_crud_and_yield(client, auth_context):
    headers = auth_context["staff_headers"]
    farmer_id = str(auth_context["farmer"].id)
    crop_id = str(auth_context["crop"].id)

    # 1. Create a plot
    create_payload = {
        "farmer_id": farmer_id,
        "crop_id": crop_id,
        "plot_name": "East Well Plot",
        "area_acres": 2.5,
        "village": "Perundurai",
        "soil_type": "red loam",
        "irrigation_type": "drip",
        "sowing_date": str(date.today() - timedelta(days=90)),
        "status": "growing",
    }
    res = client.post("/api/v1/farms/", json=create_payload, headers=headers)
    assert res.status_code == 201
    plot = res.json()
    farm_id = plot["id"]
    assert plot["plot_name"] == "East Well Plot"
    assert plot["area_acres"] == 2.5
    assert plot["expected_yield_kg"] > 0

    # 2. Get plot details
    res = client.get(f"/api/v1/farms/{farm_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == farm_id
    assert res.json()["crop_name"] == "turmeric"

    # 3. List plots with filters
    res = client.get(f"/api/v1/farms/?farmer_id={farmer_id}", headers=headers)
    assert res.status_code == 200
    list_data = res.json()
    assert list_data["total"] >= 1
    assert list_data["total_area_acres"] >= 2.5

    # 4. On-demand yield estimate endpoint
    res = client.get(f"/api/v1/farms/{farm_id}/yield-estimate", headers=headers)
    assert res.status_code == 200
    est = res.json()
    assert est["crop_name"] == "turmeric"
    assert est["estimated_yield_kg"] > 0

    # 5. Update plot
    update_payload = {"area_acres": 3.0, "status": "ready_for_harvest"}
    res = client.put(f"/api/v1/farms/{farm_id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["area_acres"] == 3.0
    assert res.json()["status"] == "ready_for_harvest"

    # 6. Delete plot (requires admin)
    res = client.delete(f"/api/v1/farms/{farm_id}", headers=auth_context["admin_headers"])
    assert res.status_code == 204

    # 7. Verify deletion
    res = client.get(f"/api/v1/farms/{farm_id}", headers=headers)
    assert res.status_code == 404


def test_farms_csv_import(client, auth_context):
    headers = auth_context["staff_headers"]
    fpo_id = str(auth_context["fpo"].id)
    farmer_phone = auth_context["farmer_user"].phone

    csv_data = (
        "farmer_phone,crop,plot_name,area_acres,village,soil_type,irrigation_type\n"
        f"{farmer_phone},turmeric,CSV Plot 1,2.0,Perundurai,red loam,drip\n"
        f"{farmer_phone},turmeric,CSV Plot 2,1.5,Perundurai,alluvial,canal\n"
    )

    res = client.post(
        f"/api/v1/farms/import-csv?fpo_id={fpo_id}",
        content=csv_data,
        headers={**headers, "Content-Type": "text/plain"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["imported"] == 2
    assert data["errors_count"] == 0


# ---------------------------------------------------------------------------
# 2. Buyers & Requirements API Tests
# ---------------------------------------------------------------------------


def test_buyers_and_requirements_api(client, auth_context):
    headers = auth_context["staff_headers"]
    fpo_id = str(auth_context["fpo"].id)
    crop_id = str(auth_context["crop"].id)

    # 1. Create commercial buyer
    buyer_payload = {
        "company_name": f"Spices Export Corp {uuid.uuid4().hex[:4]}",
        "buyer_type": "exporter",
        "contact_name": "Ravi Shankar",
        "contact_phone": "9842011122",
        "contact_email": "ravi@spicesexport.example.com",
        "location": "Perundurai SIPCOT",
        "district": auth_context["district"].name,
        "fpo_id": fpo_id,
        "gstin": "33AAACE1234F1Z5",
        "verified": True,
    }
    res = client.post("/api/v1/buyers/", json=buyer_payload, headers=headers)
    assert res.status_code == 201
    buyer = res.json()
    buyer_id = buyer["id"]
    assert buyer["company_name"] == buyer_payload["company_name"]

    # 2. List buyers
    res = client.get("/api/v1/buyers/", headers=headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1

    # 3. Post requirement
    req_payload = {
        "buyer_id": buyer_id,
        "fpo_id": fpo_id,
        "crop_id": crop_id,
        "quantity_kg": 4000.0,
        "min_grade": "A",
        "required_date": str(date.today() + timedelta(days=20)),
        "delivery_window_days": 7,
        "max_price_per_kg": 150.00,
        "delivery_location": "SIPCOT Warehouse 4",
        "notes": "Premium clean fingers",
    }
    res = client.post("/api/v1/buyers/requirements", json=req_payload, headers=headers)
    assert res.status_code == 201
    req = res.json()
    req_id = req["id"]
    assert req["quantity_kg"] == 4000.0
    assert req["status"] == "open"

    # 4. List requirements
    res = client.get(f"/api/v1/buyers/requirements?buyer_id={buyer_id}", headers=headers)
    assert res.status_code == 200
    req_list = res.json()
    assert req_list["total"] >= 1
    assert req_list["total_quantity_kg"] >= 4000.0

    # 5. Update requirement
    update_req = {"quantity_kg": 4500.0, "max_price_per_kg": 155.00}
    res = client.put(f"/api/v1/buyers/requirements/{req_id}", json=update_req, headers=headers)
    assert res.status_code == 200
    assert res.json()["quantity_kg"] == 4500.0


# ---------------------------------------------------------------------------
# 3. Matching Engine API Tests
# ---------------------------------------------------------------------------


def test_matching_engine_api_workflow(client, auth_context, db):
    headers = auth_context["staff_headers"]
    fpo_id = str(auth_context["fpo"].id)
    farmer_id = auth_context["farmer"].id
    crop_id = auth_context["crop"].id

    # Create standing plot
    plot = Farm(
        farmer_id=farmer_id,
        crop_id=crop_id,
        plot_name="Matching Candidate Plot",
        area_acres=3.0,
        village="Perundurai",
        soil_type="red loam",
        irrigation_type="drip",
        expected_yield_kg=7500.0,
        expected_harvest_date=date.today() + timedelta(days=15),
        status="growing",
        district_id=auth_context["district"].id,
    )
    db.add(plot)
    db.commit()

    # Create buyer & requirement
    buyer = Buyer(
        company_name=f"Match Buyer {uuid.uuid4().hex[:4]}",
        buyer_type="processor",
        contact_phone="9842999888",
        location="Perundurai",
        district=auth_context["district"].name,
        district_id=auth_context["district"].id,
        fpo_id=auth_context["fpo"].id,
    )
    db.add(buyer)
    db.commit()

    req = BuyerRequirement(
        buyer_id=buyer.id,
        fpo_id=auth_context["fpo"].id,
        crop_id=crop_id,
        district_id=auth_context["district"].id,
        quantity_kg=5000.0,
        min_grade=HarvestGrade.A,
        required_date=date.today() + timedelta(days=20),
        delivery_window_days=7,
        max_price_per_kg=Decimal("140.00"),
        delivery_location="Perundurai Hub",
        status="open",
    )
    db.add(req)
    db.commit()

    # 1. Search candidates via API
    res = client.get(f"/api/v1/matching/candidates/{req.id}", headers=headers)
    assert res.status_code == 200
    candidate_data = res.json()
    assert candidate_data["total_candidates"] >= 1
    best_candidate = candidate_data["candidates"][0]
    assert best_candidate["candidate_type"] == "farm_plot"
    assert best_candidate["match_score"] > 0

    # 2. Record suggested match
    suggest_payload = {
        "buyer_requirement_id": str(req.id),
        "farm_id": str(plot.id),
        "fpo_id": fpo_id,
        "matched_quantity_kg": 5000.0,
        "match_score": best_candidate["match_score"],
        "match_breakdown": best_candidate["match_breakdown"],
        "offered_price_per_kg": 138.00,
        "staff_notes": "Initial auto-match for testing",
    }
    res = client.post("/api/v1/matching/suggest", json=suggest_payload, headers=headers)
    assert res.status_code == 201
    match_resp = res.json()
    match_id = match_resp["id"]
    assert match_resp["status"] == "suggested"

    # 3. Summary endpoint (unfulfilled demand before confirmation)
    res = client.get(f"/api/v1/matching/summary?fpo_id={fpo_id}", headers=headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_standing_acres"] >= 3.0
    assert summary["total_demand_kg"] >= 5000.0

    # 4. Staff confirmation
    confirm_payload = {
        "staff_notes": "Phone verified with farmer; harvest date confirmed.",
        "offered_price_per_kg": 140.00,
    }
    res = client.post(f"/api/v1/matching/{match_id}/confirm", json=confirm_payload, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed_by_staff"
    assert float(res.json()["offered_price_per_kg"]) == 140.00

    # 5. Reject / Dismiss match (reverts fulfilled demand)
    res = client.post(
        f"/api/v1/matching/{match_id}/reject?notes=Cancelled+by+staff", headers=headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


# ---------------------------------------------------------------------------
# 4. WhatsApp Inbound "BUYERS" Intent Test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_whatsapp_bot_buyers_intent(db, auth_context):
    """Verify WhatsApp bot inbound 'BUYERS' query handles both confirmed matches and open demand."""

    @contextlib.contextmanager
    def test_db_factory():
        yield db

    bot_svc = DbBotServices(test_db_factory)
    channel = MockChannel()
    bot = BotEngine(services=bot_svc)

    farmer_phone = auth_context["farmer_user"].phone
    farmer_id = auth_context["farmer"].id
    crop_id = auth_context["crop"].id

    # 1. Setup plot and confirmed match
    plot = Farm(
        farmer_id=farmer_id,
        crop_id=crop_id,
        plot_name="Bot Test Plot",
        area_acres=2.0,
        village="Perundurai",
        soil_type="red loam",
        irrigation_type="drip",
        expected_yield_kg=5000.0,
        status="growing",
        district_id=auth_context["district"].id,
    )
    db.add(plot)
    db.commit()

    buyer = Buyer(
        company_name=f"Bot Test Buyer {uuid.uuid4().hex[:4]}",
        buyer_type="processor",
        contact_phone="9842555666",
        location="Perundurai",
        district=auth_context["district"].name,
        district_id=auth_context["district"].id,
        fpo_id=auth_context["fpo"].id,
    )
    db.add(buyer)
    db.commit()

    req = BuyerRequirement(
        buyer_id=buyer.id,
        fpo_id=auth_context["fpo"].id,
        crop_id=crop_id,
        district_id=auth_context["district"].id,
        quantity_kg=5000.0,
        min_grade=HarvestGrade.A,
        required_date=date.today() + timedelta(days=15),
        max_price_per_kg=Decimal("142.00"),
        delivery_location="Perundurai Warehouse",
        status="open",
    )
    db.add(req)
    db.commit()

    match = SupplyMatch(
        buyer_requirement_id=req.id,
        farm_id=plot.id,
        fpo_id=auth_context["fpo"].id,
        matched_quantity_kg=5000.0,
        offered_price_per_kg=Decimal("142.00"),
        match_score=0.95,
        status="confirmed_by_staff",
    )
    db.add(match)
    db.commit()

    # Inbound message: "BUYERS"
    inbound = InboundMessage(
        message_id=f"wamid.{uuid.uuid4().hex}",
        wa_id=farmer_phone,
        kind="text",
        text="BUYERS",
    )
    await bot.handle(inbound, channel)

    assert len(channel.sent_messages) >= 1
    response_text = channel.sent_messages[-1]["text"]
    # Check that confirmed opportunity notification text is returned in Tamil (farmer's preferred lang)
    assert "உறுதிப்படுத்தப்பட்ட கொள்முதல் வாய்ப்பு" in response_text
    assert buyer.company_name in response_text
    assert "142.00" in response_text
