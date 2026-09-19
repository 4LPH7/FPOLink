"""Tests for unit conversions."""

from decimal import Decimal

import pytest

from app.utils.units import convert_from_per_kg, convert_to_per_kg


def test_convert_to_per_kg_quintal():
    # 15000 Rs / quintal -> 150 Rs / kg
    price = Decimal("15000")
    result = convert_to_per_kg(price, "quintal")
    assert result == Decimal("150")


def test_convert_to_per_kg_tonne():
    # 200000 Rs / tonne -> 200 Rs / kg
    price = Decimal("200000")
    result = convert_to_per_kg(price, "tonne")
    assert result == Decimal("200")


def test_convert_to_per_kg_kg():
    price = Decimal("150.50")
    assert convert_to_per_kg(price, "kg") == Decimal("150.50")


def test_convert_to_per_kg_unit():
    price = Decimal("25")
    assert convert_to_per_kg(price, "per unit") == Decimal("25")


def test_convert_from_per_kg():
    price_kg = Decimal("150")
    result = convert_from_per_kg(price_kg, "quintal")
    assert result == Decimal("15000")


def test_convert_invalid_unit():
    with pytest.raises(ValueError, match="Unknown unit"):
        convert_to_per_kg(Decimal("100"), "unknown_unit")
