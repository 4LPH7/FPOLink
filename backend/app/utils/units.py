"""Unit conversion utilities for agricultural commodities."""

from decimal import Decimal

# Conversion factors to canonical unit (Rs/kg)
UNIT_CONVERSIONS = {
    "kg": Decimal("1"),
    "quintal": Decimal("100"),
    "tonne": Decimal("1000"),
    "metric_ton": Decimal("1000"),
    "20 kgs": Decimal("20"),
    "100 kgs": Decimal("100"),
    "per unit": Decimal("1"),  # For coconut (per unit, not per kg)
}


def convert_to_per_kg(price: Decimal, from_unit: str) -> Decimal:
    """Convert a price from any unit to Rs/kg.

    Args:
        price: Price in the original unit
        from_unit: Original unit (e.g., 'quintal', 'tonne')

    Returns:
        Price in Rs/kg
    """
    unit_lower = from_unit.lower().strip()
    factor = UNIT_CONVERSIONS.get(unit_lower)

    if factor is None:
        raise ValueError(f"Unknown unit: {from_unit}. Known units: {list(UNIT_CONVERSIONS.keys())}")

    if factor == 0:
        raise ValueError("Cannot convert: factor is zero")

    return price / factor


def convert_from_per_kg(price_per_kg: Decimal, to_unit: str) -> Decimal:
    """Convert Rs/kg to another unit."""
    unit_lower = to_unit.lower().strip()
    factor = UNIT_CONVERSIONS.get(unit_lower)

    if factor is None:
        raise ValueError(f"Unknown unit: {to_unit}")

    return price_per_kg * factor
