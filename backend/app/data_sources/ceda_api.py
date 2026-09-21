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
import time
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

# Known commodity IDs to avoid list-everything calls
KNOWN_COMMODITY_IDS: Dict[str, int] = {
    "turmeric": 14,
    "banana": 22,
}


class CEDAAPIProvider(MarketDataProvider):
    """Fetch live or historical prices from CEDA Agmarknet Data Portal API."""

    source_name = "ceda"

    # Circuit breaker state shared across instances
    _failure_count: int = 0
    _circuit_open_until: float = 0.0
    failure_threshold: int = 3
    cooldown_seconds: float = 300.0  # 5 minute cooldown

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = CEDA_API_BASE_URL,
        timeout: float = 15.0,
        connect_timeout: float = 5.0,
        max_retries: int = 2,
    ) -> None:
        self.api_key = api_key or settings.CEDA_API_KEY
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries

    def is_available(self) -> bool:
        return bool(self.api_key)

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is currently tripped."""
        now = time.time()
        if now < self.__class__._circuit_open_until:
            return True
        return False

    def reset_circuit(self) -> None:
        """Reset circuit breaker state (useful for tests or recovery)."""
        self.__class__._failure_count = 0
        self.__class__._circuit_open_until = 0.0

    def _record_failure(self) -> None:
        self.__class__._failure_count += 1
        threshold = getattr(self, "failure_threshold", self.__class__.failure_threshold)
        cooldown = getattr(self, "cooldown_seconds", self.__class__.cooldown_seconds)
        if self.__class__._failure_count >= threshold:
            self.__class__._circuit_open_until = time.time() + cooldown
            logger.warning(
                f"CEDA API circuit breaker TRIPPED ({self.__class__._failure_count} consecutive failures). "
                f"Fast-failing calls for {cooldown}s."
            )

    def _record_success(self) -> None:
        if self.__class__._failure_count > 0:
            self.__class__._failure_count = 0

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "FPOLink/1.0",
        }

    def _request_with_retry(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        """Execute HTTP request with short timeout, retries, and circuit breaker."""
        if self.is_circuit_open():
            logger.warning("CEDA API circuit breaker is OPEN; fast-failing request")
            return None

        client_timeout = httpx.Timeout(self.timeout, connect=self.connect_timeout)
        attempts = 0
        last_exception = None

        while attempts <= self.max_retries:
            attempts += 1
            try:
                with httpx.Client(timeout=client_timeout) as client:
                    resp = client.request(method, url, headers=self._headers(), **kwargs)
                    if resp.status_code in (502, 503, 504):
                        logger.warning(
                            f"CEDA API returned {resp.status_code} (attempt {attempts}/{self.max_retries + 1})"
                        )
                        if attempts <= self.max_retries:
                            time.sleep(0.3 * attempts)
                            continue
                        resp.raise_for_status()
                    resp.raise_for_status()
                    self._record_success()
                    return resp
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (502, 503, 504):
                    last_exception = e
                    logger.warning(f"CEDA API transient HTTP error: {e} (attempt {attempts})")
                    if attempts <= self.max_retries:
                        time.sleep(0.3 * attempts)
                        continue
                elif 400 <= e.response.status_code < 500:
                    # Non-transient 4xx errors (401, 403, 422, etc.) propagate immediately
                    # and must not increment circuit breaker failure state
                    logger.error(
                        f"CEDA API non-transient 4xx HTTP error {e.response.status_code}: {e}"
                    )
                    raise
                else:
                    # Other 5xx server errors (e.g. 500) are not retried but are recorded as failures
                    last_exception = e
                    logger.error(f"CEDA API server error {e.response.status_code}: {e}")
                    break
            except (httpx.TimeoutException, httpx.TransportError) as e:
                # Keep transport-error retries separate
                last_exception = e
                logger.warning(f"CEDA API transport error: {e} (attempt {attempts})")
                if attempts <= self.max_retries:
                    time.sleep(0.3 * attempts)
                    continue
            except Exception as e:
                last_exception = e
                break

        # All attempts exhausted
        logger.error(f"CEDA API request to {url} failed: {last_exception}")
        self._record_failure()
        return None

    def get_commodities(self) -> List[Dict[str, Any]]:
        """Retrieve list of all commodities: [{"id": int, "name": str}]."""
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        resp = self._request_with_retry("GET", f"{self.base_url}/agmarknet/commodities")
        if resp is not None:
            try:
                data = resp.json()
                return data.get("commodities", [])
            except Exception as e:
                logger.error(f"Error parsing CEDA commodities JSON: {e}")
        return []

    def get_geographies(self) -> List[Dict[str, Any]]:
        """Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}]"""
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        resp = self._request_with_retry("GET", f"{self.base_url}/agmarknet/geographies")
        if resp is not None:
            try:
                data = resp.json()
                return data.get("geographies", [])
            except Exception as e:
                logger.error(f"Error parsing CEDA geographies JSON: {e}")
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
        """Fetch prices from CEDA API with narrow query targeting."""
        if not self.is_available():
            logger.warning("CEDA API key not configured")
            return []

        # Resolve commodity_id: first check known mapping, then query API
        cid = commodity_id
        if cid is None:
            cid = KNOWN_COMMODITY_IDS.get(crop.lower().strip())

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
        resp = self._request_with_retry("POST", f"{self.base_url}/agmarknet/prices", json=payload)
        if resp is not None:
            try:
                data = resp.json()
                for item in data.get("data", []):
                    record = self._parse_api_item(item, crop, district)
                    if record:
                        records.append(record)
                logger.info(
                    f"Fetched {len(records)} records from CEDA API for {crop} in {district}"
                )
            except Exception as e:
                logger.error(f"Error parsing CEDA price records JSON: {e}")

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
