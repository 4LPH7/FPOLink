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
    def parse_csv(csv_content: str, default_district: str = "Erode") -> List[PriceRecord]:
        """Parse bulk price records from CSV text."""
        import csv
        import io
        from datetime import datetime

        from app.utils.units import convert_to_per_kg

        records: List[PriceRecord] = []
        reader = csv.DictReader(io.StringIO(csv_content.strip()))

        def get_col(row: dict, keys: List[str], default: str = "") -> str:
            for k in keys:
                for row_k, v in row.items():
                    if row_k and row_k.strip().lower() == k.lower() and v:
                        return v.strip()
            return default

        for row in reader:
            crop_name = get_col(row, ["crop", "crop_name", "commodity", "commodity_name"])
            market_name = get_col(row, ["market", "market_name", "mandi"])
            district = get_col(row, ["district", "district_name"]) or default_district
            variety = get_col(row, ["variety", "variety_name"]) or None
            unit = get_col(row, ["unit", "raw_unit", "units"]) or "quintal"
            date_str = get_col(row, ["date", "price_date", "arrival_date"])

            min_p_str = get_col(row, ["min_price", "min", "minimum_price"])
            max_p_str = get_col(row, ["max_price", "max", "maximum_price"])
            modal_p_str = get_col(row, ["modal_price", "modal", "price"])

            if not (crop_name and market_name and modal_p_str and date_str):
                continue

            # Parse date (try YYYY-MM-DD first, then DD/MM/YYYY, DD-MM-YYYY)
            p_date = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
                try:
                    p_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            if not p_date:
                continue

            try:
                raw_modal = Decimal(modal_p_str)
                raw_min = Decimal(min_p_str) if min_p_str else raw_modal
                raw_max = Decimal(max_p_str) if max_p_str else raw_modal
            except Exception:
                continue

            # Convert to canonical ₹/kg using unit converter if specified
            try:
                modal_kg = convert_to_per_kg(raw_modal, unit)
                min_kg = convert_to_per_kg(raw_min, unit)
                max_kg = convert_to_per_kg(raw_max, unit)
            except Exception:
                modal_kg = raw_modal
                min_kg = raw_min
                max_kg = raw_max

            records.append(
                PriceRecord(
                    crop_name=crop_name.lower(),
                    variety_name=variety,
                    market_name=market_name,
                    district=district,
                    state="Tamil Nadu",
                    min_price=min_kg,
                    max_price=max_kg,
                    modal_price=modal_kg,
                    raw_price=raw_modal,
                    raw_unit=unit,
                    price_date=p_date,
                    source="manual",
                )
            )

        return records

    @classmethod
    def load_csv_file(cls, file_path, default_district: str = "Erode") -> List[PriceRecord]:
        """Load bulk records from a local CSV file path."""
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            logger.error(f"CSV file not found: {path}")
            return []
        with open(path, "r", encoding="utf-8-sig") as f:
            return cls.parse_csv(f.read(), default_district=default_district)
