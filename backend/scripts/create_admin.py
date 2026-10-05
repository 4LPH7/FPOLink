"""Bootstrap / provision the initial FPOLink administrator account.

Reads credentials from environment variables:
  - ADMIN_PHONE (required): Admin phone number (10-15 digits, optional leading +)
  - ADMIN_PASSWORD (required): Admin password (minimum 8 characters)
  - ADMIN_NAME (optional, default: "Admin"): Admin display name
  - ADMIN_FPO_NAME (optional, default: "Erode Farmers Collective"): Attached FPO name

Works across all environments (development, staging, production).
Never logs or prints plain-text passwords.
"""

import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.fpo import FPO
from app.models.user import User, UserRole
from app.services.auth import hash_password


def create_or_update_admin(
    phone: str,
    password: str,
    name: str = "Admin",
    fpo_name: str = "Erode Farmers Collective",
    must_change_password: bool = False,
) -> User:
    """Create or update admin account idempotently."""
    phone = phone.strip()
    if not re.fullmatch(r"\+?\d{10,15}", phone):
        raise ValueError(
            "Invalid phone number format: must be 10-15 digits with optional leading +"
        )

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    db = SessionLocal()
    try:
        # 1. Ensure an FPO exists
        fpo = db.query(FPO).filter(FPO.name == fpo_name).first()
        if not fpo:
            fpo = db.query(FPO).first()
        if not fpo:
            fpo = FPO(
                name=fpo_name,
                registration_number=f"TN-FPO-{phone[-4:]}",
                district="Erode",
                village="Erode",
                contact_phone=phone,
            )
            db.add(fpo)
            db.flush()

        # 2. Find or create user
        user = db.query(User).filter(User.phone == phone).first()
        hashed = hash_password(password)

        if user:
            user.name = name or user.name
            user.role = UserRole.ADMIN
            user.hashed_password = hashed
            user.password_change_required = must_change_password
            user.is_active = True
            if not user.fpo_id:
                user.fpo_id = fpo.id
            db.commit()
            db.refresh(user)
            print(f"Administrator {phone} ({user.name}) updated successfully (FPO: {fpo.name}).")
            return user

        user = User(
            name=name,
            phone=phone,
            role=UserRole.ADMIN,
            hashed_password=hashed,
            password_change_required=must_change_password,
            is_active=True,
            language_preference="ta",
            fpo_id=fpo.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Administrator {phone} ({user.name}) created successfully (FPO: {fpo.name}).")
        return user
    finally:
        db.close()


def main() -> None:
    phone = os.environ.get("ADMIN_PHONE")
    password = os.environ.get("ADMIN_PASSWORD")
    name = os.environ.get("ADMIN_NAME", "Admin")
    fpo_name = os.environ.get("ADMIN_FPO_NAME", "Erode Farmers Collective")
    must_change = os.environ.get("ADMIN_MUST_CHANGE_PASSWORD", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    if not phone or not phone.strip():
        print("ERROR: ADMIN_PHONE environment variable is required.", file=sys.stderr)
        sys.exit(1)

    if not password or not password.strip():
        print("ERROR: ADMIN_PASSWORD environment variable is required.", file=sys.stderr)
        sys.exit(1)

    try:
        create_or_update_admin(
            phone=phone,
            password=password,
            name=name,
            fpo_name=fpo_name,
            must_change_password=must_change,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
