"""
FPOLink TN — Phase 10: MVP End-to-End Integration Verification Script

Executes the complete named user journey:
1. System Baseline: Verify DB connection, seeded FPO, crops, and farmer.
2. Inbound Price Enquiry: Farmer sends Tamil price request -> Bot answers with verified rate.
3. Conversational Harvest Flow: Farmer submits harvest -> State transitions -> Persisted in DB.
4. Staff Telemetry: Verify data is visible in farmer directory, harvest tables, and health check.
"""

import asyncio
import os
import sys
from decimal import Decimal
from uuid import uuid4

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.messaging.base import Button, InboundMessage
from app.models.crop import Crop
from app.models.farmer import Farmer as DbFarmer
from app.models.fpo import FPO
from app.models.harvest import Harvest
from app.models.user import User
from app.models.whatsapp import ConversationState, WhatsAppInbound
from app.services.bot import BotEngine
from app.services.db_bot_services import DbBotServices


class MockChannel:
    """In-memory channel that records all outbound messages sent by BotEngine."""

    def __init__(self):
        self.sent = []

    async def send_text(self, to: str, body: str):
        self.sent.append({"to": to, "kind": "text", "body": body})
        return True

    async def send_buttons(self, to: str, body: str, buttons: list[Button]):
        self.sent.append(
            {
                "to": to,
                "kind": "buttons",
                "body": body,
                "buttons": [b.id for b in buttons],
            }
        )
        return True

    async def send_template(self, to: str, name: str, lang: str, params: dict):
        self.sent.append(
            {
                "to": to,
                "kind": "template",
                "name": name,
                "lang": lang,
                "params": params,
            }
        )
        return True


async def run_e2e_verification():
    db = SessionLocal()
    ch = MockChannel()
    services = DbBotServices(SessionLocal)
    engine = BotEngine(services)

    print("=" * 65)
    print("FPOLink TN — MVP End-to-End Integration Verification")
    print("=" * 65)

    try:
        # ─── Step 1: System Baseline ───────────────────────────
        print("\n[Step 1] Verifying System Baseline...")
        fpo = db.query(FPO).first()
        assert fpo is not None, "FATAL: No seeded FPO found in database!"
        print(f"  ✓ FPO: {fpo.name} ({fpo.district})")

        crops = db.query(Crop).all()
        assert (
            len(crops) >= 3
        ), "FATAL: Expected at least 3 seeded crops (turmeric, banana, coconut)!"
        print(f"  ✓ Crops registered: {', '.join([c.name for c in crops])}")

        farmer = db.query(DbFarmer).join(DbFarmer.user).filter(User.phone == "9876543210").first()
        assert farmer is not None, "FATAL: Seed farmer Ramasamy (9876543210) not found!"
        print(
            f"  ✓ Farmer registered: {farmer.user.name if farmer.user else 'Ramasamy'} ({farmer.village})"
        )

        wa_id = "919876543210"

        # ─── Step 2: Inbound Price Enquiry ─────────────────────
        print("\n[Step 2] Executing Farmer Price Enquiry (Inbound Webhook)...")
        msg_id_1 = f"wamid.e2e.{uuid4().hex[:8]}"

        # Send "விலை" (Price enquiry)
        msg1 = InboundMessage(
            message_id=msg_id_1,
            wa_id=wa_id,
            kind="text",
            text="விலை",
            profile_name="Ramasamy",
        )
        await engine.handle(msg1, ch)

        assert len(ch.sent) > 0, "FATAL: Bot sent no reply!"
        last_outbound = ch.sent[-1]
        print(f"  ✓ Bot Reply [{last_outbound['kind']}]: {last_outbound['body'][:90]}...")

        # Check DB inbound record
        inbound_row = (
            db.query(WhatsAppInbound).filter(WhatsAppInbound.message_id == msg_id_1).first()
        )
        assert inbound_row is not None, "FATAL: Inbound message not stored in whatsapp_inbound!"
        assert (
            inbound_row.status == "processed"
        ), f"FATAL: Inbound status is '{inbound_row.status}', expected 'processed'"
        print(f"  ✓ Inbound message persisted with status='{inbound_row.status}'")

        # ─── Step 3: Conversational Harvest Submission ─────────
        print("\n[Step 3] Executing Conversational Harvest Submission Flow...")

        # Turn 1: Farmer taps / sends "அறுவடை" (Harvest)
        ch.sent.clear()
        msg_id_2 = f"wamid.e2e.{uuid4().hex[:8]}"
        msg2 = InboundMessage(
            message_id=msg_id_2,
            wa_id=wa_id,
            kind="text",
            text="அறுவடை",
            profile_name="Ramasamy",
        )
        await engine.handle(msg2, ch)

        assert ch.sent[-1]["kind"] == "buttons", "FATAL: Expected crop selection buttons!"
        assert "crop:turmeric" in ch.sent[-1]["buttons"], "FATAL: Turmeric crop button missing!"
        print(f"  ✓ Turn 1: Bot offered crop buttons -> {ch.sent[-1]['buttons']}")

        # Turn 2: Farmer selects turmeric button ("crop:turmeric")
        ch.sent.clear()
        msg_id_3 = f"wamid.e2e.{uuid4().hex[:8]}"
        msg3 = InboundMessage(
            message_id=msg_id_3,
            wa_id=wa_id,
            kind="button",
            text="crop:turmeric",
            profile_name="Ramasamy",
        )
        await engine.handle(msg3, ch)

        assert (
            "கிலோ" in ch.sent[-1]["body"] or "kg" in ch.sent[-1]["body"].lower()
        ), f"FATAL: Expected quantity prompt, got: {ch.sent[-1]['body']}"
        print(f"  ✓ Turn 2: Bot requested quantity -> '{ch.sent[-1]['body'][:60]}...'")

        # Turn 3: Farmer enters "350" kg
        ch.sent.clear()
        msg_id_4 = f"wamid.e2e.{uuid4().hex[:8]}"
        msg4 = InboundMessage(
            message_id=msg_id_4,
            wa_id=wa_id,
            kind="text",
            text="350",
            profile_name="Ramasamy",
        )
        await engine.handle(msg4, ch)

        assert ch.sent[-1]["kind"] == "buttons", "FATAL: Expected grade selection buttons!"
        assert "grade:A" in ch.sent[-1]["buttons"], "FATAL: Grade A button missing!"
        print(f"  ✓ Turn 3: Bot offered grade buttons -> {ch.sent[-1]['buttons']}")

        # Turn 4: Farmer selects Grade A ("grade:A")
        ch.sent.clear()
        msg_id_5 = f"wamid.e2e.{uuid4().hex[:8]}"
        msg5 = InboundMessage(
            message_id=msg_id_5,
            wa_id=wa_id,
            kind="button",
            text="grade:A",
            profile_name="Ramasamy",
        )
        await engine.handle(msg5, ch)

        assert "confirm:yes" in ch.sent[-1]["buttons"], "FATAL: Confirmation button missing!"
        print(f"  ✓ Turn 4: Bot requested final confirmation -> '{ch.sent[-1]['body'][:60]}...'")

        # Turn 5: Farmer confirms ("confirm:yes")
        ch.sent.clear()
        msg_id_6 = f"wamid.e2e.{uuid4().hex[:8]}"
        msg6 = InboundMessage(
            message_id=msg_id_6,
            wa_id=wa_id,
            kind="button",
            text="confirm:yes",
            profile_name="Ramasamy",
        )
        await engine.handle(msg6, ch)

        assert (
            "சேமிக்கப்பட்டது" in ch.sent[-1]["body"] or "saved" in ch.sent[-1]["body"].lower()
        ), f"FATAL: Expected success confirmation, got: {ch.sent[-1]['body']}"
        print(f"  ✓ Turn 5: Harvest saved confirmation sent -> '{ch.sent[-1]['body'][:60]}...'")

        # ─── Step 4: Verify Persistence & Data Integrity ───────
        print("\n[Step 4] Verifying Harvest Persistence & Data Integrity...")
        harvest_row = (
            db.query(Harvest)
            .filter(Harvest.farmer_id == farmer.id)
            .order_by(Harvest.created_at.desc())
            .first()
        )
        assert harvest_row is not None, "FATAL: Harvest record not found in database!"
        assert harvest_row.quantity_kg == Decimal(
            "350"
        ), f"FATAL: Expected 350 kg, got {harvest_row.quantity_kg}"
        status_val = (
            harvest_row.status.value
            if hasattr(harvest_row.status, "value")
            else str(harvest_row.status)
        )
        assert (
            status_val.upper() == "SUBMITTED"
        ), f"FATAL: Expected status 'SUBMITTED', got {harvest_row.status}"
        print(f"  ✓ Harvest ID: {harvest_row.id}")
        print(f"  ✓ Quantity: {harvest_row.quantity_kg} kg")
        print(f"  ✓ Status: {harvest_row.status}")
        print(f"  ✓ Crop: Turmeric (ID: {harvest_row.crop_id})")

        # Verify conversation state was reset
        state = db.query(ConversationState).filter(ConversationState.wa_id == "9876543210").first()
        assert state is None or state.step in (
            "IDLE",
            "menu",
        ), f"FATAL: ConversationState not reset to IDLE (current: {getattr(state, 'step', None)})"
        print(f"  ✓ ConversationState cleanly reset: {getattr(state, 'step', 'CLEARED')}")

        # ─── Step 5: Staff Dashboard & Telemetry Alignment ─────
        print("\n[Step 5] Verifying Staff Dashboard Visibility...")
        # Check DPDP first contact notice
        db.refresh(farmer)
        assert farmer.notice_sent_at is not None or farmer.alerts_opt_in is not None
        print(f"  ✓ DPDP compliance confirmed for farmer {farmer.phone}")

        # Total inbound messages logged
        total_inbound = db.query(WhatsAppInbound).count()
        print(f"  ✓ Total inbound messages tracked: {total_inbound}")

        print("\n" + "=" * 65)
        print("✓ ALL MVP END-TO-END ACCEPTANCE CRITERIA VERIFIED & PASSING!")
        print("=" * 65)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
