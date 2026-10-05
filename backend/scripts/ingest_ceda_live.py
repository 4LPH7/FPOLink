"""CEDA Agmarknet Live Ingestion & Authentication CLI Harness.

Provides programmatic interaction with Ashoka University's CEDA Data Portal API:
1. Check key validity & API connectivity
2. Request OTP and verify OTP for registration
3. Persist active key into .env
4. Fetch and ingest live price & arrival data for Tamil Nadu / Erode
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx

# Add backend directory to sys.path so app imports resolve
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.config import settings  # noqa: E402
from app.data_sources.ceda_api import (  # noqa: E402
    ERODE_CENSUS_DISTRICT_ID,
    TN_CENSUS_STATE_ID,
    CEDAAPIProvider,
)
from app.database import SessionLocal  # noqa: E402
from app.services.ingestion import IngestionService  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ceda_live")

ENV_PATH = backend_dir.parent / ".env"
CEDA_API_BASE_URL = "https://api.ceda.ashoka.edu.in/v1"


def check_status(api_key: Optional[str] = None) -> bool:
    """Check connectivity and key validity against CEDA API."""
    key = api_key or settings.CEDA_API_KEY
    print("\n" + "=" * 60)
    print(" CEDA AGMARKNET API STATUS CHECK")
    print("=" * 60)
    print(f"Base URL: {CEDA_API_BASE_URL}")
    print(
        f"Key Configured: {'Yes' if key else 'No'} ({key[:8]}... if present)"
        if key
        else "Key Configured: No"
    )

    provider = CEDAAPIProvider(api_key=key)
    valid, message = provider.validate_key()
    if valid:
        print("Status: \033[92mVALID & ACTIVE\033[0m")
        print(f"Details: {message}")
        return True
    else:
        print("Status: \033[91mINVALID OR EXPIRED\033[0m")
        print(f"Reason: {message}")
        print("\nTo generate or renew your CEDA API Key:")
        print(
            "1. Run: python backend/scripts/ingest_ceda_live.py --request-otp --email your_email@domain.com"
        )
        print("2. Check your email for the 6-digit OTP code")
        print(
            "3. Run: python backend/scripts/ingest_ceda_live.py --verify-otp --email your_email@domain.com --otp 123456"
        )
        print(
            "4. Or enter the key via: python backend/scripts/ingest_ceda_live.py --set-key <your_api_key>"
        )
        return False


def request_otp(email: str, organisation: str = "FPOLink TN") -> bool:
    """Request a 6-digit OTP from Ashoka CEDA for generating an API key."""
    print(f"\nRequesting OTP from CEDA for '{email}' (Organisation: '{organisation}')...")
    url = f"{CEDA_API_BASE_URL}/apiService/request-otp"
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json={"email": email, "organisation": organisation})
            data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
            if resp.status_code == 200:
                print(f"\033[92mSUCCESS: OTP sent to {email}!\033[0m")
                print(
                    "Please check your inbox (and spam folder) for the 6-digit verification code."
                )
                print(
                    f"Next step: python backend/scripts/ingest_ceda_live.py --verify-otp --email {email} --otp <CODE>"
                )
                return True
            else:
                msg = data.get("message") or resp.text
                print(f"\033[91mFAILED (HTTP {resp.status_code}): {msg}\033[0m")
                return False
    except Exception as e:
        print(f"\033[91mConnection error: {e}\033[0m")
        return False


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP with Ashoka CEDA."""
    print(f"\nVerifying OTP '{otp}' for '{email}'...")
    url = f"{CEDA_API_BASE_URL}/apiService/verify-otp"
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json={"email": email, "otp": otp.strip()})
            data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
            if resp.status_code == 200:
                print("\033[92mSUCCESS: OTP verified!\033[0m")
                msg = data.get("message") or "API key has been issued/emailed"
                print(f"Response: {msg}")
                # If key returned directly in response payload:
                key = data.get("apiKey") or data.get("key") or data.get("api_key")
                if key:
                    print(f"Generated Key: {key}")
                    update_env_key(key)
                else:
                    print(f"Check your email '{email}' for the CEDA API key string.")
                    print("Once received, activate it with:")
                    print("  python backend/scripts/ingest_ceda_live.py --set-key <YOUR_KEY>")
                return True
            else:
                msg = data.get("message") or resp.text
                print(f"\033[91mFAILED (HTTP {resp.status_code}): {msg}\033[0m")
                return False
    except Exception as e:
        print(f"\033[91mConnection error: {e}\033[0m")
        return False


def update_env_key(new_key: str) -> bool:
    """Validate and write new CEDA_API_KEY into .env."""
    new_key = new_key.strip()
    provider = CEDAAPIProvider(api_key=new_key)
    valid, message = provider.validate_key()
    if not valid:
        print(
            f"\033[91mERROR: The provided key could not be validated by CEDA API: {message}\033[0m"
        )
        return False

    print(f"\033[92mKey validated successfully: {message}\033[0m")

    # Update .env file
    if ENV_PATH.exists():
        content = ENV_PATH.read_text(encoding="utf-8")
        if re.search(r"^CEDA_API_KEY=.*$", content, flags=re.MULTILINE):
            updated = re.sub(
                r"^CEDA_API_KEY=.*$", f"CEDA_API_KEY={new_key}", content, flags=re.MULTILINE
            )
        else:
            updated = content + f"\nCEDA_API_KEY={new_key}\n"
        ENV_PATH.write_text(updated, encoding="utf-8")
        print(f"Updated CEDA_API_KEY in {ENV_PATH}")
    else:
        ENV_PATH.write_text(f"CEDA_API_KEY={new_key}\n", encoding="utf-8")
        print(f"Created {ENV_PATH} with CEDA_API_KEY")

    return True


def run_live_ingestion(
    api_key: Optional[str] = None,
    crops: Optional[List[str]] = None,
    district: str = "Erode",
    days: int = 90,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> dict:
    """Fetch live data from CEDA and ingest into PostgreSQL."""
    key = api_key or settings.CEDA_API_KEY
    if not key:
        print(
            "\033[91mERROR: No CEDA API key configured. Run with --request-otp or --set-key.\033[0m"
        )
        return {"error": "No API key configured"}

    provider = CEDAAPIProvider(api_key=key)
    valid, message = provider.validate_key()
    if not valid:
        print(f"\033[91mERROR: CEDA API key validation failed: {message}\033[0m")
        return {"error": message}

    crops = crops or ["turmeric", "banana", "coconut"]
    end_d = end_date or date.today()
    start_d = start_date or (end_d - timedelta(days=days))

    print("\n" + "=" * 60)
    print(" RUNNING CEDA LIVE INGESTION")
    print(f" Crops: {', '.join(crops)}")
    print(f" District: {district} (Tamil Nadu)")
    print(f" Date Range: {start_d} to {end_d}")
    print("=" * 60)

    db = SessionLocal()
    service = IngestionService(db)

    total_records = 0
    total_stored = 0

    try:
        # 1. Fetch available commodities
        commodities = provider.get_commodities()
        print(f"Fetched {len(commodities)} commodities from CEDA master catalog.")

        for crop_name in crops:
            print(f"\n[>] Fetching CEDA records for '{crop_name}' in '{district}'...")
            records = provider.fetch_prices(
                crop=crop_name,
                district=district,
                start_date=start_d,
                end_date=end_d,
                state_id=TN_CENSUS_STATE_ID,
                district_id=ERODE_CENSUS_DISTRICT_ID,
            )
            print(f"    Received: {len(records)} price records from CEDA.")
            total_records += len(records)

            if records:
                stored = service._store_records(records)
                total_stored += stored
                print(f"    Stored/Updated in DB: {stored} records.")

        db.commit()
        print("\n" + "=" * 60)
        print(" CEDA INGESTION COMPLETED")
        print(f" Total Fetched: {total_records}")
        print(f" Total Stored in DB: {total_stored}")
        print("=" * 60)
        return {"status": "success", "fetched": total_records, "stored": total_stored}

    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="FPOLink CEDA Agmarknet Live Ingestion CLI")
    parser.add_argument(
        "--status", action="store_true", help="Check CEDA API connectivity and key validity"
    )
    parser.add_argument(
        "--request-otp", action="store_true", help="Request registration OTP from CEDA"
    )
    parser.add_argument("--verify-otp", action="store_true", help="Verify OTP and generate API key")
    parser.add_argument("--email", type=str, help="Email address for CEDA registration")
    parser.add_argument("--org", type=str, default="FPOLink Tamil Nadu", help="Organisation name")
    parser.add_argument("--otp", type=str, help="6-digit OTP code received in email")
    parser.add_argument("--set-key", type=str, help="Validate and save new CEDA_API_KEY into .env")
    parser.add_argument("--ingest", action="store_true", help="Run live price ingestion from CEDA")
    parser.add_argument(
        "--crops", type=str, default="turmeric,banana,coconut", help="Comma-separated crop names"
    )
    parser.add_argument("--district", type=str, default="Erode", help="Target district")
    parser.add_argument("--days", type=int, default=90, help="Days of historical data to fetch")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--api-key", type=str, help="Override CEDA API key for this run")

    args = parser.parse_args()

    if args.request_otp:
        if not args.email:
            print("Error: --email is required for --request-otp")
            sys.exit(1)
        request_otp(args.email, args.org)
    elif args.verify_otp:
        if not args.email or not args.otp:
            print("Error: Both --email and --otp are required for --verify-otp")
            sys.exit(1)
        verify_otp(args.email, args.otp)
    elif args.set_key:
        success = update_env_key(args.set_key)
        sys.exit(0 if success else 1)
    elif args.ingest:
        crops_list = [c.strip() for c in args.crops.split(",") if c.strip()]
        start_d = date.fromisoformat(args.start_date) if args.start_date else None
        end_d = date.fromisoformat(args.end_date) if args.end_date else None
        run_live_ingestion(
            api_key=args.api_key,
            crops=crops_list,
            district=args.district,
            days=args.days,
            start_date=start_d,
            end_date=end_d,
        )
    else:
        # Default action: check status
        check_status(api_key=args.api_key)


if __name__ == "__main__":
    main()
