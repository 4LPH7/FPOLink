"""End-to-end integration tests for complete operational user journeys."""

import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.data_quality import IngestionRun
from app.models.fpo import FPO
from app.models.harvest import HarvestGrade
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.raw_ingest import RawIngest
from app.models.variety import Variety
from scripts.create_admin import create_or_update_admin


def _random_phone(prefix: str = "98") -> str:
    """Generate a valid 10-digit numeric phone number."""
    suffix = str(abs(hash(uuid.uuid4().hex)))[:8].zfill(8)
    return f"{prefix}{suffix}"


def test_journey_admin_bootstrap_and_password_rotation(client, db):
    """Journey 1: Administrator creation -> login -> required password rotation -> access granted."""
    phone = _random_phone("99")
    initial_pass = "TempAdmin@123"
    rotated_pass = "RotatedSecure@2026"

    # 1. Provision initial admin via create_admin script with must_change_password=True
    admin_user = create_or_update_admin(
        phone=phone,
        password=initial_pass,
        name="Field Pilot Director",
        fpo_name="Erode Pilot FPO",
        must_change_password=True,
    )
    assert admin_user.password_change_required is True

    # 2. Login with temporary password
    login_res = client.post("/api/auth/login", json={"phone": phone, "password": initial_pass})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["password_change_required"] is True
    temp_token = login_data["access_token"]

    # 3. Blocked from operational routes while rotation is pending
    prot_res = client.get("/api/fpos/", headers={"Authorization": f"Bearer {temp_token}"})
    assert prot_res.status_code in (401, 403)

    # 4. Rotate password
    change_res = client.post(
        "/api/auth/change-password",
        json={"current_password": initial_pass, "new_password": rotated_pass},
        headers={"Authorization": f"Bearer {temp_token}"},
    )
    assert change_res.status_code == 200
    rotated_token = change_res.json()["access_token"]

    # 5. Operational access now succeeds
    success_res = client.get("/api/fpos/", headers={"Authorization": f"Bearer {rotated_token}"})
    assert success_res.status_code == 200


def test_journey_farmer_registration_consent_and_harvest(client, db, admin_headers):
    """Journey 2: Farmer registration -> consent capture -> harvest logging."""
    fpo = FPO(
        name=f"Pilot FPO {uuid.uuid4().hex[:6]}",
        registration_number=f"REG-{uuid.uuid4().hex[:8]}",
        district="Erode",
        village="Modakkurichi",
        contact_phone=_random_phone("91"),
    )
    db.add(fpo)
    db.commit()

    farmer_phone = _random_phone("98")

    # 1. Register farmer with DPDP consent
    farmer_payload = {
        "name": "Selvam",
        "phone": farmer_phone,
        "password": "FarmerPassword@123",
        "village": "Modakkurichi",
        "taluk": "Erode",
        "district": "Erode",
        "farm_area_acres": 3.5,
        "language_preference": "ta",
        "consent_given": True,
        "alerts_opt_in": True,
    }
    reg_res = client.post(f"/api/farmers/{fpo.id}", json=farmer_payload, headers=admin_headers)
    assert reg_res.status_code == 201
    farmer_data = reg_res.json()
    farmer_id = farmer_data["id"]

    # 2. Check farmer consent stored
    assert farmer_data["alerts_opt_in"] is True

    # 3. Log harvest for this farmer
    crop = Crop(
        name=f"Turmeric-{uuid.uuid4().hex[:4]}",
        canonical_name=f"turmeric-{uuid.uuid4().hex[:4]}",
        tamil_name="மஞ்சள்",
    )
    db.add(crop)
    db.commit()

    harvest_payload = {
        "farmer_id": farmer_id,
        "crop_id": str(crop.id),
        "fpo_id": str(fpo.id),
        "quantity_kg": 1200.0,
        "expected_date": (date.today() + timedelta(days=5)).isoformat(),
        "status": "ready_for_pickup",
        "quality_grade": "Grade A",
        "notes": "Organic turmeric harvest",
    }
    harv_res = client.post("/api/harvest/", json=harvest_payload, headers=admin_headers)
    assert harv_res.status_code == 201
    created_harvest = harv_res.json()
    assert float(created_harvest["quantity_kg"]) == 1200.0


def test_journey_raw_ingestion_to_displayed_price_lineage(client, db):
    """Journey 3: Raw ingestion -> canonical mapping -> quality scoring -> displayed price with lineage."""
    crop = Crop(
        name=f"Paddy-{uuid.uuid4().hex[:4]}",
        canonical_name=f"paddy-{uuid.uuid4().hex[:4]}",
        tamil_name="நெல்",
    )
    variety = Variety(crop=crop, name="Ponni", grade="FAQ")
    market = Market(
        name=f"Erode Mandi-{uuid.uuid4().hex[:4]}", district="Erode", state="Tamil Nadu"
    )
    db.add_all([crop, variety, market])
    db.commit()

    run = IngestionRun(
        source_code="ogd",
        district="Erode",
        status="COMPLETED",
        records_fetched=1,
        records_ingested=1,
        started_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.commit()

    raw = RawIngest(
        source="ogd",
        source_record_id=f"rec-{uuid.uuid4().hex[:8]}",
        payload={"commodity": "Paddy", "market": "Erode", "modal_price": "2400"},
        checksum=uuid.uuid4().hex,
        processed=True,
    )
    db.add(raw)
    db.commit()

    price = MarketPrice(
        crop_id=crop.id,
        variety_id=variety.id,
        market_id=market.id,
        district="Erode",
        min_price=Decimal("23.00"),
        max_price=Decimal("25.00"),
        modal_price=Decimal("24.00"),
        raw_price=Decimal("2400.00"),
        raw_unit="quintal",
        price_date=date.today(),
        source="ogd",
        quality_score=95.0,
        quality_breakdown={"freshness": 100, "source": 90, "match": 95},
        ingestion_run_id=run.id,
        raw_ingest_id=raw.id,
    )
    db.add(price)
    db.commit()

    # Query latest prices
    res = client.get("/api/prices/latest?district=Erode")
    assert res.status_code == 200
    prices = res.json()["prices"]
    match = next((p for p in prices if p["crop_name"] == crop.name), None)
    assert match is not None
    assert match["variety_name"] == "Ponni"
    assert match["source"] == "ogd"
    assert match["is_stale"] is False
    assert match["freshness_category"] == "fresh"
    assert match["raw_ingest_id"] == str(raw.id)

    # Query full lineage
    lineage_res = client.get(f"/api/v1/prices/{price.id}/lineage")
    assert lineage_res.status_code == 200
    lineage = lineage_res.json()
    assert lineage["ingestion_run"]["status"] == "COMPLETED"
    assert lineage["raw_ingest"]["checksum"] == raw.checksum


def test_journey_buyer_requirement_supply_match_and_task(client, db, admin_headers):
    """Journey 4: Buyer requirement -> supply match -> staff follow-up task."""
    fpo = FPO(
        name=f"Supply FPO {uuid.uuid4().hex[:6]}",
        registration_number=f"REG-{uuid.uuid4().hex[:8]}",
        district="Erode",
        village="Perundurai",
        contact_phone=_random_phone("91"),
    )
    crop = Crop(
        name=f"Banana-{uuid.uuid4().hex[:4]}",
        canonical_name=f"banana-{uuid.uuid4().hex[:4]}",
        tamil_name="வாழை",
    )
    db.add_all([fpo, crop])
    db.commit()

    # 1. Create Buyer & Buyer Requirement
    buyer = Buyer(
        company_name="Green Supermarket",
        buyer_type="retailer",
        contact_name="Ramesh",
        contact_phone="9844112233",
        location="Coimbatore",
        district="Coimbatore",
        verified=True,
    )
    db.add(buyer)
    db.commit()

    req = BuyerRequirement(
        buyer_id=buyer.id,
        crop_id=crop.id,
        quantity_kg=5000.0,
        min_grade=HarvestGrade.A,
        max_price_per_kg=Decimal("35.00"),
        delivery_location="Coimbatore",
        status="open",
        required_date=date.today() + timedelta(days=10),
    )
    db.add(req)
    db.commit()

    # 2. Staff creates follow-up task for this buyer opportunity
    task_payload = {
        "title": f"Follow up with {buyer.company_name} for {crop.name} requirement",
        "description": "Call Ramesh to negotiate dispatch date and transport pooling",
        "fpo_id": str(fpo.id),
        "priority": "high",
        "status": "todo",
        "due_date": (date.today() + timedelta(days=2)).isoformat(),
    }
    task_res = client.post("/api/tasks", json=task_payload, headers=admin_headers)
    assert task_res.status_code == 201
    task = task_res.json()
    task_id = task["id"]
    assert task["status"] == "todo"

    # 3. Staff completes the task
    update_res = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "done"},
        headers=admin_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "done"


def test_journey_stale_data_warning_on_outage(client, db):
    """Journey 5: Mandi provider outage / stale data displays explicit stale warning."""
    crop = Crop(
        name=f"StaleCrop-{uuid.uuid4().hex[:4]}",
        canonical_name=f"stalecrop-{uuid.uuid4().hex[:4]}",
        tamil_name="பயிர்",
    )
    market = Market(
        name=f"StaleMarket-{uuid.uuid4().hex[:4]}", district="Dharmapuri", state="Tamil Nadu"
    )
    db.add_all([crop, market])
    db.commit()

    # Insert price from 10 days ago (simulating feed outage)
    stale_price = MarketPrice(
        crop_id=crop.id,
        market_id=market.id,
        district="Dharmapuri",
        min_price=Decimal("18.00"),
        max_price=Decimal("22.00"),
        modal_price=Decimal("20.00"),
        price_date=date.today() - timedelta(days=10),
        source="ogd",
    )
    db.add(stale_price)
    db.commit()

    # Query latest prices
    res = client.get("/api/prices/latest?district=Dharmapuri")
    assert res.status_code == 200
    prices = res.json()["prices"]
    p = next((x for x in prices if x["crop_name"] == crop.name), None)
    assert p is not None
    assert p["is_stale"] is True
    assert p["stale_days"] == 10
    assert p["freshness_category"] == "outdated"

    # Query forecast endpoint -> check stale warning metadata
    fc_res = client.get(f"/api/v1/intelligence/forecast?crop_id={crop.id}&market_id={market.id}")
    assert fc_res.status_code == 200
    fc = fc_res.json()
    assert fc["is_stale"] is True
    assert fc["days_since_last_observation"] == 10
    assert "uncertainty" in fc["stale_warning"].lower()
