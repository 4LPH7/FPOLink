"""Manual data provider — FPO staff manually enters observed prices."""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.data_sources.base import MarketDataProvider, PriceRecord

logger = logging.getLogger(__name__)


class ManualProvider(MarketDataProvider):
    """Handles manually-entered price data from FPO staff."""

    source_name = "manual"

    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Manual prices are entered via API, not fetched.

        This provider returns an empty list — manual entries
        go directly through the price API endpoint.
        """
        return []

    @staticmethod
    def create_manual_record(
        crop_name: str,
        market_name: str,
        district: str,
        min_price: Decimal,
        max_price: Decimal,
        modal_price: Decimal,
        price_date: date,
    ) -> PriceRecord:
        """Create a PriceRecord from manual entry."""
        return PriceRecord(
            crop_name=crop_name,
            market_name=market_name,
            district=district,
            min_price=min_price,
            max_price=max_price,
            modal_price=modal_price,
            raw_price=modal_price,
            raw_unit="kg",
            price_date=price_date,
            source="manual",
        )
