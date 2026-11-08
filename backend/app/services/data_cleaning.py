"""Data cleaning utilities for market price data."""

from decimal import Decimal
from statistics import median
from typing import List


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
