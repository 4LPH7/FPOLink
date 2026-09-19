"""Base market data provider interface.

All data source adapters inherit from this and implement fetch_prices().
The adapter pattern means if a government site changes its HTML/API,
you only replace one adapter.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PriceRecord:
    """Standardized price record from any data source."""
    crop_name: str
    variety_name: Optional[str] = None
    market_name: str = ""
    district: str = ""
    state: str = "Tamil Nadu"
    min_price: Decimal = Decimal("0")
    max_price: Decimal = Decimal("0")
    modal_price: Decimal = Decimal("0")
    raw_price: Optional[Decimal] = None
    raw_unit: str = "kg"  # Original unit before conversion
    arrival_quantity: Optional[float] = None
    price_date: date = field(default_factory=date.today)
    source: str = ""
    raw_payload: Optional[dict] = None  # For raw_ingest storage


class MarketDataProvider(ABC):
    """Abstract base class for market data providers."""

    source_name: str = "unknown"

    @abstractmethod
    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Fetch price records for a crop in a district within a date range."""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if this data source is currently accessible."""
        return True
