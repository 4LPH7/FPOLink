"""NASA POWER provider — long-term weather history for ML training.

Free, no API key required.
Provides solar, temperature, precipitation data.
"""

import logging
from datetime import date
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


class NASAPowerProvider:
    """Fetch long-term weather history from NASA POWER."""

    def fetch_history(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """Fetch daily weather data from NASA POWER."""
        try:
            params = {
                "parameters": "T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M",
                "community": "AG",
                "longitude": longitude,
                "latitude": latitude,
                "start": start_date.strftime("%Y%m%d"),
                "end": end_date.strftime("%Y%m%d"),
                "format": "JSON",
            }

            with httpx.Client(timeout=60.0) as client:
                response = client.get(NASA_POWER_URL, params=params)
                response.raise_for_status()
                data = response.json()

            parameters = data.get("properties", {}).get("parameter", {})
            t2m_max = parameters.get("T2M_MAX", {})
            t2m_min = parameters.get("T2M_MIN", {})
            precip = parameters.get("PRECTOTCORR", {})
            humidity = parameters.get("RH2M", {})
            wind = parameters.get("WS2M", {})

            results = []
            for date_key in sorted(t2m_max.keys()):
                val_max = t2m_max.get(date_key)
                val_min = t2m_min.get(date_key)
                val_precip = precip.get(date_key)

                # NASA POWER uses -999 for missing data
                if val_max == -999 or val_min == -999:
                    continue

                results.append(
                    {
                        "date": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:]}",
                        "temperature_max": val_max,
                        "temperature_min": val_min,
                        "rainfall_mm": val_precip if val_precip != -999 else None,
                        "humidity": humidity.get(date_key)
                        if humidity.get(date_key) != -999
                        else None,
                        "wind_speed": wind.get(date_key) if wind.get(date_key) != -999 else None,
                    }
                )

            logger.info(f"Fetched {len(results)} days of NASA POWER data")
            return results

        except Exception as e:
            logger.error(f"NASA POWER error: {e}")
            return []
