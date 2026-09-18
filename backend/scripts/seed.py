"""
FPOLink TN — Database Seed Script
Seeds initial reference data for development and demo purposes.
Idempotent: safe to run multiple times.
"""

import os
import sys
import uuid
import datetime

# Add backend directory to path for app imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from passlib.context import CryptContext
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.fpo import FPO
from app.models.farmer import Farmer
from app.models.market_price import MarketPrice
from app.models.weather import WeatherData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def seed_data():
    """Seed the database with initial reference data."""
    # Ensure all tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("=" * 50)
        print("FPOLink TN — Seeding Database")
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

        # ─── 3. FPO ───────────────────────────────────────
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

        # ─── 4. Farmer Users + Farmer Records ─────────────
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
                # Create the user account
                farmer_user = User(
                    name=fd["name"],
                    phone=fd["phone"],
                    role=UserRole.FARMER,
                    hashed_password=hash_password("farmer123"),
                    is_active=True,
                    language_preference="ta",
                )
                db.add(farmer_user)
                db.commit()
                db.refresh(farmer_user)

                # Create the farmer profile
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
                print(f"✓ Farmer '{fd['name']}' created (phone: {fd['phone']}, password: farmer123)")
            else:
                print(f"· Farmer '{fd['name']}' already exists")

        # ─── 5. Market Prices (Turmeric, Erode, last 5 days) ──
        turmeric = crop_objects.get("turmeric")
        if turmeric:
            today = datetime.date.today()
            price_data = [
                {"days_ago": 0, "modal": 150.0},
                {"days_ago": 1, "modal": 148.0},
                {"days_ago": 2, "modal": 144.0},
                {"days_ago": 3, "modal": 145.0},
                {"days_ago": 4, "modal": 142.0},
            ]

            for pd_item in price_data:
                price_date = today - datetime.timedelta(days=pd_item["days_ago"])
                existing = (
                    db.query(MarketPrice)
                    .filter(
                        MarketPrice.crop_id == turmeric.id,
                        MarketPrice.market_name == "Erode",
                        MarketPrice.price_date == price_date,
                        MarketPrice.source == "seed",
                    )
                    .first()
                )
                if not existing:
                    modal = pd_item["modal"]
                    mp = MarketPrice(
                        crop_id=turmeric.id,
                        market_name="Erode",
                        district="Erode",
                        min_price=modal - 10,
                        max_price=modal + 10,
                        modal_price=modal,
                        arrival_quantity=1200.0 + (pd_item["days_ago"] * 50),
                        price_date=price_date,
                        source="seed",
                    )
                    db.add(mp)
                    db.commit()
                    print(f"✓ Turmeric price for {price_date}: ₹{modal}/kg")
                else:
                    print(f"· Turmeric price for {price_date} already exists")

        # ─── 6. Weather Data (Erode, today + tomorrow) ────
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
                print(f"✓ Weather data for Erode on {wd['date']}: {wd['temperature_max']}°C, {wd['rainfall_mm']}mm rain")
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
