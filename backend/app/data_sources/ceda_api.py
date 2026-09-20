"""CEDA Data Portal API provider (Ashoka University).

Programmatic access to raw Agmarknet agricultural market data:
- Base URL: https://api.ceda.ashoka.edu.in/v1
- Auth: Authorization: Bearer <CEDA_API_KEY>
- Endpoints:
    GET  /agmarknet/commodities
    GET  /agmarknet/geographies
    POST /agmarknet/markets
    POST /agmarknet/prices
    POST /agmarknet/quantities
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings
from app.data_sources.base import MarketDataProvider, PriceRecord

logger = logging.getLogger(__name__)

CEDA_API_BASE_URL = "https://api.ceda.ashoka.edu.in/v1"
QUINTAL_TO_KG = Decimal("100")

# Known Census 2011 codes for Tamil Nadu & Erode
TN_CENSUS_STATE_ID = 33
ERODE_CENSUS_DISTRICT_ID = 610


class CEDAAPIProvider(MarketDataProvider):
    """Fetch live or historical prices from CEDA Agmarknet Data Portal API."""

    source_name = "ceda"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = CEDA_API_BASE_URL,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or settings.CEDA_API_KEY
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "FPOLink/1.0",
        }

    def get_commodities(self) -> List[Dict[str, Any]]:
        """Retrieve list of all commodities: [{"id": int, "name": str}]."""
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}/agmarknet/commodities",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("commodities", [])
        except Exception as e:
            logger.error(f"Error fetching CEDA commodities: {e}")
            return []

    def get_geographies(self) -> List[Dict[str, Any]]:
        """Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}]"""
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}/agmarknet/geographies",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("geographies", [])
        except Exception as e:
            logger.error(f"Error fetching CEDA geographies: {e}")
            return []

    def fetch_prices(
        self,
        crop: str,
        district: str = "Erode",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        commodity_id: Optional[int] = None,
        state_id: int = TN_CENSUS_STATE_ID,
        district_id: Optional[int] = ERODE_CENSUS_DISTRICT_ID,
        market_ids: Optional[List[int]] = None,
    ) -> List[PriceRecord]:
        """Fetch prices from CEDA API.

        Requires integer commodity_id. If not passed, attempts to discover
        commodity_id via get_commodities() matching the crop name.
        """
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        # Resolve commodity_id if needed
        cid = commodity_id
        if cid is None:
            commodities = self.get_commodities()
            for item in commodities:
                if crop.lower() in item.get("name", "").lower():
                    cid = item.get("id")
                    break

        if cid is None:
            logger.error(f"Could not resolve CEDA commodity_id for '{crop}'")
            return []

        from_str = start_date.isoformat() if start_date else "2024-01-01"
        to_str = end_date.isoformat() if end_date else date.today().isoformat()

        payload: Dict[str, Any] = {
            "commodity_id": cid,
            "state_id": state_id,
            "from_date": from_str,
            "to_date": to_str,
        }
        if district_id is not None:
            payload["district_id"] = [district_id]
        if market_ids:
            payload["market_id"] = market_ids

        records: List[PriceRecord] = []
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/agmarknet/prices",
                    json=payload,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()

            for item in data.get("data", []):
                record = self._parse_api_item(item, crop, district)
                if record:
                    records.append(record)

            logger.info(f"Fetched {len(records)} records from CEDA API for {crop} in {district}")
        except Exception as e:
            logger.error(f"Error fetching prices from CEDA API: {e}")

        return records

    def _parse_api_item(self, item: dict, crop: str, district: str) -> Optional[PriceRecord]:
        """Parse CEDA API JSON item into standardized PriceRecord."""
        try:
            raw_modal = Decimal(str(item.get("modal_price", 0)))
            raw_min = Decimal(str(item.get("min_price", raw_modal)))
            raw_max = Decimal(str(item.get("max_price", raw_modal)))

            if raw_modal <= 0:
                return None

            # Prices in Rs/quintal -> Rs/kg
            modal_price = raw_modal / QUINTAL_TO_KG
            min_price = raw_min / QUINTAL_TO_KG
            max_price = raw_max / QUINTAL_TO_KG

            date_val = date.fromisoformat(item["date"])
            market_id = item.get("market_id")
            market_name = str(item.get("market_name") or f"Mandi {market_id or district}")

            return PriceRecord(
                crop_name=crop.lower(),
                variety_name=item.get("variety"),
                market_name=market_name,
                district=district,
                state="Tamil Nadu",
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
                raw_price=raw_modal,
                raw_unit="quintal",
                arrival_quantity=float(item.get("quantity", 0)) if "quantity" in item else None,
                price_date=date_val,
                source="ceda",
                raw_payload=item,
            )
        except Exception as e:
            logger.debug(f"Skipping CEDA API item {item}: {e}")
            return None
