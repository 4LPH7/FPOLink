"""Weather ingestion service."""

import logging
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.data_sources.nasa_power import NASAPowerProvider
from app.data_sources.weather import WeatherProvider
from app.models.geography import District
from app.models.weather import WeatherData

logger = logging.getLogger(__name__)

# Key Tamil Nadu district coordinates for Open-Meteo & NASA POWER weather queries
DEFAULT_LOCATIONS = {
    "Erode": {"latitude": 11.3410, "longitude": 77.7172},
    "Coimbatore": {"latitude": 11.0168, "longitude": 76.9558},
    "Salem": {"latitude": 11.6643, "longitude": 78.1460},
    "Tiruppur": {"latitude": 11.1085, "longitude": 77.3411},
    "Thirupur": {"latitude": 11.1085, "longitude": 77.3411},
    "Namakkal": {"latitude": 11.2189, "longitude": 78.1674},
    "Dharmapuri": {"latitude": 12.1211, "longitude": 78.1582},
    "Dindigul": {"latitude": 10.3673, "longitude": 77.9803},
    "Karur": {"latitude": 10.9601, "longitude": 78.0766},
    "Madurai": {"latitude": 9.9252, "longitude": 78.1198},
    "Thanjavur": {"latitude": 10.7870, "longitude": 79.1378},
    "Tiruchirappalli": {"latitude": 10.7905, "longitude": 78.7047},
    "Trichy": {"latitude": 10.7905, "longitude": 78.7047},
    "Theni": {"latitude": 10.0104, "longitude": 77.4768},
    "Krishnagiri": {"latitude": 12.5186, "longitude": 78.2137},
    "Vellore": {"latitude": 12.9165, "longitude": 79.1325},
    "Cuddalore": {"latitude": 11.7480, "longitude": 79.7714},
    "Villupuram": {"latitude": 11.9401, "longitude": 79.4861},
    "Tirunelveli": {"latitude": 8.7139, "longitude": 77.7567},
    "Thoothukudi": {"latitude": 8.7642, "longitude": 78.1348},
    "Kanyakumari": {"latitude": 8.0883, "longitude": 77.5385},
    "Chennai": {"latitude": 13.0827, "longitude": 80.2707},
}


class WeatherService:
    """Manages weather data ingestion and retrieval."""

    def __init__(self, db: Session):
        self.db = db
        self.open_meteo = WeatherProvider()
        self.nasa_power = NASAPowerProvider()

    def _resolve_coordinates(self, district: str) -> Optional[dict]:
        """Resolve coordinates from dictionary or database."""
        coords = DEFAULT_LOCATIONS.get(district)
        if not coords:
            for name, loc in DEFAULT_LOCATIONS.items():
                if name.lower() == district.lower():
                    return loc
            # Fallback to District model
            d_row = self.db.query(District).filter(District.name.ilike(district)).first()
            if d_row and d_row.latitude and d_row.longitude:
                return {"latitude": d_row.latitude, "longitude": d_row.longitude}
        return coords

    def ingest_forecast(self, district: str = "Erode", days: int = 7) -> int:
        """Fetch and store weather forecast."""
        coords = self._resolve_coordinates(district)
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
            existing = (
                self.db.query(WeatherData)
                .filter(
                    WeatherData.district == district,
                    WeatherData.date == d,
                )
                .first()
            )

            if existing:
                # Update forecast data
                existing.temperature_max = entry["temperature_max"]
                existing.temperature_min = entry["temperature_min"]
                existing.rainfall_mm = entry["rainfall_mm"] or 0
                existing.humidity = entry.get("humidity")
                existing.wind_speed = entry.get("wind_speed")
                stored += 1
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
        logger.info(f"Stored/updated {stored} weather entries for {district}")
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
            existing = (
                self.db.query(WeatherData)
                .filter(
                    WeatherData.district == district,
                    WeatherData.date == d,
                )
                .first()
            )

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
