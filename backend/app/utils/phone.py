"""Phone number normalisation utilities for India / FPOLink."""

import re


def normalise_phone(phone: str) -> str:
    """Normalise phone number to 10-digit Indian standard.

    Strips country codes (+91, 0091, 91), leading zeros, spaces, and punctuation.
    Returns the last 10 digits. Raises ValueError if fewer than 10 digits are present.
    """
    if not phone:
        raise ValueError("Phone number cannot be empty")

    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10:
        raise ValueError(
            f"Phone number must contain at least 10 digits, got '{phone}' ({len(digits)} digits)"
        )

    # Return last 10 digits
    return digits[-10:]


def format_phone_e164(phone: str, country_code: str = "91") -> str:
    """Format normalised phone to E.164 (+91...)."""
    return f"+{country_code}{normalise_phone(phone)}"
