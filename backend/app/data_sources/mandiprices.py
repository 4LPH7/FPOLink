"""MandiPrices.co.in / Agmarknet web provider.

Parses daily wholesale mandi prices for Tamil Nadu from mandiprices.co.in,
which aggregates official Government of India Agmarknet data across 461 markets.
Supports loading from local cache (backend/data/mandiprices/) or live HTTP requests.
"""

import logging
import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

from app.data_sources.base import MarketDataProvider, PriceRecord

logger = logging.getLogger(__name__)

# Mapping from canonical crop name to mandiprices URL slug
CROP_SLUG_MAP: Dict[str, str] = {
    "turmeric": "turmeric",
    "banana": "banana",
    "coconut": "coconut",
    "tomato": "tomato",
    "tapioca": "tapioca",
    "maize": "maize",
    "onion": "onion",
    "small onion": "onion",
    "green chilli": "green-chilli",
    "ladies finger": "bhindi-ladies-finger",
    "brinjal": "brinjal",
    "paddy": "paddy-common",
    "groundnut": "groundnut",
    "cotton": "cotton",
    "ginger": "ginger-green",
    "mango": "mango",
}

CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mandiprices"


class MandiPricesProvider(MarketDataProvider):
    """Fetch daily mandi prices from MandiPrices / Agmarknet portal."""

    source_name = "agmarknet"

    def __init__(self, use_cache_first: bool = True):
        self.use_cache_first = use_cache_first

    def is_available(self) -> bool:
        return True

    def fetch_prices(
        self,
        crop: str,
        district: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PriceRecord]:
        """Fetch prices for a crop and district."""
        crop_clean = crop.lower().strip()
        slug = CROP_SLUG_MAP.get(crop_clean, crop_clean.replace(" ", "-"))

        html_content = self._get_html(slug)
        if not html_content:
            logger.warning(f"No HTML data available for crop {crop} (slug: {slug})")
            return []

        records = self._parse_table(html_content, crop_clean, district)

        # Apply date filters if provided
        filtered = []
        for r in records:
            if start_date and r.price_date < start_date:
                continue
            if end_date and r.price_date > end_date:
                continue
            filtered.append(r)

        logger.info(
            f"MandiPricesProvider parsed {len(filtered)} records for {crop} in district={district}"
        )
        return filtered

    def _get_html(self, slug: str) -> Optional[str]:
        """Load HTML from cache or live HTTP request."""
        # 1. Try local cache file
        cache_name = f"{slug.replace('-', '_')}.html"
        cache_file = CACHE_DIR / cache_name
        if not cache_file.exists():
            # Try alternate naming
            cache_file = CACHE_DIR / f"{slug}.html"

        if self.use_cache_first and cache_file.exists():
            try:
                return cache_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Error reading cache file {cache_file}: {e}")

        # 2. Try live HTTP request
        url = f"https://mandiprices.co.in/commodity/{slug}/tamil-nadu"
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    text = resp.text
                    # Save to cache
                    try:
                        CACHE_DIR.mkdir(parents=True, exist_ok=True)
                        cache_file.write_text(text, encoding="utf-8")
                    except Exception:
                        pass
                    return text
        except Exception as e:
            logger.warning(f"Live request to {url} failed: {e}")

        # 3. Fallback to cache even if use_cache_first was False
        if cache_file.exists():
            try:
                return cache_file.read_text(encoding="utf-8")
            except Exception:
                pass

        return None

    def _parse_table(
        self, html_content: str, crop_name: str, target_district: str
    ) -> List[PriceRecord]:
        """Parse the HTML table into standardized PriceRecord instances."""
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", class_="dt")
        if not table:
            return []

        tbody = table.find("tbody")
        if not tbody:
            return []

        records = []
        is_all_districts = not target_district or target_district.lower() == "all"
        target_dist_clean = target_district.lower().strip() if target_district else ""

        for row in tbody.find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 6:
                continue

            market_col = cols[0]
            district_col = cols[1]
            modal_str = cols[2]
            min_str = cols[3]
            max_str = cols[4]
            updated_str = cols[5]

            # District matching
            if not is_all_districts and target_dist_clean not in district_col.lower():
                continue

            # Parse prices in ₹/quintal -> convert to ₹/kg
            modal_dec = self._clean_price(modal_str)
            min_dec = self._clean_price(min_str)
            max_dec = self._clean_price(max_str)

            if modal_dec is None or modal_dec <= 0:
                continue

            quintal_to_kg = Decimal("100")
            modal_kg = modal_dec / quintal_to_kg
            min_kg = (min_dec / quintal_to_kg) if min_dec and min_dec > 0 else modal_kg
            max_kg = (max_dec / quintal_to_kg) if max_dec and max_dec > 0 else modal_kg

            # Parse date
            price_date = self._parse_date(updated_str)
            if not price_date:
                price_date = date.today()

            record = PriceRecord(
                crop_name=crop_name,
                variety_name=None,
                market_name=market_col,
                district=district_col,
                state="Tamil Nadu",
                min_price=min_kg,
                max_price=max_kg,
                modal_price=modal_kg,
                raw_price=modal_dec,
                raw_unit="quintal",
                price_date=price_date,
                source=self.source_name,
                raw_payload={
                    "market": market_col,
                    "district": district_col,
                    "modal_price": str(modal_dec),
                    "min_price": str(min_dec) if min_dec else None,
                    "max_price": str(max_dec) if max_dec else None,
                    "date": updated_str,
                    "crop": crop_name,
                    "source": "mandiprices_agmarknet",
                },
            )
            records.append(record)

        return records

    @staticmethod
    def _clean_price(price_str: str) -> Optional[Decimal]:
        """Convert '₹8,048' -> Decimal('8048')."""
        if not price_str:
            return None
        cleaned = re.sub(r"[^\d.]", "", price_str)
        if not cleaned:
            return None
        try:
            return Decimal(cleaned)
        except Exception:
            return None

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """Convert '25 Sep 2026' -> date(2026, 9, 25)."""
        if not date_str:
            return None
        # Common formats on MandiPrices
        for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                pass
        return None
