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

def get_real_price_sources() -> Tuple[str, ...]:
    """Dynamically return verified price sources based on environment and DEMO_MODE.
    
    Guarantees that DEMO_PRICE_SOURCE is never included in production environments.
    """
    from app.config import settings

    if settings.ENVIRONMENT.lower() == "production":
        return VERIFIED_PRICE_SOURCES
    if getattr(settings, "DEMO_MODE", False):
        return VERIFIED_PRICE_SOURCES + (DEMO_PRICE_SOURCE,)
    return VERIFIED_PRICE_SOURCES


# Default tuple for static references
REAL_PRICE_SOURCES: Tuple[str, ...] = VERIFIED_PRICE_SOURCES + (
    (DEMO_PRICE_SOURCE,) if (settings.DEMO_MODE and settings.ENVIRONMENT.lower() != "production") else ()
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
    return source.lower().strip() in set(get_real_price_sources())


def get_source_priority(source: str) -> int:
    """Return priority rank for source (lower = higher priority).

    Unknown sources receive lowest priority (99).
    """
    from app.config import settings

    if not source:
        return 99
    base = dict(SOURCE_PRIORITY)
    if (
        getattr(settings, "DEMO_MODE", False)
        and settings.ENVIRONMENT.lower() != "production"
    ):
        base[DEMO_PRICE_SOURCE] = 50
    return base.get(source.lower().strip(), 99)
