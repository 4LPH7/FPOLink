"""Open Government Data (data.gov.in) provider.

Fetches daily wholesale mandi prices from the OGD platform.
Requires a free API key from data.gov.in.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional

import httpx

from app.config import settings
from app.data_sources.base import MarketDataProvider, PriceRecord

logger = logging.getLogger(__name__)

# data.gov.in resource for daily prices
OGD_BASE_URL = "https://api.data.gov.in/resource"
# Note: The exact resource ID needs to be verified. There are multiple
# mandi price datasets on data.gov.in. The one sourced from Agmarknet
# typically has fields: State, District, Market, Commodity, Variety,
# Arrival_Date, Min_Price, Max_Price, Modal_Price.
OGD_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Verify this


class OGDProvider(MarketDataProvider):
    """Fetch daily mandi prices from data.gov.in OGD API."""

    source_name = "ogd"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OGD_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Fetch prices from data.gov.in API."""
        if not self.is_available():
            logger.warning("OGD API key not configured. Skipping.")
            return []

        records = []
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": 1000,
                "filters[State.keyword]": "Tamil Nadu",
                "filters[District.keyword]": district,
                "filters[Commodity.keyword]": crop.capitalize(),
            }

            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{OGD_BASE_URL}/{OGD_RESOURCE_ID}",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            for record in data.get("records", []):
                parsed = self._parse_record(record, crop, district)
                if parsed:
                    # Apply date filter
                    if start_date and parsed.price_date < start_date:
                        continue
                    if end_date and parsed.price_date > end_date:
                        continue
                    records.append(parsed)

            logger.info(f"Fetched {len(records)} records from OGD for {crop} in {district}")

        except httpx.HTTPError as e:
            logger.error(f"OGD API error: {e}")
        except Exception as e:
            logger.error(f"Error fetching from OGD: {e}")

        return records

    def _parse_record(self, record: dict, crop: str, district: str) -> Optional[PriceRecord]:
        """Parse an OGD API record into a PriceRecord."""
        try:
            from app.data_sources.ceda import CEDAProvider

            record_commodity = self._get_field(
                record, ["commodity", "Commodity", "COMMODITY", "Crop", "crop"]
            )
            if record_commodity and crop.lower() not in record_commodity.lower():
                return None

            record_district = self._get_field(record, ["district", "District", "DISTRICT"])
            if record_district and district.lower() not in record_district.lower():
                return None

            raw_modal_str = self._get_field(
                record,
                [
                    "modal_price",
                    "Modal_Price",
                    "Modal Price",
                    "Modal_x0020_Price",
                    "Modal",
                    "modalPrice",
                ],
            )
            raw_min_str = self._get_field(
                record,
                ["min_price", "Min_Price", "Min Price", "Min_x0020_Price", "Minimum", "minPrice"],
            )
            raw_max_str = self._get_field(
                record,
                ["max_price", "Max_Price", "Max Price", "Max_x0020_Price", "Maximum", "maxPrice"],
            )

            raw_modal = CEDAProvider._parse_decimal(raw_modal_str)
            if raw_modal is None or raw_modal <= 0:
                return None

            raw_min = CEDAProvider._parse_decimal(raw_min_str)
            raw_max = CEDAProvider._parse_decimal(raw_max_str)

            # Convert quintal to kg
            quintal_to_kg = Decimal("100")
            modal_price = raw_modal / quintal_to_kg
            min_price = (raw_min / quintal_to_kg) if raw_min else modal_price
            max_price = (raw_max / quintal_to_kg) if raw_max else modal_price

            # Parse date
            date_str = self._get_field(
                record,
                ["arrival_date", "Arrival_Date", "Arrival Date", "Date", "date", "Price Date"],
            )
            if not date_str:
                return None

            price_date = CEDAProvider._parse_date(date_str)
            if not price_date:
                return None

            market = (
                self._get_field(
                    record, ["market", "Market", "Market Center", "MARKET", "market_center"]
                )
                or district
            )
            variety = self._get_field(record, ["variety", "Variety", "VARIETY"])

            return PriceRecord(
                crop_name=crop.lower(),
                variety_name=variety,
                market_name=market.strip(),
                district=district.strip(),
                state=self._get_field(record, ["state", "State", "STATE"]) or "Tamil Nadu",
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
                raw_price=raw_modal,
                raw_unit="quintal",
                price_date=price_date,
                source="ogd",
                raw_payload=record,
            )
        except Exception as e:
            logger.debug(f"Skipping OGD record: {e}")
            return None

    @staticmethod
    def _get_field(record: dict, keys: list) -> Optional[str]:
        """Case-tolerant field retriever."""
        for key in keys:
            if key in record and record[key] is not None:
                val = str(record[key]).strip()
                if val:
                    return val
        # Case-insensitive scan
        record_lower = {k.lower(): str(v).strip() for k, v in record.items() if v is not None}
        for key in keys:
            if key.lower() in record_lower and record_lower[key.lower()]:
                return record_lower[key.lower()]
        return None
