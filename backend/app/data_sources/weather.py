"""Weather data provider using Open-Meteo (free, no API key).

Note: Open-Meteo is free for non-commercial use only.
Check terms if the FPO will pay for the service.
"""

import logging
from datetime import date, timedelta
from typing import Optional, List, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WeatherProvider:
    """Fetch weather data from Open-Meteo API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OPEN_METEO_BASE_URL

    def fetch_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Fetch weather forecast for the next N days."""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max",
                        "timezone": "Asia/Kolkata",
                        "forecast_days": days,
                    },
                )
                response.raise_for_status()
                data = response.json()

            daily = data.get("daily", {})
            dates = daily.get("time", [])
            results = []
            for i, d in enumerate(dates):
                results.append({
                    "date": d,
                    "temperature_max": daily.get("temperature_2m_max", [None])[i],
                    "temperature_min": daily.get("temperature_2m_min", [None])[i],
                    "rainfall_mm": daily.get("precipitation_sum", [None])[i],
                    "humidity": daily.get("relative_humidity_2m_mean", [None])[i],
                    "wind_speed": daily.get("wind_speed_10m_max", [None])[i],
                })

            logger.info(f"Fetched {len(results)} days of weather forecast")
            return results

        except Exception as e:
            logger.error(f"Weather forecast error: {e}")
            return []

    def fetch_history(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """Fetch historical weather data."""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/archive",  # Open-Meteo historical endpoint
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max",
                        "timezone": "Asia/Kolkata",
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    },
                )
                response.raise_for_status()
                data = response.json()

            daily = data.get("daily", {})
            dates = daily.get("time", [])
            results = []
            for i, d in enumerate(dates):
                results.append({
                    "date": d,
                    "temperature_max": daily.get("temperature_2m_max", [None])[i],
                    "temperature_min": daily.get("temperature_2m_min", [None])[i],
                    "rainfall_mm": daily.get("precipitation_sum", [None])[i],
                    "humidity": daily.get("relative_humidity_2m_mean", [None])[i],
                    "wind_speed": daily.get("wind_speed_10m_max", [None])[i],
                })

            logger.info(f"Fetched {len(results)} days of weather history")
            return results

        except Exception as e:
            logger.error(f"Weather history error: {e}")
            return []
