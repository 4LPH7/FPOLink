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

# All 38 Tamil Nadu Revenue Districts coordinates for Open-Meteo & NASA POWER
DEFAULT_LOCATIONS = {
    "Ariyalur": {"latitude": 11.1401, "longitude": 79.0786},
    "Chengalpattu": {"latitude": 12.6841, "longitude": 79.9836},
    "Chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "Coimbatore": {"latitude": 11.0168, "longitude": 76.9558},
    "Cuddalore": {"latitude": 11.7480, "longitude": 79.7714},
    "Dharmapuri": {"latitude": 12.1211, "longitude": 78.1582},
    "Dindigul": {"latitude": 10.3673, "longitude": 77.9803},
    "Erode": {"latitude": 11.3410, "longitude": 77.7172},
    "Kallakurichi": {"latitude": 11.7383, "longitude": 78.9639},
    "Kanchipuram": {"latitude": 12.8342, "longitude": 79.7036},
    "Kanyakumari": {"latitude": 8.0883, "longitude": 77.5385},
    "Karur": {"latitude": 10.9601, "longitude": 78.0766},
    "Krishnagiri": {"latitude": 12.5186, "longitude": 78.2137},
    "Madurai": {"latitude": 9.9252, "longitude": 78.1198},
    "Mayiladuthurai": {"latitude": 11.1075, "longitude": 79.6522},
    "Nagapattinam": {"latitude": 10.7656, "longitude": 79.8424},
    "Namakkal": {"latitude": 11.2189, "longitude": 78.1674},
    "Nilgiris": {"latitude": 11.4102, "longitude": 76.6950},
    "Perambalur": {"latitude": 11.2342, "longitude": 78.8820},
    "Pudukkottai": {"latitude": 10.3833, "longitude": 78.8001},
    "Ramanathapuram": {"latitude": 9.3639, "longitude": 78.8395},
    "Ranipet": {"latitude": 12.9272, "longitude": 79.3331},
    "Salem": {"latitude": 11.6643, "longitude": 78.1460},
    "Sivaganga": {"latitude": 9.8433, "longitude": 78.4809},
    "Tenkasi": {"latitude": 8.9594, "longitude": 77.3152},
    "Thanjavur": {"latitude": 10.7870, "longitude": 79.1378},
    "Theni": {"latitude": 10.0104, "longitude": 77.4768},
    "Thoothukudi": {"latitude": 8.7642, "longitude": 78.1348},
    "Tiruchirappalli": {"latitude": 10.7905, "longitude": 78.7047},
    "Trichy": {"latitude": 10.7905, "longitude": 78.7047},
    "Tirunelveli": {"latitude": 8.7139, "longitude": 77.7567},
    "Tirupathur": {"latitude": 12.4958, "longitude": 78.5678},
    "Tiruppur": {"latitude": 11.1085, "longitude": 77.3411},
    "Thirupur": {"latitude": 11.1085, "longitude": 77.3411},
    "Tiruvallur": {"latitude": 13.1432, "longitude": 79.9079},
    "Tiruvannamalai": {"latitude": 12.2253, "longitude": 79.0747},
    "Tiruvarur": {"latitude": 10.7725, "longitude": 79.6368},
    "Vellore": {"latitude": 12.9165, "longitude": 79.1325},
    "Viluppuram": {"latitude": 11.9401, "longitude": 79.4861},
    "Virudhunagar": {"latitude": 9.5680, "longitude": 77.9624},
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
