"""Contract tests for WhatsApp Cloud API outgoing payloads using respx."""

import json

import httpx
import pytest
import respx

from app.messaging.base import Button
from app.messaging.whatsapp_cloud import WhatsAppCloudChannel


@pytest.mark.anyio
@respx.mock
async def test_send_text_contract():
    """Assert exact JSON payload and headers for text messages."""
    access_token = "test_meta_token_abc"
    phone_id = "10987654321"
    api_version = "v23.0"
    wa_url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"

    route = respx.post(wa_url).respond(status_code=200, json={"messages": [{"id": "wamid.HBgL"}]})

    async with httpx.AsyncClient() as client:
        channel = WhatsAppCloudChannel(access_token, phone_id, api_version, client=client)
        await channel.send_text("919876543210", "Vanakkam! Today turmeric price is ₹130/kg.")

    assert route.called
    request = route.calls.last.request
    assert request.headers["authorization"] == f"Bearer {access_token}"
    assert request.headers["content-type"] == "application/json"

    data = json.loads(request.content)
    assert data == {
        "messaging_product": "whatsapp",
        "to": "919876543210",
        "type": "text",
        "text": {"body": "Vanakkam! Today turmeric price is ₹130/kg."},
    }


@pytest.mark.anyio
@respx.mock
async def test_send_buttons_contract():
    """Assert exact JSON for interactive buttons, max 3 buttons, and 20 char title truncation."""
    access_token = "test_meta_token_abc"
    phone_id = "10987654321"
    api_version = "v23.0"
    wa_url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"

    route = respx.post(wa_url).respond(status_code=200, json={"messages": [{"id": "wamid.HBgL"}]})

    # Pass 4 buttons, one with title > 20 chars
    buttons = [
        Button("b_price", "Current Market Price"),  # 20 chars
        Button("b_forecast", "Crop Price Forecast Analysis"),  # 28 chars -> truncate to 20
        Button("b_harvest", "Record Harvest"),  # 14 chars
        Button("b_overflow", "Ignored Fourth Button"),  # Exceeds max 3 -> must be dropped
    ]

    async with httpx.AsyncClient() as client:
        channel = WhatsAppCloudChannel(access_token, phone_id, api_version, client=client)
        await channel.send_buttons("919876543210", "Please select an option:", buttons)

    assert route.called
    data = json.loads(route.calls.last.request.content)
    assert data == {
        "messaging_product": "whatsapp",
        "to": "919876543210",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Please select an option:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "b_price", "title": "Current Market Price"}},
                    {
                        "type": "reply",
                        "reply": {"id": "b_forecast", "title": "Crop Price Forecast "},
                    },
                    {"type": "reply", "reply": {"id": "b_harvest", "title": "Record Harvest"}},
                ]
            },
        },
    }
    assert len(data["interactive"]["action"]["buttons"]) == 3
    assert len(data["interactive"]["action"]["buttons"][1]["reply"]["title"]) <= 20


@pytest.mark.anyio
@respx.mock
async def test_send_template_contract():
    """Assert exact JSON for business-initiated templates with body parameters."""
    access_token = "test_meta_token_abc"
    phone_id = "10987654321"
    api_version = "v23.0"
    wa_url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"

    route = respx.post(wa_url).respond(status_code=200, json={"messages": [{"id": "wamid.HBgL"}]})

    async with httpx.AsyncClient() as client:
        channel = WhatsAppCloudChannel(access_token, phone_id, api_version, client=client)
        await channel.send_template(
            "919876543210",
            name="daily_price_digest",
            lang="ta",
            params=["மஞ்சள்", "13000", "ஈரோடு"],
        )

    assert route.called
    data = json.loads(route.calls.last.request.content)
    assert data == {
        "messaging_product": "whatsapp",
        "to": "919876543210",
        "type": "template",
        "template": {
            "name": "daily_price_digest",
            "language": {"code": "ta"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "மஞ்சள்"},
                        {"type": "text", "text": "13000"},
                        {"type": "text", "text": "ஈரோடு"},
                    ],
                }
            ],
        },
    }
