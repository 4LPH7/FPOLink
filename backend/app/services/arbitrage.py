"""Inter-District Market Arbitrage and Transport Net Realization Engine.

Computes geographical distance (Haversine formula), freight cost estimates,
and net arbitrage margins across Tamil Nadu regulated agricultural markets.
"""

from datetime import date, timedelta
from decimal import Decimal
import math
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth's radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def find_market_arbitrage(
    db: Session,
    crop_id: UUID,
    origin_market_id: UUID,
    max_distance_km: float = 300.0,
    base_transport_cost: float = 50.0,  # Base loading/unloading fee per quintal
    rate_per_km_quintal: float = 1.20,  # Freight rate ₹/km/quintal
    days_window: int = 7,
) -> Dict:
    """Evaluate inter-district arbitrage opportunities for a crop from an origin mandi."""
    origin_market = db.query(Market).filter(Market.id == origin_market_id).first()
    crop = db.query(Crop).filter(Crop.id == crop_id).first()

    if not origin_market or not crop:
        return {"error": "Invalid origin market or crop ID", "opportunities": []}

    # Fetch newest price at origin
    origin_price_rec = (
        db.query(MarketPrice)
        .filter(MarketPrice.crop_id == crop_id, MarketPrice.market_id == origin_market_id)
        .order_by(MarketPrice.price_date.desc())
        .first()
    )

    if not origin_price_rec:
        return {
            "crop_id": str(crop_id),
            "crop_name": crop.name,
            "origin_market_id": str(origin_market_id),
            "origin_market_name": origin_market.name,
            "origin_price": None,
            "opportunities": [],
        }

    origin_price = float(origin_price_rec.modal_price)
    cutoff_date = origin_price_rec.price_date - timedelta(days=days_window)

    # Subquery for latest price in all other markets within recent days
    subq = (
        db.query(
            MarketPrice.market_id,
            func.max(MarketPrice.price_date).label("max_date"),
        )
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id != origin_market_id,
            MarketPrice.price_date >= cutoff_date,
        )
        .group_by(MarketPrice.market_id)
        .subquery()
    )

    candidate_prices = (
        db.query(MarketPrice, Market)
        .join(Market, MarketPrice.market_id == Market.id)
        .join(
            subq,
            (MarketPrice.market_id == subq.c.market_id)
            & (MarketPrice.price_date == subq.c.max_date),
        )
        .filter(MarketPrice.crop_id == crop_id)
        .all()
    )

    origin_lat = float(origin_market.latitude) if origin_market.latitude is not None else 11.3410
    origin_lon = float(origin_market.longitude) if origin_market.longitude is not None else 77.7172

    opportunities = []
    for mp, target_market in candidate_prices:
        target_lat = float(target_market.latitude) if target_market.latitude is not None else origin_lat
        target_lon = float(target_market.longitude) if target_market.longitude is not None else origin_lon

        distance_km = haversine_distance_km(origin_lat, origin_lon, target_lat, target_lon)
        if distance_km > max_distance_km:
            continue

        target_modal = float(mp.modal_price)
        gross_spread = round(target_modal - origin_price, 2)
        transport_cost = round(base_transport_cost + (distance_km * rate_per_km_quintal), 2)
        net_spread = round(gross_spread - transport_cost, 2)

        if net_spread >= 100.0:
            recommendation = "strong_arbitrage"
        elif net_spread > 0.0:
            recommendation = "profitable_dispatch"
        else:
            recommendation = "local_preferred"

        opportunities.append({
            "target_market_id": str(target_market.id),
            "target_market_name": target_market.name,
            "district": target_market.district,
            "target_price": target_modal,
            "price_date": mp.price_date.isoformat(),
            "distance_km": distance_km,
            "gross_spread": gross_spread,
            "transport_cost": transport_cost,
            "net_spread": net_spread,
            "recommendation": recommendation,
        })

    # Sort opportunities: highest net gain first
    opportunities.sort(key=lambda x: x["net_spread"], reverse=True)

    return {
        "crop_id": str(crop_id),
        "crop_name": crop.name,
        "crop_tamil_name": crop.tamil_name,
        "origin_market_id": str(origin_market_id),
        "origin_market_name": origin_market.name,
        "origin_district": origin_market.district,
        "origin_price": origin_price,
        "origin_price_date": origin_price_rec.price_date.isoformat(),
        "total_destinations_analyzed": len(opportunities),
        "opportunities": opportunities,
    }
