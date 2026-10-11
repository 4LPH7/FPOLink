"""Interactively provision an administrator using the shared hardened bootstrap."""

import getpass
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from create_admin import create_or_update_admin


def main() -> None:
    phone = input("Admin phone (10-15 digits, optional leading +): ").strip()
    if not re.fullmatch(r"\+?\d{10,15}", phone):
        raise SystemExit("Invalid phone number format")

    password = getpass.getpass("Admin password (minimum 12 characters in production): ")
    if password != getpass.getpass("Confirm admin password: "):
        raise SystemExit("Passwords do not match")

    name = input("Admin name [Admin]: ").strip() or "Admin"
    create_or_update_admin(
        phone=phone,
        password=password,
        name=name,
        must_change_password=True,
    )


if __name__ == "__main__":
    main()
