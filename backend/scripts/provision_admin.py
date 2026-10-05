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
    phone = input("Admin phone (10-15 digits, optional leading +): ").strip()
    if not re.fullmatch(r"\+?\d{10,15}", phone):
        raise SystemExit("Invalid phone number format")

    password = getpass.getpass("Admin password (minimum 12 characters): ")
    confirmation = getpass.getpass("Confirm admin password: ")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    db = SessionLocal()
    try:
        if db.query(User).filter(User.phone == phone).first():
            raise SystemExit("An account with that phone number already exists")
        admin = User(
            name=input("Admin name: ").strip(),
            phone=phone,
            role=UserRole.ADMIN,
            hashed_password=hash_password(password),
            password_change_required=True,
            is_active=True,
            language_preference="en",
        )
        if not admin.name:
            raise SystemExit("Admin name is required")
        db.add(admin)
        db.commit()
        print("Administrator created. Sign in with the phone number and password you entered.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
