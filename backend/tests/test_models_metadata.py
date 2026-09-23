"""Model metadata regression tests."""

import app.models  # noqa: F401
from app.models.base import Base


def test_weather_data_table_registered_in_metadata():
    assert "weather_data" in Base.metadata.tables
