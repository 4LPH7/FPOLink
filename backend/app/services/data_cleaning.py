"""Data cleaning utilities for market price data."""

import logging
from decimal import Decimal
from typing import List, Optional
from statistics import median

from app.data_sources.base import PriceRecord

logger = logging.getLogger(__name__)


def clean_price_records(records: List[PriceRecord]) -> List[PriceRecord]:
    """Clean and validate a list of price records."""
    cleaned = []
    for record in records:
        if _validate_record(record):
            record = _normalize_record(record)
            cleaned.append(record)
    
    logger.info(f"Cleaned {len(cleaned)}/{len(records)} records")
    return cleaned


def _validate_record(record: PriceRecord) -> bool:
    """Validate a price record."""
    # Must have positive modal price
    if not record.modal_price or record.modal_price <= 0:
        return False
    
    # Must have a valid date
    if not record.price_date:
        return False
    
    # Must have crop and market
    if not record.crop_name or not record.market_name:
        return False
    
    # Min should not exceed max
    if record.min_price and record.max_price:
        if record.min_price > record.max_price:
            return False
    
    return True


def _normalize_record(record: PriceRecord) -> PriceRecord:
    """Normalize a price record."""
    # Ensure min <= modal <= max
    if record.min_price > record.modal_price:
        record.min_price = record.modal_price
    if record.max_price < record.modal_price:
        record.max_price = record.modal_price
    
    # Normalize crop name
    record.crop_name = record.crop_name.lower().strip()
    
    # Normalize market name
    record.market_name = record.market_name.strip()
    
    return record


def detect_anomaly_mad(
    prices: List[Decimal],
    threshold: float = 3.0,
) -> List[bool]:
    """Detect anomalies using Median Absolute Deviation (MAD).
    
    More robust than mean/std for skewed, spiky price data.
    Returns a list of booleans: True = anomalous.
    """
    if len(prices) < 3:
        return [False] * len(prices)
    
    float_prices = [float(p) for p in prices]
    med = median(float_prices)
    
    # MAD = median(|x_i - median|)
    abs_deviations = [abs(p - med) for p in float_prices]
    mad = median(abs_deviations)
    
    if mad == 0:
        return [False] * len(prices)
    
    # Modified z-score using MAD
    # 0.6745 is the 0.75th quantile of the standard normal distribution
    results = []
    for p in float_prices:
        modified_z = 0.6745 * (p - med) / mad
        results.append(abs(modified_z) > threshold)
    
    return results
