"""CEDA Agri-Market provider (Ashoka University).

Parses the historical CSV data from CEDA's agricultural market dataset.
300+ commodities, 2,700+ mandis, 2000-present.
Fields: variety, grade, min/max/modal price in Rs per quintal.

This is the training-data goldmine for ML models.
"""

import csv
import logging
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from app.data_sources.base import MarketDataProvider, PriceRecord

logger = logging.getLogger(__name__)

# 1 quintal = 100 kg
QUINTAL_TO_KG = Decimal("100")


class CEDAProvider(MarketDataProvider):
    """Parse CEDA historical CSV data for price backfill."""

    source_name = "ceda"

    def __init__(
        self,
        data_dir: str = "ml/datasets",
        source_name: Optional[str] = None,
        allow_synthetic: bool = False,
    ):
        self.data_dir = data_dir
        self.source_name = source_name
        self.allow_synthetic = allow_synthetic

    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Parse CEDA CSV and return standardized price records.

        Expected CSV columns (may vary):
        State, District, Market, Commodity, Variety, Grade,
        Min Price, Max Price, Modal Price, Date

        Prices are in Rs/quintal — converted to Rs/kg.
        """
        records = []
        csv_path = self._find_csv(crop, district)
        if not csv_path:
            logger.warning(f"No CEDA CSV found for {crop} in {district}")
            return records

        # Guard against loading synthetic files when allow_synthetic is False
        lower_path = csv_path.lower()
        is_synthetic = "synthetic" in lower_path or "sample" in lower_path
        if is_synthetic and not self.allow_synthetic:
            logger.warning(f"Skipping synthetic CSV {csv_path} because allow_synthetic is False")
            return records

        # Tag synthetic or sample data to prevent contaminating ML datasets
        source = self.source_name
        if not source:
            if is_synthetic:
                source = "ceda_synthetic"
            else:
                source = "ceda"

        logger.info(f"Parsing CEDA CSV: {csv_path} (source: {source})")
        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    record = self._parse_row(
                        row, crop, district, start_date, end_date, source=source
                    )
                    if record:
                        records.append(record)
        except Exception as e:
            logger.error(f"Error parsing CEDA CSV: {e}")

        logger.info(f"Parsed {len(records)} price records from CEDA")
        return records

    def _find_csv(self, crop: str, district: str) -> Optional[str]:
        """Find a CEDA CSV file matching the crop/district."""
        # If data_dir is a direct file path
        if os.path.isfile(self.data_dir):
            if not self.allow_synthetic and (
                "synthetic" in self.data_dir.lower() or "sample" in self.data_dir.lower()
            ):
                return None
            return self.data_dir

        if not os.path.exists(self.data_dir):
            return None

        # Helper to check if file is synthetic
        def _is_synthetic(fname: str) -> bool:
            fl = fname.lower()
            return "synthetic" in fl or "sample" in fl

        # 1. Match specific crop
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".csv") and crop.lower() in filename.lower():
                if not self.allow_synthetic and _is_synthetic(filename):
                    continue
                return os.path.join(self.data_dir, filename)

        # 2. Match generic ceda file (only if allowed)
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".csv") and "ceda" in filename.lower():
                if not self.allow_synthetic and _is_synthetic(filename):
                    continue
                return os.path.join(self.data_dir, filename)

        return None

    def _parse_row(
        self,
        row: dict,
        crop: str,
        district: str,
        start_date: Optional[date],
        end_date: Optional[date],
        source: str = "ceda",
    ) -> Optional[PriceRecord]:
        """Parse a single CSV row into a PriceRecord."""
        try:
            # Flexible column name matching matching CEDA Agmarknet published schema:
            # date, state_name, district_name, market_name, commodity_name, variety, grade, min_price, max_price, modal_price
            row_commodity = self._get_field(
                row,
                [
                    "commodity_name",
                    "Commodity_Name",
                    "Commodity",
                    "commodity",
                    "COMMODITY",
                    "Crop",
                    "crop",
                ],
            )
            row_district = self._get_field(
                row,
                [
                    "district_name",
                    "District_Name",
                    "District",
                    "district",
                    "DISTRICT",
                ],
            )

            if not row_commodity or not row_district:
                return None

            # Filter by crop and district
            if crop.lower() not in row_commodity.lower():
                return None
            if district.lower() not in row_district.lower():
                return None

            # Parse date
            date_str = self._get_field(
                row,
                [
                    "date",
                    "Date",
                    "DATE",
                    "Price Date",
                    "price_date",
                    "Arrival_Date",
                    "arrival_date",
                ],
            )
            if not date_str:
                return None
            price_date = self._parse_date(date_str)
            if not price_date:
                return None

            # Apply date filter
            if start_date and price_date < start_date:
                return None
            if end_date and price_date > end_date:
                return None

            # Parse prices (Rs/quintal → Rs/kg)
            raw_modal = self._parse_decimal(
                self._get_field(
                    row,
                    [
                        "modal_price",
                        "Modal_Price",
                        "Modal Price",
                        "modal",
                        "Modal",
                    ],
                )
            )
            raw_min = self._parse_decimal(
                self._get_field(
                    row,
                    [
                        "min_price",
                        "Min_Price",
                        "Min Price",
                        "minimum",
                        "Minimum",
                    ],
                )
            )
            raw_max = self._parse_decimal(
                self._get_field(
                    row,
                    [
                        "max_price",
                        "Max_Price",
                        "Max Price",
                        "maximum",
                        "Maximum",
                    ],
                )
            )

            if raw_modal is None or raw_modal <= 0:
                return None

            # Convert quintal to kg
            modal_price = raw_modal / QUINTAL_TO_KG
            min_price = (raw_min / QUINTAL_TO_KG) if raw_min else modal_price
            max_price = (raw_max / QUINTAL_TO_KG) if raw_max else modal_price

            market_name = (
                self._get_field(
                    row,
                    [
                        "market_name",
                        "Market_Name",
                        "Market",
                        "market",
                        "MARKET",
                        "Market Center",
                    ],
                )
                or district
            )
            variety = self._get_field(row, ["variety", "Variety", "VARIETY"])
            # Arrival is separate in CEDA schema, optional in PriceRecord
            arrival = self._parse_float(
                self._get_field(
                    row, ["arrival", "Arrival", "arrivals", "Arrivals", "Arrival_Tonnes"]
                )
            )

            state_name = (
                self._get_field(row, ["state_name", "State_Name", "State", "state", "STATE"])
                or "Tamil Nadu"
            )

            return PriceRecord(
                crop_name=crop.lower(),
                variety_name=variety,
                market_name=market_name.strip(),
                district=district.strip(),
                state=state_name.strip(),
                min_price=min_price,
                max_price=max_price,
                modal_price=modal_price,
                raw_price=raw_modal,
                raw_unit="quintal",
                arrival_quantity=arrival,
                price_date=price_date,
                source=source,
                raw_payload=dict(row),
            )
        except Exception as e:
            logger.debug(f"Skipping row: {e}")
            return None

    @staticmethod
    def _get_field(row: dict, possible_keys: list) -> Optional[str]:
        """Try multiple possible column names."""
        for key in possible_keys:
            if key in row and row[key]:
                return row[key].strip()
        return None

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """Try multiple date formats."""
        formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
        if not value:
            return None
        try:
            return Decimal(value.strip().replace(",", ""))
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _parse_float(value: Optional[str]) -> Optional[float]:
        if not value:
            return None
        try:
            return float(value.strip().replace(",", ""))
        except ValueError:
            return None
