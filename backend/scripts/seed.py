"""
FPOLink TN — Database Seed Script (v2)
Uses Argon2 hashing (pwdlib) and normalized markets table.
Idempotent: safe to run multiple times.
"""

import datetime
import os
import sys
from decimal import Decimal

# Add backend directory to path for app imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine
from app.models.base import Base
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.user import User, UserRole
from app.models.variety import Variety
from app.models.weather import WeatherData
from app.services.auth import hash_password


def seed_data():
    """Seed the database with initial reference data."""
    # Ensure all tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("=" * 50)
        print("FPOLink TN — Seeding Database (v2)")
        print("=" * 50)

        # ─── 1. Admin User ────────────────────────────────
        admin_phone = "9999900000"
        admin = db.query(User).filter(User.phone == admin_phone).first()
        if not admin:
            admin = User(
                name="Admin",
                phone=admin_phone,
                email="admin@fpolink.local",
                role=UserRole.ADMIN,
                hashed_password=hash_password("admin123"),
                is_active=True,
                language_preference="en",
                consent_given=True,
                consent_date=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("✓ Admin user created (phone: 9999900000, password: admin123)")
        else:
            print("· Admin user already exists")

        # ─── 2. Crops ─────────────────────────────────────
        crops_data = [
            {"name": "turmeric", "tamil_name": "மஞ்சள்", "unit": "kg", "category": "spice"},
            {"name": "banana", "tamil_name": "வாழைப்பழம்", "unit": "kg", "category": "fruit"},
            {"name": "coconut", "tamil_name": "தேங்காய்", "unit": "unit", "category": "plantation"},
        ]

        crop_objects = {}
        for cd in crops_data:
            crop = db.query(Crop).filter(Crop.name == cd["name"]).first()
            if not crop:
                crop = Crop(**cd)
                db.add(crop)
                db.commit()
                db.refresh(crop)
                print(f"✓ Crop '{cd['name']}' ({cd['tamil_name']}) created")
            else:
                print(f"· Crop '{cd['name']}' already exists")
            crop_objects[cd["name"]] = crop

        # ─── 3. Varieties ─────────────────────────────────
        varieties_data = [
            {"crop": "turmeric", "name": "finger", "tamil_name": "விரல் மஞ்சள்", "grade": "A"},
            {"crop": "turmeric", "name": "bulb", "tamil_name": "கிழங்கு மஞ்சள்", "grade": "B"},
            {"crop": "banana", "name": "Nendran", "tamil_name": "நேந்திரம்", "grade": "A"},
            {"crop": "banana", "name": "Poovan", "tamil_name": "பூவன்", "grade": "A"},
        ]

        for vd in varieties_data:
            crop = crop_objects[vd["crop"]]
            existing = (
                db.query(Variety)
                .filter(Variety.crop_id == crop.id, Variety.name == vd["name"])
                .first()
            )
            if not existing:
                variety = Variety(
                    crop_id=crop.id,
                    name=vd["name"],
                    tamil_name=vd["tamil_name"],
                    grade=vd["grade"],
                )
                db.add(variety)
                db.commit()
                print(f"✓ Variety '{vd['name']}' for {vd['crop']} created")
            else:
                print(f"· Variety '{vd['name']}' already exists")

        # ─── 4. Markets ───────────────────────────────────
        markets_data = [
            {
                "name": "Erode Mandi",
                "district": "Erode",
                "state": "Tamil Nadu",
                "latitude": 11.3410,
                "longitude": 77.7172,
                "market_type": "mandi",
            },
            {
                "name": "Gobichettipalayam Mandi",
                "district": "Erode",
                "state": "Tamil Nadu",
                "latitude": 11.4539,
                "longitude": 77.4380,
                "market_type": "mandi",
            },
            {
                "name": "Erode Uzhavar Sandhai",
                "district": "Erode",
                "state": "Tamil Nadu",
                "latitude": 11.3410,
                "longitude": 77.7172,
                "market_type": "uzhavar_sandhai",
            },
        ]

        market_objects = {}
        for md in markets_data:
            market = db.query(Market).filter(Market.name == md["name"]).first()
            if not market:
                market = Market(**md)
                db.add(market)
                db.commit()
                db.refresh(market)
                print(f"✓ Market '{md['name']}' created")
            else:
                print(f"· Market '{md['name']}' already exists")
            market_objects[md["name"]] = market

        # ─── 5. FPO ───────────────────────────────────────
        fpo_reg = "FPO-TN-ERD-001"
        fpo = db.query(FPO).filter(FPO.registration_number == fpo_reg).first()
        if not fpo:
            fpo = FPO(
                name="Erode Farmers Collective",
                registration_number=fpo_reg,
                district="Erode",
                village="Perundurai",
                state="Tamil Nadu",
                contact_phone="9999900001",
            )
            db.add(fpo)
            db.commit()
            db.refresh(fpo)
            print("✓ FPO 'Erode Farmers Collective' created")
        else:
            print("· FPO already exists")

        # ─── 6. Farmer Users + Farmer Records ─────────────
        farmers_data = [
            {
                "name": "Ramasamy",
                "phone": "9876543210",
                "village": "Perundurai",
                "taluk": "Perundurai",
                "farm_area_acres": 2.5,
            },
            {
                "name": "Kuppusamy",
                "phone": "9876543211",
                "village": "Gobichettipalayam",
                "taluk": "Gobichettipalayam",
                "farm_area_acres": 1.5,
            },
        ]

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
                )
                db.add(farmer_user)
                db.commit()
                db.refresh(farmer_user)

                farmer = Farmer(
                    user_id=farmer_user.id,
                    fpo_id=fpo.id,
                    village=fd["village"],
                    taluk=fd["taluk"],
                    district="Erode",
                    farm_area_acres=fd["farm_area_acres"],
                )
                db.add(farmer)
                db.commit()
                print(
                    f"✓ Farmer '{fd['name']}' created (phone: {fd['phone']}, password: farmer123)"
                )
            else:
                print(f"· Farmer '{fd['name']}' already exists")

        # ─── 7. Market Prices (Turmeric, Erode, last 5 days) ──
        turmeric = crop_objects.get("turmeric")
        erode_mandi = market_objects.get("Erode Mandi")
        if turmeric and erode_mandi:
            today = datetime.date.today()
            price_data = [
                {"days_ago": 0, "modal": Decimal("150.00")},
                {"days_ago": 1, "modal": Decimal("148.00")},
                {"days_ago": 2, "modal": Decimal("144.00")},
                {"days_ago": 3, "modal": Decimal("145.00")},
                {"days_ago": 4, "modal": Decimal("142.00")},
            ]

            for pd_item in price_data:
                price_date = today - datetime.timedelta(days=pd_item["days_ago"])
                existing = (
                    db.query(MarketPrice)
                    .filter(
                        MarketPrice.crop_id == turmeric.id,
                        MarketPrice.market_id == erode_mandi.id,
                        MarketPrice.price_date == price_date,
                        MarketPrice.source == "seed",
                    )
                    .first()
                )
                if not existing:
                    modal = pd_item["modal"]
                    mp = MarketPrice(
                        crop_id=turmeric.id,
                        market_id=erode_mandi.id,
                        district="Erode",
                        min_price=modal - Decimal("10.00"),
                        max_price=modal + Decimal("10.00"),
                        modal_price=modal,
                        raw_price=modal * Decimal("100"),  # Rs/quintal
                        raw_unit="quintal",
                        arrival_quantity=1200.0 + (pd_item["days_ago"] * 50),
                        price_date=price_date,
                        source="seed",
                    )
                    db.add(mp)
                    db.commit()
                    print(f"✓ Turmeric price for {price_date}: ₹{modal}/kg")
                else:
                    print(f"· Turmeric price for {price_date} already exists")

        # ─── 8. Weather Data (Erode, today + tomorrow) ────
        today = datetime.date.today()
        weather_entries = [
            {
                "district": "Erode",
                "date": today,
                "temperature_max": 33.5,
                "temperature_min": 24.2,
                "rainfall_mm": 0.0,
                "humidity": 65.0,
                "wind_speed": 8.5,
                "source": "seed",
            },
            {
                "district": "Erode",
                "date": today + datetime.timedelta(days=1),
                "temperature_max": 31.0,
                "temperature_min": 23.8,
                "rainfall_mm": 5.2,
                "humidity": 78.0,
                "wind_speed": 12.0,
                "source": "seed",
            },
        ]

        for wd in weather_entries:
            existing = (
                db.query(WeatherData)
                .filter(
                    WeatherData.district == wd["district"],
                    WeatherData.date == wd["date"],
                )
                .first()
            )
            if not existing:
                w = WeatherData(**wd)
                db.add(w)
                db.commit()
                print(
                    f"✓ Weather for Erode on {wd['date']}: {wd['temperature_max']}°C, {wd['rainfall_mm']}mm rain"
                )
            else:
                print(f"· Weather data for {wd['date']} already exists")

        print()
        print("=" * 50)
        print("✓ Seeding completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
