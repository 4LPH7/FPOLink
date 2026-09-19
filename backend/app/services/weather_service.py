"""Weather ingestion service."""

import logging
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.weather import WeatherData
from app.data_sources.weather import WeatherProvider
from app.data_sources.nasa_power import NASAPowerProvider

logger = logging.getLogger(__name__)

# Erode district coordinates
DEFAULT_LOCATIONS = {
    "Erode": {"latitude": 11.3410, "longitude": 77.7172},
}


class WeatherService:
    """Manages weather data ingestion and retrieval."""

    def __init__(self, db: Session):
        self.db = db
        self.open_meteo = WeatherProvider()
        self.nasa_power = NASAPowerProvider()

    def ingest_forecast(self, district: str = "Erode", days: int = 7) -> int:
        """Fetch and store weather forecast."""
        coords = DEFAULT_LOCATIONS.get(district)
        if not coords:
            logger.warning(f"No coordinates for district: {district}")
            return 0

        data = self.open_meteo.fetch_forecast(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            days=days,
        )

        stored = 0
        for entry in data:
            d = date.fromisoformat(entry["date"])
            existing = self.db.query(WeatherData).filter(
                WeatherData.district == district,
                WeatherData.date == d,
            ).first()

            if existing:
                # Update forecast data
                existing.temperature_max = entry["temperature_max"]
                existing.temperature_min = entry["temperature_min"]
                existing.rainfall_mm = entry["rainfall_mm"] or 0
                existing.humidity = entry.get("humidity")
                existing.wind_speed = entry.get("wind_speed")
            else:
                w = WeatherData(
                    district=district,
                    date=d,
                    temperature_max=entry["temperature_max"],
                    temperature_min=entry["temperature_min"],
                    rainfall_mm=entry["rainfall_mm"] or 0,
                    humidity=entry.get("humidity"),
                    wind_speed=entry.get("wind_speed"),
                    source="open_meteo",
                )
                self.db.add(w)
                stored += 1

        self.db.commit()
        logger.info(f"Stored {stored} weather entries for {district}")
        return stored

    def backfill_history(
        self,
        district: str = "Erode",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """Backfill weather history from NASA POWER."""
        coords = DEFAULT_LOCATIONS.get(district)
        if not coords:
            return 0

        start = start_date or date(2020, 1, 1)
        end = end_date or date.today()

        data = self.nasa_power.fetch_history(
            latitude=coords["latitude"],
            longitude=coords["longitude"],
            start_date=start,
            end_date=end,
        )

        stored = 0
        for entry in data:
            d = date.fromisoformat(entry["date"])
            existing = self.db.query(WeatherData).filter(
                WeatherData.district == district,
                WeatherData.date == d,
            ).first()

            if not existing:
                w = WeatherData(
                    district=district,
                    date=d,
                    temperature_max=entry["temperature_max"],
                    temperature_min=entry["temperature_min"],
                    rainfall_mm=entry["rainfall_mm"] or 0,
                    humidity=entry.get("humidity"),
                    wind_speed=entry.get("wind_speed"),
                    source="nasa_power",
                )
                self.db.add(w)
                stored += 1

        self.db.commit()
        logger.info(f"Backfilled {stored} weather entries for {district}")
        return stored
