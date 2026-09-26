"""
Seed Supply and Demand Network for Erode Pilot (Phase 13 / v0.8)
Populates:
1. Multi-plot discrete acreage for Erode Farmers Collective (14 plots across 6 farmers)
2. 4 Commercial Buyers (Processors, Retailers, Traders)
3. 5 Procurement Requirements across Turmeric, Banana, and Coconut
4. Sample suggested and confirmed Supply Matches for verification
"""

import datetime
import os
import sys
from decimal import Decimal

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.geography import District, Taluk
from app.models.harvest import HarvestGrade
from app.models.supply_match import SupplyMatch
from app.models.user import User, UserRole
from app.models.variety import Variety
from app.services.auth import hash_password
from app.services.yield_estimator import estimate_crop_yield


def seed_supply_demand():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("=" * 60)
        print("FPOLink TN — Seeding Supply & Demand Network (v0.8)")
        print("=" * 60)

        # 1. Admin user & FPO lookup
        admin = db.query(User).filter(User.phone == "9999900000").first()
        fpo = db.query(FPO).filter(FPO.registration_number == "FPO-TN-ERD-001").first()
        if not fpo:
            fpo = FPO(
                name="Erode Farmers Collective",
                registration_number="FPO-TN-ERD-001",
                district="Erode",
                village="Perundurai",
                state="Tamil Nadu",
                contact_phone="9999900001",
            )
            db.add(fpo)
            db.commit()
            db.refresh(fpo)
            print("✓ Created FPO 'Erode Farmers Collective'")
        else:
            print(f"· Found FPO: {fpo.name} ({fpo.id})")

        # 2. Geography lookups for Erode
        erode_district = db.query(District).filter(District.name.ilike("%Erode%")).first()
        taluks = {}
        if erode_district:
            taluks = {
                t.name.lower(): t
                for t in db.query(Taluk).filter(Taluk.district_id == erode_district.id).all()
            }

        # 3. Crops & Varieties lookups
        crops = {c.name.lower(): c for c in db.query(Crop).all()}
        varieties = {}
        for v in db.query(Variety).all():
            varieties[(v.crop_id, v.name.lower())] = v

        # 4. Farmers (Ensure 6 farmers under this FPO)
        farmers_data = [
            {
                "name": "Ramasamy",
                "phone": "9876543210",
                "village": "Perundurai",
                "taluk": "Perundurai",
                "area": 5.5,
            },
            {
                "name": "Marimuthu",
                "phone": "9876543211",
                "village": "Perundurai",
                "taluk": "Perundurai",
                "area": 5.5,
            },
            {
                "name": "Selvaraj K",
                "phone": "9876543212",
                "village": "Modakkurichi",
                "taluk": "Modakkurichi",
                "area": 5.5,
            },
            {
                "name": "Murugesan P",
                "phone": "9876543213",
                "village": "Kodumudi",
                "taluk": "Kodumudi",
                "area": 6.5,
            },
            {
                "name": "Thangavel M",
                "phone": "9876543214",
                "village": "Bhavani",
                "taluk": "Bhavani",
                "area": 7.0,
            },
            {
                "name": "Palanisamy S",
                "phone": "9876543215",
                "village": "Perundurai",
                "taluk": "Perundurai",
                "area": 9.5,
            },
        ]

        farmer_objs = {}
        for fd in farmers_data:
            farmer_user = db.query(User).filter(User.phone == fd["phone"]).first()
            if not farmer_user:
                farmer_user = User(
                    name=fd["name"],
                    phone=fd["phone"],
                    role=UserRole.FARMER,
                    hashed_password=hash_password("farmer123"),
                    is_active=True,
                    language_preference="ta",
                    consent_given=True,
                    consent_date=datetime.datetime.now(datetime.timezone.utc),
                    fpo_id=fpo.id,
                )
                db.add(farmer_user)
                db.commit()
                db.refresh(farmer_user)

            farmer_profile = db.query(Farmer).filter(Farmer.user_id == farmer_user.id).first()
            taluk_obj = taluks.get(fd["taluk"].lower())
            if not farmer_profile:
                farmer_profile = Farmer(
                    user_id=farmer_user.id,
                    fpo_id=fpo.id,
                    phone=fd["phone"],
                    village=fd["village"],
                    taluk=fd["taluk"],
                    district="Erode",
                    district_id=erode_district.id if erode_district else None,
                    taluk_id=taluk_obj.id if taluk_obj else None,
                    farm_area_acres=fd["area"],
                    lang="ta",
                    alerts_opt_in=True,
                )
                db.add(farmer_profile)
                db.commit()
                db.refresh(farmer_profile)
                print(f"✓ Created Farmer profile for {fd['name']} ({fd['phone']})")
            else:
                farmer_objs[fd["phone"]] = farmer_profile
            farmer_objs[fd["phone"]] = farmer_profile

        # 5. Multi-Plot Discrete Farm Acreage (14 plots)
        today = datetime.date.today()
        plots_data = [
            # Ramasamy
            {
                "farmer_phone": "9876543210",
                "plot_name": "Kattu Valavu Turmeric",
                "crop": "turmeric",
                "area_acres": 2.5,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "red loam",
                "irrigation_type": "drip",
                "sowing_date": today - datetime.timedelta(days=180),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543210",
                "plot_name": "Kinaru Thottam Banana",
                "crop": "banana",
                "area_acres": 3.0,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "alluvial",
                "irrigation_type": "borewell",
                "sowing_date": today - datetime.timedelta(days=300),
                "status": "ready_for_harvest",
            },
            # Marimuthu
            {
                "farmer_phone": "9876543211",
                "plot_name": "Aalamarathu Kadu Turmeric",
                "crop": "turmeric",
                "area_acres": 1.5,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "clay loam",
                "irrigation_type": "canal",
                "sowing_date": today - datetime.timedelta(days=210),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543211",
                "plot_name": "Thennai Thoppu Coconut",
                "crop": "coconut",
                "area_acres": 4.0,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "red loam",
                "irrigation_type": "drip",
                "sowing_date": today - datetime.timedelta(days=730),
                "status": "growing",
            },
            # Selvaraj
            {
                "farmer_phone": "9876543212",
                "plot_name": "Modakkurichi Canal Banana",
                "crop": "banana",
                "area_acres": 2.0,
                "village": "Modakkurichi",
                "taluk": "Modakkurichi",
                "soil_type": "alluvial",
                "irrigation_type": "canal",
                "sowing_date": today - datetime.timedelta(days=240),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543212",
                "plot_name": "Vaikkal Medu Turmeric",
                "crop": "turmeric",
                "area_acres": 3.5,
                "village": "Modakkurichi",
                "taluk": "Modakkurichi",
                "soil_type": "red loam",
                "irrigation_type": "drip",
                "sowing_date": today - datetime.timedelta(days=150),
                "status": "growing",
            },
            # Murugesan
            {
                "farmer_phone": "9876543213",
                "plot_name": "Kodumudi Kaveri Bank Banana",
                "crop": "banana",
                "area_acres": 4.0,
                "village": "Kodumudi",
                "taluk": "Kodumudi",
                "soil_type": "alluvial",
                "irrigation_type": "canal",
                "sowing_date": today - datetime.timedelta(days=310),
                "status": "ready_for_harvest",
            },
            {
                "farmer_phone": "9876543213",
                "plot_name": "Ayyanar Kovil Paddy",
                "crop": "paddy",
                "area_acres": 2.5,
                "village": "Kodumudi",
                "taluk": "Kodumudi",
                "soil_type": "clay",
                "irrigation_type": "canal",
                "sowing_date": today - datetime.timedelta(days=60),
                "status": "growing",
            },
            # Thangavel
            {
                "farmer_phone": "9876543214",
                "plot_name": "Bhavani Riverbed Turmeric",
                "crop": "turmeric",
                "area_acres": 2.0,
                "village": "Bhavani",
                "taluk": "Bhavani",
                "soil_type": "alluvial",
                "irrigation_type": "borewell",
                "sowing_date": today - datetime.timedelta(days=170),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543214",
                "plot_name": "Mettu Thottam Coconut",
                "crop": "coconut",
                "area_acres": 3.0,
                "village": "Bhavani",
                "taluk": "Bhavani",
                "soil_type": "sandy loam",
                "irrigation_type": "borewell",
                "sowing_date": today - datetime.timedelta(days=1000),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543214",
                "plot_name": "Puthu Nanjai Paddy",
                "crop": "paddy",
                "area_acres": 3.0,
                "village": "Bhavani",
                "taluk": "Bhavani",
                "soil_type": "alluvial",
                "irrigation_type": "canal",
                "sowing_date": today - datetime.timedelta(days=30),
                "status": "growing",
            },
            # Palanisamy
            {
                "farmer_phone": "9876543215",
                "plot_name": "Perundurai Karisal Paddy",
                "crop": "paddy",
                "area_acres": 2.0,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "clay loam",
                "irrigation_type": "borewell",
                "sowing_date": today - datetime.timedelta(days=60),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543215",
                "plot_name": "Semman Kadu Coconut",
                "crop": "coconut",
                "area_acres": 5.0,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "red loam",
                "irrigation_type": "drip",
                "sowing_date": today - datetime.timedelta(days=1200),
                "status": "growing",
            },
            {
                "farmer_phone": "9876543215",
                "plot_name": "Veeduthi Banana",
                "crop": "banana",
                "area_acres": 2.5,
                "village": "Perundurai",
                "taluk": "Perundurai",
                "soil_type": "alluvial",
                "irrigation_type": "borewell",
                "sowing_date": today - datetime.timedelta(days=220),
                "status": "growing",
            },
        ]

        farm_objects = {}
        for pd in plots_data:
            farmer = farmer_objs[pd["farmer_phone"]]
            crop = crops.get(pd["crop"])
            if not crop:
                continue

            existing_plot = (
                db.query(Farm)
                .filter(Farm.farmer_id == farmer.id, Farm.plot_name == pd["plot_name"])
                .first()
            )

            # Estimate yields using deterministic rule-based benchmark
            est = estimate_crop_yield(
                crop_name=crop.name,
                area_acres=pd["area_acres"],
                soil_type=pd["soil_type"],
                irrigation_type=pd["irrigation_type"],
                sowing_date=pd["sowing_date"],
            )

            taluk_obj = taluks.get(pd["taluk"].lower())

            if not existing_plot:
                plot = Farm(
                    farmer_id=farmer.id,
                    crop_id=crop.id,
                    plot_name=pd["plot_name"],
                    area_acres=pd["area_acres"],
                    village=pd["village"],
                    soil_type=pd["soil_type"],
                    irrigation_type=pd["irrigation_type"],
                    sowing_date=pd["sowing_date"],
                    expected_harvest_date=est.get("estimated_harvest_window_start"),
                    expected_yield_kg=est.get("estimated_yield_kg"),
                    status=pd["status"],
                    district_id=erode_district.id if erode_district else None,
                    taluk_id=taluk_obj.id if taluk_obj else None,
                )
                db.add(plot)
                db.commit()
                db.refresh(plot)
                print(
                    f"✓ Created plot '{plot.plot_name}' ({crop.name}, {plot.area_acres} ac, est: {plot.expected_yield_kg:.0f} kg)"
                )
                farm_objects[pd["plot_name"]] = plot
            else:
                farm_objects[pd["plot_name"]] = existing_plot

        # 6. Commercial Buyers (4 entities)
        buyers_data = [
            {
                "company_name": "ITC Spices Division",
                "buyer_type": "processor",
                "contact_name": "Senthil Kumar",
                "contact_phone": "9842100001",
                "contact_email": "procurement@itcspices.example.com",
                "location": "SIPCOT Industrial Complex, Perundurai",
                "district": "Erode",
                "gstin": "33AAACI1234A1Z1",
                "verified": True,
            },
            {
                "company_name": "Aachi Masala Foods Pvt Ltd",
                "buyer_type": "processor",
                "contact_name": "Muruganandam",
                "contact_phone": "9842100002",
                "contact_email": "supply@aachimasala.example.com",
                "location": "Bypass Road, Erode",
                "district": "Erode",
                "gstin": "33AABCA5678B1Z2",
                "verified": True,
            },
            {
                "company_name": "Nilgiris Supermarket Procurement",
                "buyer_type": "retailer",
                "contact_name": "Prakash R",
                "contact_phone": "9842100003",
                "contact_email": "fresh@nilgiris.example.com",
                "location": "Avinashi Road, Coimbatore",
                "district": "Coimbatore",
                "gstin": "33AACCN9012C1Z3",
                "verified": True,
            },
            {
                "company_name": "Erode Regulated Market Traders Association",
                "buyer_type": "trader",
                "contact_name": "Kandasamy V",
                "contact_phone": "9842100004",
                "contact_email": "traders@erodemarket.example.com",
                "location": "Perundurai Road, Erode",
                "district": "Erode",
                "gstin": "33AADDE3456D1Z4",
                "verified": True,
            },
        ]

        buyer_objs = {}
        for bd in buyers_data:
            existing_buyer = (
                db.query(Buyer).filter(Buyer.company_name == bd["company_name"]).first()
            )
            if not existing_buyer:
                buyer = Buyer(
                    company_name=bd["company_name"],
                    buyer_type=bd["buyer_type"],
                    contact_name=bd["contact_name"],
                    contact_phone=bd["contact_phone"],
                    contact_email=bd["contact_email"],
                    location=bd["location"],
                    district=bd["district"],
                    district_id=erode_district.id
                    if (erode_district and bd["district"] == "Erode")
                    else None,
                    fpo_id=fpo.id,
                    gstin=bd["gstin"],
                    verified=bd["verified"],
                    created_by_user_id=admin.id if admin else None,
                )
                db.add(buyer)
                db.commit()
                db.refresh(buyer)
                print(f"✓ Created Buyer: {buyer.company_name} ({buyer.buyer_type})")
                buyer_objs[bd["company_name"]] = buyer
            else:
                buyer_objs[bd["company_name"]] = existing_buyer

        # 7. Procurement Requirements (5 active requirements)
        turmeric_crop = crops.get("turmeric")
        banana_crop = crops.get("banana")
        coconut_crop = crops.get("coconut")

        # Varieties
        turmeric_finger = varieties.get((turmeric_crop.id, "finger")) if turmeric_crop else None
        turmeric_bulb = varieties.get((turmeric_crop.id, "bulb")) if turmeric_crop else None
        banana_nendran = varieties.get((banana_crop.id, "nendran")) if banana_crop else None
        banana_poovan = varieties.get((banana_crop.id, "poovan")) if banana_crop else None

        reqs_data = [
            {
                "buyer": "ITC Spices Division",
                "crop": turmeric_crop,
                "variety": turmeric_finger,
                "quantity_kg": 5000.0,
                "min_grade": HarvestGrade.A,
                "required_date": today + datetime.timedelta(days=30),
                "delivery_window_days": 10,
                "max_price_per_kg": Decimal("145.00"),
                "delivery_location": "ITC Processing Unit, SIPCOT, Perundurai",
                "notes": "Moisture max 10%, curcumin content > 3.5%",
            },
            {
                "buyer": "Aachi Masala Foods Pvt Ltd",
                "crop": turmeric_crop,
                "variety": turmeric_bulb,
                "quantity_kg": 8000.0,
                "min_grade": HarvestGrade.B,
                "required_date": today + datetime.timedelta(days=45),
                "delivery_window_days": 15,
                "max_price_per_kg": Decimal("130.00"),
                "delivery_location": "Aachi Depot, Erode",
                "notes": "Well-dried Salem/Erode local bulb turmeric",
            },
            {
                "buyer": "Nilgiris Supermarket Procurement",
                "crop": banana_crop,
                "variety": banana_nendran,
                "quantity_kg": 2500.0,
                "min_grade": HarvestGrade.A,
                "required_date": today + datetime.timedelta(days=14),
                "delivery_window_days": 5,
                "max_price_per_kg": Decimal("48.00"),
                "delivery_location": "Nilgiris Regional DC, Coimbatore",
                "notes": "Uniform bunch size, zero blemish for fresh retail",
            },
            {
                "buyer": "Nilgiris Supermarket Procurement",
                "crop": banana_crop,
                "variety": banana_poovan,
                "quantity_kg": 3000.0,
                "min_grade": HarvestGrade.A,
                "required_date": today + datetime.timedelta(days=20),
                "delivery_window_days": 7,
                "max_price_per_kg": Decimal("35.00"),
                "delivery_location": "Erode Collection Hub",
                "notes": "Semi-ripe bunches",
            },
            {
                "buyer": "Erode Regulated Market Traders Association",
                "crop": coconut_crop,
                "variety": None,
                "quantity_kg": 4000.0,
                "min_grade": HarvestGrade.A,
                "required_date": today + datetime.timedelta(days=25),
                "delivery_window_days": 7,
                "max_price_per_kg": Decimal("32.00"),
                "delivery_location": "Erode Mandi Yard",
                "notes": "Matured dehusked coconuts, minimum 450g per nut",
            },
        ]

        req_objs = []
        for rd in reqs_data:
            buyer = buyer_objs.get(rd["buyer"])
            if not buyer or not rd["crop"]:
                continue

            existing_req = (
                db.query(BuyerRequirement)
                .filter(
                    BuyerRequirement.buyer_id == buyer.id,
                    BuyerRequirement.crop_id == rd["crop"].id,
                    BuyerRequirement.required_date == rd["required_date"],
                )
                .first()
            )
            if not existing_req:
                req = BuyerRequirement(
                    buyer_id=buyer.id,
                    fpo_id=fpo.id,
                    crop_id=rd["crop"].id,
                    variety_id=rd["variety"].id if rd["variety"] else None,
                    district_id=erode_district.id if erode_district else None,
                    quantity_kg=rd["quantity_kg"],
                    min_grade=rd["min_grade"],
                    required_date=rd["required_date"],
                    delivery_window_days=rd["delivery_window_days"],
                    max_price_per_kg=rd["max_price_per_kg"],
                    delivery_location=rd["delivery_location"],
                    status="open",
                    notes=rd["notes"],
                    created_by_user_id=admin.id if admin else None,
                )
                db.add(req)
                db.commit()
                db.refresh(req)
                print(
                    f"✓ Created Requirement: {buyer.company_name} - {rd['crop'].name} ({req.quantity_kg:.0f} kg)"
                )
                req_objs.append(req)
            else:
                req_objs.append(existing_req)

        # 8. Sample Supply Matches (1 confirmed by staff, 1 suggested by system)
        if req_objs and farm_objects:
            # Match 1: Confirmed match on ITC Spices Turmeric Requirement
            itc_req = req_objs[0]  # ITC Spices Turmeric
            turmeric_plot = farm_objects.get("Kattu Valavu Turmeric")
            if itc_req and turmeric_plot:
                existing_match = (
                    db.query(SupplyMatch)
                    .filter(
                        SupplyMatch.buyer_requirement_id == itc_req.id,
                        SupplyMatch.farm_id == turmeric_plot.id,
                    )
                    .first()
                )
                if not existing_match:
                    match1 = SupplyMatch(
                        buyer_requirement_id=itc_req.id,
                        farm_id=turmeric_plot.id,
                        fpo_id=fpo.id,
                        matched_quantity_kg=turmeric_plot.expected_yield_kg or 5000.0,
                        offered_price_per_kg=Decimal("142.00"),
                        match_score=0.92,
                        match_breakdown={
                            "crop_match": 1.0,
                            "proximity_score": 0.95,
                            "quantity_fulfillment": 0.90,
                            "timeline_feasibility": 0.85,
                            "grade_confidence": 0.95,
                        },
                        status="confirmed_by_staff",
                        staff_notes="Verified high-grade rhizomes with farmer Ramasamy; ready for scheduled harvest.",
                        confirmed_by_id=admin.id if admin else None,
                        confirmed_at=datetime.datetime.now(datetime.timezone.utc),
                    )
                    db.add(match1)
                    db.commit()
                    print(f"✓ Created Confirmed Match: ITC Spices <-> {turmeric_plot.plot_name}")

            # Match 2: Suggested match on Nilgiris Banana Requirement
            banana_req = next((r for r in req_objs if r.crop_id == banana_crop.id), None)
            banana_plot = farm_objects.get("Kodumudi Kaveri Bank Banana")
            if banana_req and banana_plot:
                existing_match2 = (
                    db.query(SupplyMatch)
                    .filter(
                        SupplyMatch.buyer_requirement_id == banana_req.id,
                        SupplyMatch.farm_id == banana_plot.id,
                    )
                    .first()
                )
                if not existing_match2:
                    match2 = SupplyMatch(
                        buyer_requirement_id=banana_req.id,
                        farm_id=banana_plot.id,
                        fpo_id=fpo.id,
                        matched_quantity_kg=min(2500.0, banana_plot.expected_yield_kg or 2500.0),
                        offered_price_per_kg=Decimal("46.00"),
                        match_score=0.88,
                        match_breakdown={
                            "crop_match": 1.0,
                            "proximity_score": 0.80,
                            "quantity_fulfillment": 0.95,
                            "timeline_feasibility": 0.90,
                            "grade_confidence": 0.85,
                        },
                        status="suggested",
                        staff_notes="Automated algorithm candidate; harvest is mature in Kaveri riverbank plot.",
                    )
                    db.add(match2)
                    db.commit()
                    print(f"✓ Created Suggested Match: Nilgiris <-> {banana_plot.plot_name}")

        print("=" * 60)
        print("✓ Supply & Demand pilot seeding complete!")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"✗ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_supply_demand()
