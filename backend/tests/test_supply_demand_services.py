"""Integration and unit tests for Wave 2: Yield Estimator, Farm/Buyer Services, CSV Import, and Matching Engine."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest, HarvestGrade, HarvestStatus
from app.models.user import User, UserRole
from app.schemas.buyer import (
    BuyerCreate,
    BuyerRequirementCreate,
    BuyerRequirementUpdate,
)
from app.schemas.farm import FarmCreate, FarmUpdate
from app.services.buyer_service import (
    create_buyer,
    create_buyer_requirement,
    list_buyer_requirements,
    update_buyer_requirement,
)
from app.services.csv_import import import_buyers_csv, import_farms_csv
from app.services.farm_service import (
    create_farm,
    get_farmer_plots,
    list_farms,
    update_farm,
)
from app.services.matching_service import (
    confirm_match_by_staff,
    create_or_suggest_match,
    find_candidate_matches_for_requirement,
    get_supply_demand_summary,
    reject_match_by_staff,
)
from app.services.yield_estimator import (
    estimate_crop_yield,
)


def test_yield_estimator_benchmarks_and_multipliers():
    """Verify rule-based yield estimation adheres to TNAU benchmarks and multipliers."""
    # 1. Turmeric baseline (2500 kg/acre) with Drip (+15%) and Red Loam (+10%)
    est = estimate_crop_yield(
        crop_name="turmeric",
        area_acres=2.0,
        soil_type="Red Loam",
        irrigation_type="Drip",
        sowing_date=date(2026, 6, 1),
    )
    # Expected = 2.0 * 2500 * 1.10 * 1.15 = 6325.0
    assert est["base_yield_kg_per_acre"] == 2500.0
    assert est["soil_factor"] == 1.10
    assert est["irrigation_factor"] == 1.15
    assert est["estimated_yield_kg"] == 6325.0
    # Gestation: 270 days
    assert est["estimated_harvest_window_start"] == date(2026, 6, 1) + timedelta(days=270)

    # 2. Rainfed banana with clay soil penalty
    est_rain = estimate_crop_yield(
        crop_name="banana",
        area_acres=1.0,
        soil_type="Clay",
        irrigation_type="Rainfed",
    )
    # Expected = 1.0 * 18000 * 0.85 * 0.70 = 10710.0
    assert est_rain["estimated_yield_kg"] == 10710.0


def test_farm_service_crud_and_auto_yield(db):
    """Verify Farm CRUD operations and automated yield estimation."""
    user = User(
        name="Arun Farmer",
        phone=f"96{uuid.uuid4().int % 100000000:08d}",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(user)
    db.flush()

    fpo = FPO(
        name="Modakkurichi FPO",
        registration_number=f"FPO-MOD-{uuid.uuid4().hex[:6]}",
        district="Erode",
        village="Modakkurichi",
        contact_phone="9441122334",
    )
    db.add(fpo)
    db.flush()

    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo.id,
        village="Modakkurichi",
        taluk="Modakkurichi",
        district="Erode",
        farm_area_acres=5.0,
    )
    db.add(farmer)
    db.flush()

    crop = db.query(Crop).filter(Crop.name.ilike("%turmeric%")).first()
    if not crop:
        crop = db.query(Crop).first()

    # 1. Create Farm plot (without explicit expected yield)
    farm_data = FarmCreate(
        farmer_id=farmer.id,
        crop_id=crop.id,
        plot_name="North Field",
        area_acres=2.0,
        village="Modakkurichi",
        soil_type="Red Loam",
        irrigation_type="Drip",
        sowing_date=date(2026, 5, 15),
    )
    farm = create_farm(db, farm_data)
    assert farm.id is not None
    assert farm.expected_yield_kg is not None
    assert farm.expected_yield_kg > 0.0
    assert farm.expected_harvest_date is not None

    # 2. List farms
    farms, total, total_acres = list_farms(db, farmer_id=farmer.id)
    assert total == 1
    assert total_acres == 2.0
    assert farms[0].plot_name == "North Field"

    # 3. Update farm area
    updated = update_farm(db, farm.id, FarmUpdate(area_acres=3.0))
    assert updated.area_acres == 3.0
    # Expected yield should have recalculated for 3 acres
    assert updated.expected_yield_kg > farm_data.area_acres * 2000.0

    # 4. Get plots
    plots = get_farmer_plots(db, farmer.id)
    assert len(plots) == 1


def test_buyer_service_crud_and_requirements(db):
    """Verify staff-mediated buyer creation, listing, and requirement fulfillment."""
    fpo = db.query(FPO).first()
    crop = db.query(Crop).first()

    # 1. Create buyer
    buyer_in = BuyerCreate(
        company_name="Sakthi Masala Private Limited",
        buyer_type="processor",
        contact_name="Mr. Duraisamy",
        contact_phone="9842233445",
        contact_email="procurement@sakthimasala.example.com",
        location="Erode Mamangam",
        district="Erode",
        fpo_id=fpo.id if fpo else None,
        verified=True,
    )
    buyer = create_buyer(db, buyer_in)
    assert buyer.id is not None
    assert buyer.company_name == "Sakthi Masala Private Limited"

    # 2. Post requirement
    req_in = BuyerRequirementCreate(
        buyer_id=buyer.id,
        fpo_id=fpo.id if fpo else None,
        crop_id=crop.id,
        quantity_kg=10000.0,
        min_grade=HarvestGrade.A,
        required_date=date.today() + timedelta(days=45),
        max_price_per_kg=Decimal("130.00"),
        delivery_location="Sakthi Masala Factory Gate 2",
    )
    req = create_buyer_requirement(db, req_in)
    assert req.id is not None
    assert req.status == "open"
    assert req.quantity_kg == 10000.0

    # 3. List requirements
    reqs, total_count, total_qty = list_buyer_requirements(db, buyer_id=buyer.id)
    assert total_count >= 1
    assert total_qty >= 10000.0

    # 4. Update requirement (partial fulfillment)
    updated_req = update_buyer_requirement(
        db, req.id, BuyerRequirementUpdate(fulfilled_quantity_kg=10000.0)
    )
    assert updated_req.status == "fulfilled"


def test_csv_import_farms_and_buyers(db):
    """Verify CSV import pipeline handles bulk plot and buyer ingestion."""
    # Setup FPO and Farmer
    user = User(
        name="CSV Test Farmer",
        phone="9988776655",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(user)
    db.flush()

    fpo = FPO(
        name="CSV Test FPO",
        registration_number=f"FPO-CSV-{uuid.uuid4().hex[:6]}",
        district="Erode",
        village="Erode",
        contact_phone="9988776600",
    )
    db.add(fpo)
    db.flush()

    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo.id,
        phone="9988776655",
        village="Erode",
        taluk="Erode",
        district="Erode",
        farm_area_acres=10.0,
    )
    db.add(farmer)
    db.commit()

    # 1. Import Farms CSV
    csv_farms = """farmer_phone,crop_name,plot_name,area_acres,village,soil_type,irrigation_type,sowing_date
9988776655,turmeric,East Field,2.5,Erode,Red Loam,Drip,2026-06-01
9988776655,banana,West Field,1.8,Erode,Alluvial,Canal,2026-05-15
9111111111,turmeric,Invalid Farmer,1.0,Erode,Red Loam,Drip,2026-06-01
"""
    farm_res = import_farms_csv(db, fpo.id, csv_farms)
    assert farm_res["imported"] == 2
    assert farm_res["errors_count"] == 1  # 1 unknown farmer

    # 2. Import Buyers CSV
    c_p1 = f"98{uuid.uuid4().int % 100000000:08d}"
    c_p2 = f"98{uuid.uuid4().int % 100000000:08d}"
    c_n1 = f"Everest Spices {uuid.uuid4().hex[:4]}"
    c_n2 = f"Grand Supermarket {uuid.uuid4().hex[:4]}"
    csv_buyers = f"""company_name,contact_phone,location,buyer_type,crop_name,quantity_kg,min_grade,max_price_per_kg
{c_n1},{c_p1},Erode,processor,turmeric,5000,A,135.00
{c_n2},{c_p2},Salem,retailer,banana,2000,B,28.50
"""
    buyer_res = import_buyers_csv(db, fpo.id, csv_buyers)
    assert buyer_res["buyers_imported"] >= 1
    assert buyer_res["requirements_imported"] >= 1


def test_matching_engine_candidate_ranking_and_staff_workflow(db):
    """Verify semi-automatic matching engine candidate ranking and staff confirmation workflow."""
    crop = db.query(Crop).filter(Crop.name.ilike("%turmeric%")).first()
    if not crop:
        crop = db.query(Crop).first()

    fpo = db.query(FPO).first()

    # 1. Setup Buyer and Requirement
    buyer = Buyer(
        company_name="Universal Foods Exporters",
        contact_phone="9944001122",
        location="Erode",
        district="Erode",
        fpo_id=fpo.id if fpo else None,
    )
    db.add(buyer)
    db.flush()

    req = BuyerRequirement(
        buyer_id=buyer.id,
        fpo_id=fpo.id if fpo else None,
        crop_id=crop.id,
        quantity_kg=4000.0,
        fulfilled_quantity_kg=0.0,
        min_grade=HarvestGrade.B,
        required_date=date.today() + timedelta(days=20),
        delivery_location="Erode Cold Storage Hub",
    )
    db.add(req)
    db.flush()

    # 2. Setup Farmer 1 with matching Farm plot
    u1 = User(
        name="Kavitha Farmer",
        phone=f"95{uuid.uuid4().int % 100000000:08d}",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(u1)
    db.flush()
    farmer1 = Farmer(
        user_id=u1.id,
        fpo_id=fpo.id,
        village="Erode",
        taluk="Erode",
        district="Erode",
        farm_area_acres=4.0,
    )
    db.add(farmer1)
    db.flush()
    farm1 = Farm(
        farmer_id=farmer1.id,
        crop_id=crop.id,
        plot_name="High Curcumin Plot",
        area_acres=2.0,
        expected_yield_kg=4500.0,
        expected_harvest_date=date.today() + timedelta(days=18),
        status="active",
    )
    db.add(farm1)

    # 3. Setup Farmer 2 with verified Harvest
    u2 = User(
        name="Nagaraj Farmer",
        phone=f"94{uuid.uuid4().int % 100000000:08d}",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(u2)
    db.flush()
    farmer2 = Farmer(
        user_id=u2.id,
        fpo_id=fpo.id,
        village="Bhavani",
        taluk="Bhavani",
        district="Erode",
        farm_area_acres=3.0,
    )
    db.add(farmer2)
    db.flush()
    harvest1 = Harvest(
        farmer_id=farmer2.id,
        crop_id=crop.id,
        quantity_kg=3800.0,
        grade=HarvestGrade.A,
        harvest_date=date.today(),
        status=HarvestStatus.VERIFIED,
    )
    db.add(harvest1)
    db.commit()

    # 4. Test candidate finding
    candidates = find_candidate_matches_for_requirement(db, req.id, max_candidates=10)
    assert len(candidates) >= 2
    # Verify candidate structure
    top_candidate = candidates[0]
    assert "candidate_type" in top_candidate
    assert "match_score" in top_candidate
    assert top_candidate["match_score"] > 70.0
    assert "match_breakdown" in top_candidate
    assert top_candidate["match_breakdown"]["crop_match"] is True

    # 5. Create suggested match
    staff_user = (
        db.query(User)
        .filter(User.role.in_([UserRole.ADMIN, UserRole.FPO_ADMIN, UserRole.FPO_STAFF]))
        .first()
    )
    staff_id = staff_user.id if staff_user else u1.id

    match = create_or_suggest_match(
        db=db,
        requirement_id=req.id,
        matched_quantity_kg=3800.0,
        match_score=top_candidate["match_score"],
        match_breakdown=top_candidate["match_breakdown"],
        harvest_id=harvest1.id,
        offered_price_per_kg=Decimal("120.00"),
        staff_notes="Candidate harvest batch inspected by FPO staff",
    )
    assert match.id is not None
    assert match.status == "suggested"

    # 6. Staff confirmation
    confirmed = confirm_match_by_staff(
        db, match.id, staff_id, notes="Confirmed via phone call with farmer"
    )
    assert confirmed.status == "confirmed_by_staff"
    assert confirmed.confirmed_at is not None

    # Verify requirement fulfilled quantity updated
    db.refresh(req)
    assert req.fulfilled_quantity_kg == 3800.0
    assert req.status == "partially_fulfilled"

    # 7. Test rejection workflow
    rejected = reject_match_by_staff(db, match.id, staff_id, notes="Farmer declined offer")
    assert rejected.status == "rejected"
    db.refresh(req)
    assert req.fulfilled_quantity_kg == 0.0

    # 8. Test supply demand summary
    summary = get_supply_demand_summary(db, fpo_id=fpo.id)
    assert summary is not None
    assert summary["total_supply_kg"] > 0.0
    assert summary["total_demand_kg"] > 0.0
    assert len(summary["commodities"]) >= 1
