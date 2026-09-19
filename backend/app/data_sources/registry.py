"""Data source registry — manages provider fallback chain."""

import logging
from datetime import date
from typing import List, Optional

from app.data_sources.base import MarketDataProvider, PriceRecord
from app.data_sources.ceda import CEDAProvider
from app.data_sources.ogd import OGDProvider
from app.data_sources.manual import ManualProvider

logger = logging.getLogger(__name__)


class DataSourceRegistry:
    """Manages data source providers with fallback chain.

    Priority: OGD (live API) → CEDA (historical) → Manual
    Agmarknet scraping is intentionally omitted as default —
    add only if API sources are insufficient.
    """

    def __init__(self):
        self.providers: List[MarketDataProvider] = [
            OGDProvider(),
            CEDAProvider(),
            ManualProvider(),
        ]

    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Fetch prices from all available providers.

        Uses fallback chain: tries each provider in priority order.
        Returns results from the first provider that returns data.
        """
        for provider in self.providers:
            if not provider.is_available():
                logger.info(f"Provider {provider.source_name} not available, skipping")
                continue

            try:
                records = provider.fetch_prices(crop, district, start_date, end_date)
                if records:
                    logger.info(
                        f"Got {len(records)} records from {provider.source_name} "
                        f"for {crop} in {district}"
                    )
                    return records
            except Exception as e:
                logger.error(f"Provider {provider.source_name} failed: {e}")
                continue

        logger.warning(f"No data found for {crop} in {district} from any provider")
        return []

    def fetch_all(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Fetch from ALL available providers (not just first success)."""
        all_records = []
        for provider in self.providers:
            if not provider.is_available():
                continue
            try:
                records = provider.fetch_prices(crop, district, start_date, end_date)
                all_records.extend(records)
            except Exception as e:
                logger.error(f"Provider {provider.source_name} failed: {e}")
        return all_records
