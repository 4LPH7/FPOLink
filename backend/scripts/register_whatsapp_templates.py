"""CLI utility to register and check status of WhatsApp message templates with Meta (T0.4).

Usage:
    python backend/scripts/register_whatsapp_templates.py --action list
    python backend/scripts/register_whatsapp_templates.py --action submit [--template-file docs/meta_templates.json]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings


def get_waba_id() -> str:
    """Retrieve WhatsApp Business Account ID or fall back to Phone Number ID."""
    waba_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID") or settings.WHATSAPP_PHONE_NUMBER_ID
    if not waba_id or waba_id.startswith("test_"):
        print(
            "[WARNING] WHATSAPP_BUSINESS_ACCOUNT_ID not explicitly set; using WHATSAPP_PHONE_NUMBER_ID."
        )
    return waba_id


def list_templates(waba_id: str) -> None:
    """Fetch and display all registered templates in the WABA."""
    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{waba_id}/message_templates"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}

    print(
        f"Querying Meta Graph API ({settings.WHATSAPP_API_VERSION}) templates for WABA: {waba_id}..."
    )
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"\nFound {len(data)} templates:")
            print(f"{'Name':<25} | {'Language':<10} | {'Category':<12} | {'Status':<12}")
            print("-" * 65)
            for t in data:
                print(
                    f"{t.get('name'):<25} | {t.get('language'):<10} | {t.get('category'):<12} | {t.get('status'):<12}"
                )
        else:
            print(f"\n[ERROR] Meta returned {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"\n[EXCEPTION] Failed to list templates: {e}")


def submit_templates(waba_id: str, template_file_path: Path) -> None:
    """Submit templates defined in JSON file to Meta Graph API for approval."""
    if not template_file_path.exists():
        print(f"[ERROR] Template file not found: {template_file_path}")
        sys.exit(1)

    with open(template_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    templates = data.get("templates", [])
    print(f"Loaded {len(templates)} templates from {template_file_path.name}.")

    url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{waba_id}/message_templates"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=15.0) as client:
        for t in templates:
            name = t.get("name")
            lang = t.get("language")
            print(f"\nSubmitting template '{name}' ({lang})...")
            try:
                resp = client.post(url, headers=headers, json=t)
                if resp.status_code in (200, 201):
                    res_json = resp.json()
                    print(
                        f"  [SUCCESS] Template '{name}' created. ID: {res_json.get('id')}, Status: {res_json.get('status')}"
                    )
                else:
                    print(f"  [FAILED] HTTP {resp.status_code}: {resp.text}")
            except Exception as e:
                print(f"  [EXCEPTION] Error submitting '{name}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="WhatsApp Message Template Registration & Inspection Tool"
    )
    parser.add_argument(
        "--action", choices=["list", "submit"], default="list", help="Action to perform"
    )
    parser.add_argument(
        "--template-file",
        default="docs/meta_templates.json",
        help="Path to template definitions JSON",
    )
    args = parser.parse_args()

    waba_id = get_waba_id()
    print("=" * 65)
    print("FPOLink TN — WhatsApp Template Manager")
    print("=" * 65)

    if not settings.WHATSAPP_ACCESS_TOKEN or settings.WHATSAPP_ACCESS_TOKEN.startswith("test_"):
        print("\n[NOTE] Running with mock or unset WHATSAPP_ACCESS_TOKEN.")
        print("To submit or inspect live templates on Meta:")
        print("  1. Configure WHATSAPP_ACCESS_TOKEN in .env")
        print("  2. Configure WHATSAPP_BUSINESS_ACCOUNT_ID in .env")
        print(f"\nValidating template payload structure in '{args.template_file}' locally...")
        path = Path(args.template_file)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✓ Valid JSON format with {len(data.get('templates', []))} template specs:")
            for t in data.get("templates", []):
                print(f"  - {t.get('name')} ({t.get('language')}) | Category: {t.get('category')}")
        else:
            print(f"File not found: {path}")
        return

    if args.action == "list":
        list_templates(waba_id)
    elif args.action == "submit":
        submit_templates(waba_id, Path(args.template_file))


if __name__ == "__main__":
    main()
