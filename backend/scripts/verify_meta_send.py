"""CLI utility to verify Meta WhatsApp Cloud API outbound transmission (T0.2).

Usage:
    python backend/scripts/verify_meta_send.py --to 919876543210 [--text "Hello from FPOLink!"]
    python backend/scripts/verify_meta_send.py --to 919876543210 --template daily_price_digest
"""

import argparse
import json
import os
import sys

import httpx

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings


def send_direct_text(to_phone: str, text_body: str) -> dict:
    """Send text message directly to Meta WhatsApp Cloud API."""
    if not settings.WHATSAPP_ACCESS_TOKEN or settings.WHATSAPP_ACCESS_TOKEN.startswith("test_"):
        print("\n[ERROR] WHATSAPP_ACCESS_TOKEN is not configured or is a mock token.")
        print("Please configure valid Meta Cloud API credentials in your .env file:")
        print("  WHATSAPP_ACCESS_TOKEN=<system_user_access_token>")
        print("  WHATSAPP_PHONE_NUMBER_ID=<meta_phone_number_id>\n")
        sys.exit(1)

    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": text_body},
    }

    print(f"Connecting to Meta Graph API ({settings.WHATSAPP_API_VERSION})...")
    print(f"Endpoint: {url}")
    print(f"Recipient: {to_phone}")

    with httpx.Client(timeout=15.0) as client:
        response = client.post(url, headers=headers, json=payload)

    return {
        "status_code": response.status_code,
        "response_json": response.json()
        if response.headers.get("content-type", "").startswith("application/json")
        else response.text,
    }


def send_test_template(to_phone: str, template_name: str, lang: str = "ta") -> dict:
    """Send pre-approved utility template to Meta WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": lang},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "2026-09-23"},
                        {"type": "text", "text": "Turmeric / மஞ்சள்"},
                        {"type": "text", "text": "Erode Mandi"},
                        {"type": "text", "text": "₹154.50/kg"},
                    ],
                }
            ],
        },
    }

    with httpx.Client(timeout=15.0) as client:
        response = client.post(url, headers=headers, json=payload)

    return {
        "status_code": response.status_code,
        "response_json": response.json()
        if response.headers.get("content-type", "").startswith("application/json")
        else response.text,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Test Meta WhatsApp Cloud API outbound message send"
    )
    parser.add_argument(
        "--to", required=True, help="Recipient phone with country code (e.g. 919876543210)"
    )
    parser.add_argument(
        "--text",
        default="வணக்கம்! FPOLink சோதனை செய்தி (Test message from FPOLink).",
        help="Custom text body",
    )
    parser.add_argument("--template", help="Template name to test send (e.g. daily_price_digest)")
    parser.add_argument("--lang", default="ta", choices=["ta", "en"], help="Template language code")
    args = parser.parse_args()

    # Normalise phone: strip + and spaces
    phone = args.to.replace("+", "").replace(" ", "").replace("-", "")

    print("=" * 60)
    print("FPOLink TN — Meta WhatsApp Cloud API Outbound Verification")
    print("=" * 60)

    try:
        if args.template:
            result = send_test_template(phone, args.template, lang=args.lang)
        else:
            result = send_direct_text(phone, args.text)

        status = result["status_code"]
        body = result["response_json"]

        print(f"\nResponse HTTP Status: {status}")
        print(f"Payload:\n{json.dumps(body, indent=2)}")

        if status == 200:
            messages = body.get("messages", [])
            wamid = messages[0].get("id") if messages else "N/A"
            print("\n[SUCCESS] Message successfully dispatched to Meta Cloud API!")
            print(f"Meta Message ID (wamid): {wamid}")
            print("Check the recipient phone for incoming WhatsApp message.")
        elif status == 400:
            print("\n[FAILED] Meta rejected the request (Bad Request).")
            print("Common causes:")
            print(
                "  - Recipient number not verified in Meta Developer Sandbox (if using Test Number)"
            )
            print("  - Template not yet approved or parameter mismatch")
        elif status == 401:
            print("\n[FAILED] Authentication failed. Access token is invalid or expired.")
        else:
            print(f"\n[FAILED] Unexpected response from Meta: {status}")

    except Exception as e:
        print(f"\n[EXCEPTION] Failed to execute send: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
