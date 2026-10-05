"""Constants and utilities for verified market price data sources.

Guarantees that synthetic, demo, and test data cannot contaminate
farmer-facing responses, dashboard statistics, or ML training pipelines.
"""

from typing import Dict, Set, Tuple

from app.config import settings

# Whitelist of real, verified market price sources
VERIFIED_PRICE_SOURCES: Tuple[str, ...] = ("ceda", "ogd", "agmarknet", "mandiprices_agmarknet")

# Clearly-labelled demonstration prices (scripts/seed_demo.py). Served ONLY when DEMO_MODE=true
# so a fresh test deployment has something to show; every response carries source="demo_seed".
DEMO_PRICE_SOURCE = "demo_seed"

# Sources served by price APIs, the bot and forecasting.
REAL_PRICE_SOURCES: Tuple[str, ...] = VERIFIED_PRICE_SOURCES + (
    (DEMO_PRICE_SOURCE,) if settings.DEMO_MODE else ()
)
REAL_PRICE_SOURCES_SET: Set[str] = set(REAL_PRICE_SOURCES)

# Deterministic source arbitration priority (lower number = higher priority)
# When multiple sources report for the same crop, market, variety, and date:
# - ogd is preferred for current/recent days as the official real-time mandi observation.
# - agmarknet is the official primary mandi source.
# - ceda is preserved for long-term historical records.
SOURCE_PRIORITY: Dict[str, int] = {
    "ogd": 1,
    "agmarknet": 2,
    "mandiprices_agmarknet": 2,
    "ceda": 3,
}
if settings.DEMO_MODE:
    SOURCE_PRIORITY[DEMO_PRICE_SOURCE] = 50

# Synthetic or unverified sources that MUST NEVER be served to farmers
SYNTHETIC_SOURCES: Tuple[str, ...] = (
    "ceda_synthetic",
    "seed",
    "seed_demo",
    "demo_seed",
    "test",
)


def is_real_source(source: str) -> bool:
    """Return True if source is in the real verified price sources whitelist."""
    if not source:
        return False
    return source.lower().strip() in REAL_PRICE_SOURCES_SET


def get_source_priority(source: str) -> int:
    """Return priority rank for source (lower = higher priority).

    Unknown sources receive lowest priority (99).
    """
    if not source:
        return 99
    return SOURCE_PRIORITY.get(source.lower().strip(), 99)
