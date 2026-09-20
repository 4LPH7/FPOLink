"""Constants and utilities for verified market price data sources.

Guarantees that synthetic, demo, and test data cannot contaminate
farmer-facing responses, dashboard statistics, or ML training pipelines.
"""

from typing import Dict, Set, Tuple

# Whitelist of real, verified market price sources
REAL_PRICE_SOURCES: Tuple[str, ...] = ("ceda", "ogd")
REAL_PRICE_SOURCES_SET: Set[str] = set(REAL_PRICE_SOURCES)

# Deterministic source arbitration priority (lower number = higher priority)
# When both OGD (live daily) and CEDA (historical) report for the same crop,
# market, variety, and date:
# - ogd is preferred for current/recent days as the official real-time mandi observation.
# - ceda is preserved for long-term historical records.
SOURCE_PRIORITY: Dict[str, int] = {
    "ogd": 1,
    "ceda": 2,
}

# Synthetic or unverified sources that MUST NEVER be served to farmers
SYNTHETIC_SOURCES: Tuple[str, ...] = ("ceda_synthetic", "seed", "seed_demo", "test")


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
