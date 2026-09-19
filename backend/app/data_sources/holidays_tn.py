"""Tamil Nadu holiday/festival features for price prediction.

Uses Python `holidays` package supplemented with curated
Tamil Nadu festivals that affect agricultural demand.
"""

import logging
from datetime import date
from typing import List, Dict

try:
    import holidays
    HAS_HOLIDAYS = True
except ImportError:
    HAS_HOLIDAYS = False

logger = logging.getLogger(__name__)

# Major Tamil Nadu festivals and events affecting agricultural demand
# These are approximate dates — some shift by Tamil/Hindu calendar
TN_FESTIVALS = {
    # (month, day): (name, demand_impact)
    (1, 14): ("Pongal / Bhogi", "high"),
    (1, 15): ("Thai Pongal", "very_high"),
    (1, 16): ("Mattu Pongal", "high"),
    (1, 17): ("Kaanum Pongal", "medium"),
    (4, 14): ("Tamil New Year (Puthandu)", "high"),
    (8, 15): ("Independence Day", "medium"),
    (10, 2): ("Gandhi Jayanti", "low"),
    (1, 26): ("Republic Day", "low"),
    # Deepavali moves each year — approximate October/November
    # Navratri/Dussehra — September/October
    # These need to be updated yearly or computed from a lunar calendar
}


def is_festival(d: date) -> bool:
    """Check if a date is a known festival day."""
    # Check curated Tamil Nadu festivals
    if (d.month, d.day) in TN_FESTIVALS:
        return True

    # Check national holidays
    if HAS_HOLIDAYS:
        india_holidays = holidays.India(years=d.year, state='TN')
        if d in india_holidays:
            return True

    return False


def days_to_nearest_festival(d: date, window: int = 30) -> int:
    """Days until the nearest festival within a window. Returns window+1 if none."""
    for offset in range(window + 1):
        check_date = date(d.year, d.month, d.day)
        try:
            from datetime import timedelta
            check_date = d + timedelta(days=offset)
            if is_festival(check_date):
                return offset
        except ValueError:
            continue
    return window + 1


def get_festival_features(d: date) -> Dict[str, int]:
    """Generate festival-related features for a given date."""
    return {
        "is_festival": int(is_festival(d)),
        "days_to_festival": days_to_nearest_festival(d),
        "is_pongal_week": int(d.month == 1 and 12 <= d.day <= 18),
        "is_deepavali_month": int(d.month in [10, 11]),  # Approximate
    }
