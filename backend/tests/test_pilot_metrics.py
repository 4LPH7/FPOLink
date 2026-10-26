"""Pilot metrics: per-FPO weekly use, advice shown and harvest pooled."""

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.messaging.base import InboundMessage
from app.models.bot_activity import BotActivity
from app.models.crop import Crop
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest, HarvestGrade
from app.models.user import User, UserRole
from app.services.bot import BotEngine
from app.services.bot import Farmer as BotFarmer
from app.services.db_bot_services import DbBotServices

client = TestClient(app)


def make_farmer(db, fpo, phone):
    user = User(name="F", phone=phone, hashed_password="x", role=UserRole.FARMER, is_active=True)
    db.add(user)
    db.flush()
    farmer = Farmer(
        user_id=user.id, fpo_id=fpo.id, phone=phone, village="V", taluk="T", farm_area_acres=1
    )
    db.add(farmer)
    db.flush()
    return farmer


def test_report_counts_use_advice_and_harvest_per_fpo(db, admin_headers):
    tag = uuid.uuid4().hex[:8]
    fpo = FPO(
        name=f"Pilot {tag}",
        registration_number=tag,
        district="Erode",
        village="V",
        contact_phone="9000000000",
    )
    db.add(fpo)
    db.flush()
    active = make_farmer(db, fpo, f"9{uuid.uuid4().int % 10**9:09d}")
    make_farmer(db, fpo, f"9{uuid.uuid4().int % 10**9:09d}")  # registered, never used it
    crop = Crop(name=f"c{tag}", unit="kg")
    db.add(crop)
    db.flush()
    now = datetime.now(timezone.utc)
    db.add_all(
        [
            BotActivity(farmer_id=active.id, intent="price", advice_shown=True, created_at=now),
            BotActivity(farmer_id=active.id, intent="price", advice_shown=False, created_at=now),
            BotActivity(  # last month: outside the 7-day window
                farmer_id=active.id, intent="price", created_at=now - timedelta(days=30)
            ),
            Harvest(
                farmer_id=active.id,
                crop_id=crop.id,
                quantity_kg=250,
                grade=HarvestGrade.A,
                harvest_date=date.today(),
            ),
        ]
    )
    db.commit()

    resp = client.get(
        "/api/v1/pilot/metrics", params={"fpo_id": str(fpo.id)}, headers=admin_headers
    )

    assert resp.status_code == 200, resp.text
    row = resp.json()["fpos"][0]
    assert row["farmers_registered"] == 2
    assert row["active_farmers"] == 1
    assert row["price_queries"] == 2
    assert row["advice_shown"] == 1
    assert row["harvests_reported"] == 1
    assert row["harvest_kg"] == 250


def test_report_needs_admin(db):
    assert client.get("/api/v1/pilot/metrics").status_code in (401, 403)


def test_bot_records_what_a_farmer_asked_for(db):
    tag = uuid.uuid4().hex[:8]
    fpo = FPO(
        name=f"B {tag}", registration_number=tag, district="Erode", village="V",
        contact_phone="9000000000",
    )  # fmt: skip
    db.add(fpo)
    db.flush()
    farmer = make_farmer(db, fpo, f"9{uuid.uuid4().int % 10**9:09d}")
    db.commit()

    class Svc(DbBotServices):
        async def find_farmer(self, phone10):
            return BotFarmer(
                str(farmer.id), "F", "Erode", "en", notice_sent_at=datetime.now(timezone.utc)
            )

        async def first_time(self, message_id):
            return True

        async def get_state(self, wa_id):
            return None

        async def mark_processed(self, message_id):
            pass

        async def latest_price(self, crop, district=None):
            return None

    from contextlib import nullcontext

    svc = Svc(db_factory=lambda: nullcontext(db))
    asyncio.run(
        BotEngine(svc).handle(InboundMessage("m1", "919000000001", "text", "turmeric price"), _Ch())
    )

    rows = db.query(BotActivity).filter(BotActivity.farmer_id == farmer.id).all()
    assert [(r.intent, r.advice_shown) for r in rows] == [("price", False)]


class _Ch:
    async def send_text(self, to, body):
        pass

    async def send_buttons(self, to, body, buttons):
        pass
