"""Tests for Phase 13 Wave 1: Supply and demand models, migrations, and Pydantic schemas."""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest, HarvestGrade
from app.models.supply_match import SupplyMatch
from app.models.user import User, UserRole
from app.schemas.buyer import (
    BuyerCreate,
    BuyerRequirementCreate,
    BuyerRequirementResponse,
    BuyerResponse,
)
from app.schemas.farm import (
    FarmCreate,
    FarmListResponse,
    FarmResponse,
    FarmYieldEstimateResponse,
)
from app.schemas.matching import (
    MatchBreakdown,
    MatchCandidate,
    MatchCandidateListResponse,
    MatchConfirmRequest,
    MatchCreate,
    MatchResponse,
    SupplyDemandCropSummary,
    SupplyDemandSummaryResponse,
)


def test_farm_model_and_plot_expansion(db):
    """Verify Farm model supports discrete plot attributes and multi-plot relationships."""
    # 1. Create User, FPO, Farmer, Crop
    user = User(
        name="Selvam Farmer",
        phone=f"98{uuid.uuid4().int % 100000000:08d}",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(user)
    db.flush()

    fpo = FPO(
        name="Kodumudi Turmeric FPO",
        registration_number=f"FPO-KOD-{uuid.uuid4().hex[:6]}",
        district="Erode",
        village="Kodumudi",
        contact_phone="9443322110",
    )
    db.add(fpo)
    db.flush()

    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo.id,
        village="Solangapalayam",
        taluk="Kodumudi",
        district="Erode",
        farm_area_acres=4.5,
    )
    db.add(farmer)
    db.flush()

    crop = db.query(Crop).first()
    if not crop:
        crop = Crop(name=f"Crop-{uuid.uuid4().hex[:4]}", unit="kg")
        db.add(crop)
        db.flush()

    # 2. Add two distinct plots for this farmer
    plot1 = Farm(
        farmer_id=farmer.id,
        crop_id=crop.id,
        plot_name="Canal North Plot",
        area_acres=2.5,
        village="Solangapalayam",
        soil_type="Red Loam",
        irrigation_type="Drip",
        sowing_date=date(2026, 6, 1),
        expected_harvest_date=date(2027, 2, 15),
        expected_yield_kg=6250.0,
        status="active",
    )
    plot2 = Farm(
        farmer_id=farmer.id,
        crop_id=crop.id,
        plot_name="River South Plot",
        area_acres=2.0,
        village="Solangapalayam",
        soil_type="Alluvial",
        irrigation_type="Canal",
        sowing_date=date(2026, 6, 10),
        expected_harvest_date=date(2027, 2, 25),
        expected_yield_kg=4800.0,
        status="active",
    )
    db.add_all([plot1, plot2])
    db.commit()

    # 3. Assertions
    refreshed_farmer = db.query(Farmer).filter(Farmer.id == farmer.id).first()
    assert len(refreshed_farmer.farms) >= 2
    plots = {f.plot_name: f for f in refreshed_farmer.farms}
    assert "Canal North Plot" in plots
    assert plots["Canal North Plot"].soil_type == "Red Loam"
    assert plots["Canal North Plot"].irrigation_type == "Drip"
    assert plots["Canal North Plot"].expected_yield_kg == 6250.0


def test_staff_mediated_buyer_and_requirements(db):
    """Verify Buyer model works without a user_id (staff-entered) and supports requirements."""
    fpo = db.query(FPO).first()
    crop = db.query(Crop).first()

    # Create staff-entered buyer
    buyer = Buyer(
        user_id=None,  # Nullable for staff mediation
        fpo_id=fpo.id if fpo else None,
        company_name="ITC Spices Division - Erode",
        buyer_type="processor",
        contact_name="Ramesh Procurement Head",
        contact_phone="9876501234",
        contact_email="ramesh@itcspices.example.com",
        location="Erode SIPCOT Industrial Estate",
        district="Erode",
        gstin="33AAAAA0000A1Z5",
        verified=True,
    )
    db.add(buyer)
    db.flush()

    assert buyer.id is not None
    assert buyer.user_id is None
    assert buyer.buyer_type == "processor"

    # Post procurement requirement
    req = BuyerRequirement(
        buyer_id=buyer.id,
        fpo_id=fpo.id if fpo else None,
        crop_id=crop.id,
        quantity_kg=5000.0,
        fulfilled_quantity_kg=0.0,
        min_grade=HarvestGrade.A,
        required_date=date(2027, 3, 1),
        delivery_window_days=10,
        max_price_per_kg=Decimal("125.50"),
        delivery_location="SIPCOT Warehouse Bay 3",
        status="open",
        notes="High curcumin content preferred (> 3.5%)",
    )
    db.add(req)
    db.commit()

    refreshed_buyer = db.query(Buyer).filter(Buyer.id == buyer.id).first()
    assert len(refreshed_buyer.requirements) >= 1
    r = refreshed_buyer.requirements[0]
    assert r.quantity_kg == 5000.0
    assert r.min_grade == HarvestGrade.A
    assert r.max_price_per_kg == Decimal("125.50")
    assert r.delivery_window_days == 10


def test_supply_match_model(db):
    """Verify SupplyMatch model links buyer requirements with farm plots and harvests."""
    crop = db.query(Crop).first()
    fpo = db.query(FPO).first()

    # 1. Setup buyer & requirement
    buyer = Buyer(
        company_name="Aachi Masala Foods",
        contact_phone="9840011223",
        location="Chennai",
        district="Chennai",
    )
    db.add(buyer)
    db.flush()

    req = BuyerRequirement(
        buyer_id=buyer.id,
        crop_id=crop.id,
        quantity_kg=3000.0,
        min_grade=HarvestGrade.B,
        required_date=date.today() + timedelta(days=30),
    )
    db.add(req)
    db.flush()

    # 2. Setup user/farmer/plot
    user = User(
        name="Murugan Farmer",
        phone=f"97{uuid.uuid4().int % 100000000:08d}",
        role=UserRole.FARMER,
        hashed_password="pw",
    )
    db.add(user)
    db.flush()

    farmer = Farmer(
        user_id=user.id,
        fpo_id=fpo.id,
        village="Bhavani",
        taluk="Bhavani",
        district="Erode",
        farm_area_acres=3.0,
    )
    db.add(farmer)
    db.flush()

    farm = Farm(
        farmer_id=farmer.id,
        crop_id=crop.id,
        plot_name="Plot South 1",
        area_acres=2.0,
        village="Bhavani",
        expected_yield_kg=3500.0,
    )
    db.add(farm)
    db.flush()

    # 3. Create SupplyMatch
    match = SupplyMatch(
        buyer_requirement_id=req.id,
        farm_id=farm.id,
        fpo_id=fpo.id,
        matched_quantity_kg=3000.0,
        offered_price_per_kg=Decimal("110.00"),
        match_score=88.5,
        match_breakdown={
            "crop_match": True,
            "distance_km": 42.0,
            "proximity_score": 86.0,
            "quantity_fit_ratio": 1.0,
            "timing_days_delta": 4,
            "timing_score": 80.0,
            "grade_score": 100.0,
        },
        status="suggested",
        staff_notes="Verified by field agent via telephone",
    )
    db.add(match)
    db.commit()

    refreshed_match = db.query(SupplyMatch).filter(SupplyMatch.id == match.id).first()
    assert refreshed_match is not None
    assert refreshed_match.match_score == 88.5
    assert refreshed_match.match_breakdown["distance_km"] == 42.0
    assert refreshed_match.status == "suggested"
    assert refreshed_match.farm.plot_name == "Plot South 1"
    assert refreshed_match.buyer_requirement.buyer.company_name == "Aachi Masala Foods"


def test_pydantic_schemas_validation():
    """Verify validation on Farm, Buyer, and Matching Pydantic schemas."""
    # Farm schemas
    farm_in = FarmCreate(
        farmer_id=uuid.uuid4(),
        crop_id=uuid.uuid4(),
        plot_name="Plot West",
        area_acres=3.2,
        village="Kodumudi",
        soil_type="Red Loam",
        irrigation_type="Drip",
        sowing_date=date(2026, 5, 10),
    )
    assert farm_in.area_acres == 3.2
    assert farm_in.soil_type == "Red Loam"

    with pytest.raises(Exception):
        FarmCreate(
            farmer_id=uuid.uuid4(),
            crop_id=uuid.uuid4(),
            area_acres=-1.0,  # invalid <= 0
        )

    # Buyer schemas
    buyer_in = BuyerCreate(
        company_name="Nilgiris Mart",
        contact_phone="9876543210",
        location="Coimbatore",
        buyer_type="retailer",
    )
    assert buyer_in.company_name == "Nilgiris Mart"
    assert buyer_in.buyer_type == "retailer"

    # Match schemas
    breakdown = MatchBreakdown(
        crop_match=True,
        distance_km=25.5,
        proximity_score=91.5,
        quantity_fit_ratio=0.95,
        timing_days_delta=2,
        timing_score=90.0,
        grade_score=100.0,
        composite_score=93.8,
    )
    candidate = MatchCandidate(
        candidate_type="farm_plot",
        source_id=str(uuid.uuid4()),
        farmer_id=str(uuid.uuid4()),
        farmer_name="Kandasamy",
        farmer_phone="9443311220",
        crop_id=str(uuid.uuid4()),
        crop_name="turmeric",
        available_quantity_kg=2500.0,
        match_score=93.8,
        match_breakdown=breakdown,
    )
    assert candidate.match_score == 93.8
    assert candidate.match_breakdown.distance_km == 25.5

    # Supply demand summary
    summary = SupplyDemandSummaryResponse(
        commodities=[
            SupplyDemandCropSummary(
                crop_id=str(uuid.uuid4()),
                crop_name="turmeric",
                crop_tamil_name="மஞ்சள்",
                standing_acres=45.0,
                estimated_standing_yield_kg=112500.0,
                verified_harvest_kg=15000.0,
                total_supply_kg=127500.0,
                total_demand_kg=80000.0,
                net_balance_kg=47500.0,
                active_plots_count=18,
                open_requirements_count=4,
            )
        ],
        total_standing_acres=45.0,
        total_supply_kg=127500.0,
        total_demand_kg=80000.0,
        active_plots_total=18,
        open_requirements_total=4,
    )
    assert summary.total_standing_acres == 45.0
    assert summary.total_supply_kg - summary.total_demand_kg == 47500.0
    assert summary.commodities[0].net_balance_kg == 47500.0
