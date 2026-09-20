"""Unit tests for phone normalisation, farmer consent, and bot models."""

import pytest

from app.models.farmer import Farmer
from app.models.whatsapp import ConversationState, OutboundMessage, WhatsAppInbound
from app.utils.phone import format_phone_e164, normalise_phone


class TestPhoneNormalisation:
    def test_ten_digits(self):
        assert normalise_phone("9876543210") == "9876543210"

    def test_with_spaces_and_hyphens(self):
        assert normalise_phone("98765-43210") == "9876543210"
        assert normalise_phone("98765 43210") == "9876543210"

    def test_with_plus_91(self):
        assert normalise_phone("+91 98765 43210") == "9876543210"
        assert normalise_phone("+919876543210") == "9876543210"

    def test_with_leading_zero(self):
        assert normalise_phone("09876543210") == "9876543210"

    def test_format_e164(self):
        assert format_phone_e164("9876543210") == "+919876543210"
        assert format_phone_e164("+91 98765 43210") == "+919876543210"

    def test_invalid_too_short(self):
        with pytest.raises(ValueError, match="at least 10 digits"):
            normalise_phone("987654")

    def test_invalid_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            normalise_phone("")


class TestBotModelsMetadata:
    def test_bot_tables_exist(self):
        assert WhatsAppInbound.__tablename__ == "whatsapp_inbound"
        assert ConversationState.__tablename__ == "conversation_state"
        assert OutboundMessage.__tablename__ == "outbound_messages"

    def test_farmer_fields_exist(self):
        columns = {c.name for c in Farmer.__table__.columns}
        assert "phone" in columns
        assert "lang" in columns
        assert "alerts_opt_in" in columns
        assert "alerts_opt_in_at" in columns
        assert "alerts_opt_out_at" in columns
