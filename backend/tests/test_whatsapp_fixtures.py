"""Parametrized contract tests verifying WhatsApp Cloud API fixtures against parser (T0.3)."""

import json
from pathlib import Path

from app.messaging.whatsapp_cloud import parse_status_updates, parse_webhook

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "whatsapp"


def load_fixture(filename: str) -> dict:
    """Load JSON fixture file."""
    path = FIXTURES_DIR / filename
    assert path.exists(), f"Fixture file not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_text_en_fixture():
    """Verify parsing of English text message 'PRICE'."""
    data = load_fixture("text_en.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919000000001"
    assert m.profile_name == "Ravi Kumar"
    assert m.kind == "text"
    assert m.text == "PRICE"
    assert m.message_id.startswith("wamid.")


def test_text_ta_fixture():
    """Verify parsing of Tamil text message 'விலை'."""
    data = load_fixture("text_ta.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919876543210"
    assert m.profile_name == "முத்துசாமி"
    assert m.kind == "text"
    assert m.text == "விலை"


def test_button_price_fixture():
    """Verify parsing of interactive button tap for b_price."""
    data = load_fixture("button_price.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919876543210"
    assert m.kind == "button"
    assert m.text == "b_price"


def test_button_harvest_fixture():
    """Verify parsing of interactive button tap for b_harvest."""
    data = load_fixture("button_harvest.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919876543210"
    assert m.kind == "button"
    assert m.text == "b_harvest"


def test_unsupported_voice_fixture():
    """Verify that incoming voice/audio notes are parsed as voice type without crashing."""
    data = load_fixture("unsupported_voice.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919876543210"
    assert m.kind == "voice"
    assert m.text == ""


def test_unsupported_image_fixture():
    """Verify that incoming image attachments are parsed as image type without crashing."""
    data = load_fixture("unsupported_image.json")
    messages = parse_webhook(data)
    assert len(messages) == 1
    m = messages[0]
    assert m.wa_id == "919876543210"
    assert m.kind == "image"
    assert m.text == ""


def test_status_delivered_fixture():
    """Verify delivery receipt status webhook parsing."""
    data = load_fixture("status_delivered.json")
    # Message parsing should yield empty list
    messages = parse_webhook(data)
    assert len(messages) == 0

    # Status update parsing should extract delivery update
    statuses = parse_status_updates(data)
    assert len(statuses) == 1
    s = statuses[0]
    assert s.recipient_id == "919876543210"
    assert s.status == "delivered"
    assert s.meta_message_id.startswith("wamid.")


def test_status_read_fixture():
    """Verify read receipt status webhook parsing."""
    data = load_fixture("status_read.json")
    messages = parse_webhook(data)
    assert len(messages) == 0

    statuses = parse_status_updates(data)
    assert len(statuses) == 1
    s = statuses[0]
    assert s.recipient_id == "919876543210"
    assert s.status == "read"


def test_status_failed_fixture():
    """Verify delivery failure callback parsing and error extraction."""
    data = load_fixture("status_failed.json")
    messages = parse_webhook(data)
    assert len(messages) == 0

    statuses = parse_status_updates(data)
    assert len(statuses) == 1
    s = statuses[0]
    assert s.recipient_id == "919876543210"
    assert s.status == "failed"
    assert s.errors is not None
    assert len(s.errors) == 1
    assert s.errors[0]["code"] == 131026
