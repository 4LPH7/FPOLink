"""Interactively create an initial production administrator without logging secrets."""

import getpass
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import hash_password


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Create or update administrator account.")
    parser.add_argument("--phone", help="Admin phone number", default=None)
    parser.add_argument("--password", help="Admin password", default=None)
    parser.add_argument("--name", help="Admin name", default=None)
    args = parser.parse_args()

    phone = (args.phone or input("Admin phone (10-15 digits, optional leading +): ")).strip()
    if not re.fullmatch(r"\+?\d{10,15}", phone):
        raise SystemExit("Invalid phone number format")

    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Admin password (minimum 8 characters): ")
        confirmation = getpass.getpass("Confirm admin password: ")
        if password != confirmation:
            raise SystemExit("Passwords do not match")

    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters")

    name = (args.name or (input("Admin name [Admin]: ").strip() or "Admin")).strip()

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.phone == phone).first()
        if existing:
            existing.name = name or existing.name
            existing.role = UserRole.ADMIN
            existing.hashed_password = hash_password(password)
            existing.password_change_required = True
            existing.is_active = True
            db.commit()
            print(f"Administrator {phone} ({name}) updated successfully.")
            return

        admin = User(
            name=name,
            phone=phone,
            role=UserRole.ADMIN,
            hashed_password=hash_password(password),
            password_change_required=True,
            is_active=True,
            language_preference="ta",
        )
        db.add(admin)
        db.commit()
        print(f"Administrator {phone} ({name}) created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
