"""Explainable Data Quality Scoring Service for Mandi Prices."""

import datetime
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple


def calculate_quality_score(
    price_date: datetime.date,
    modal_price: Decimal,
    min_price: Decimal,
    max_price: Decimal,
    source: str,
    alias_confidence: float = 1.0,
    arrival_quantity: Optional[float] = None,
    reference_date: Optional[datetime.date] = None,
) -> Tuple[float, Dict[str, Any]]:
    """Compute an explainable data quality score (0.0 to 100.0) with granular component metrics.

    Components:
    1. Freshness (0.0 - 1.0): penalty for historical lag
    2. Source Reliability (0.0 - 1.0): based on verified official feeds
    3. Market Match (0.0 - 1.0): confidence of canonical market/crop resolution
    4. Completeness (0.0 - 1.0): presence of min, max, modal, arrival
    5. Outlier Penalty (0.0 - 0.5): logical contradiction or price dispersion
    """
    today = reference_date or datetime.date.today()

    # 1. Freshness
    age_days = (today - price_date).days if isinstance(price_date, datetime.date) else 0
    if age_days <= 0:
        freshness = 1.0
    elif age_days == 1:
        freshness = 0.95
    elif age_days <= 3:
        freshness = 0.80
    elif age_days <= 7:
        freshness = 0.60
    elif age_days <= 14:
        freshness = 0.40
    else:
        freshness = 0.20

    # 2. Source reliability
    source_lower = (source or "").lower()
    if source_lower in ("ogd", "agmarknet", "tn_agrinet"):
        source_reliability = 1.0
    elif source_lower == "ceda":
        source_reliability = 0.95
    elif source_lower == "manual_entry":
        source_reliability = 0.85
    else:
        source_reliability = 0.70

    # 3. Market match
    market_match = max(0.0, min(1.0, float(alias_confidence)))

    # 4. Completeness
    has_prices = (
        (modal_price is not None and modal_price > 0)
        and (min_price is not None)
        and (max_price is not None)
    )
    has_arrival = arrival_quantity is not None and arrival_quantity > 0
    if has_prices and has_arrival:
        completeness = 1.0
    elif has_prices:
        completeness = 0.85
    else:
        completeness = 0.50

    # 5. Outlier penalty
    outlier_penalty = 0.0
    try:
        if min_price > max_price or modal_price < min_price or modal_price > max_price:
            outlier_penalty += 0.35  # Logical price contradiction
        elif max_price > 0 and (max_price - min_price) / max_price > 0.8:
            outlier_penalty += 0.15  # Excessive price spread
    except Exception:
        outlier_penalty += 0.20

    # Overall weighted score
    raw_score = (
        (freshness * 0.30)
        + (source_reliability * 0.25)
        + (market_match * 0.25)
        + (completeness * 0.20)
        - outlier_penalty
    ) * 100.0

    score = round(max(0.0, min(100.0, raw_score)), 1)

    breakdown = {
        "freshness": round(freshness, 2),
        "source_reliability": round(source_reliability, 2),
        "market_match": round(market_match, 2),
        "completeness": round(completeness, 2),
        "outlier_penalty": round(outlier_penalty, 2),
        "age_days": age_days,
        "rating": "verified"
        if score >= 85
        else "good"
        if score >= 70
        else "limited"
        if score >= 50
        else "unreliable",
    }

    return score, breakdown
