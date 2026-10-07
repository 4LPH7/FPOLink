"""Inter-District Market Arbitrage and Transport Net Realization Engine.

Computes geographical distance (Haversine formula), configurable freight profiles,
itemized cost deductions (handling, mandi fees, transit spoilage), variety alignment,
and defensible net arbitrage margins across Tamil Nadu regulated agricultural markets.
"""

import math
from datetime import timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.variety import Variety

# Standard commercial transport vehicle presets for Tamil Nadu agricultural corridors
VEHICLE_PROFILES = {
    "pickup": {
        "name": "Pickup / Mini Truck (Tata Ace)",
        "capacity_quintals": 15.0,
        "base_cost_per_qtl": 35.0,
        "rate_per_km_quintal": 2.00,
        "min_shipment_qtl": 5.0,
    },
    "lcv": {
        "name": "Light Commercial Vehicle (LCV / 407)",
        "capacity_quintals": 35.0,
        "base_cost_per_qtl": 50.0,
        "rate_per_km_quintal": 1.20,
        "min_shipment_qtl": 10.0,
    },
    "medium_truck": {
        "name": "Medium Truck (6-Wheeler)",
        "capacity_quintals": 100.0,
        "base_cost_per_qtl": 25.0,
        "rate_per_km_quintal": 0.85,
        "min_shipment_qtl": 30.0,
    },
}

DISCLAIMER_TA = (
    "இது மதிப்பிடப்பட்ட சாத்தியக்கூறு மட்டுமே; போக்குவரத்து கட்டணம், தரம் மற்றும் "
    "சந்தை கட்டணங்களின் அடிப்படையில் மாறுபடலாம்."
)

DISCLAIMER_EN = (
    "Estimated net opportunities based on reported mandi modal prices. "
    "Does not guarantee realized trading profit; actual outcomes depend on vehicle capacity, "
    "live arrival volumes, transporter quotes, and quality grading."
)


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    r = 6371.0  # Earth's radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 1)


def get_default_spoilage_risk(crop: Crop) -> float:
    """Determine default transit shrinkage/spoilage percentage based on crop perishability."""
    name_lower = (crop.name or "").lower()
    cat_lower = (crop.category or "").lower()
    perish_lower = (crop.perishability or "").lower()

    # Highly perishable: banana, vegetables, horticulture
    if (
        "banana" in name_lower
        or "tomato" in name_lower
        or "vegetable" in cat_lower
        or perish_lower == "high"
        or crop.is_horticulture
    ):
        return 3.0
    # Semi-perishable: coconut, sugarcane, fresh fruit
    if "coconut" in name_lower or "sugarcane" in name_lower or perish_lower == "medium":
        return 1.0
    # Durable: turmeric, grains, pulses, spices, commercial dry crops
    return 0.0


def compute_uncertainty_score(
    distance_km: float,
    date_diff_days: int,
    variety_match: str,
    spoilage_cost: float,
    spoilage_risk_pct: float,
    arrival_quantity: Optional[float] = None,
) -> tuple[int, str, List[str]]:
    """Compute multi-factor uncertainty score, discrete rating, and explanatory reasons."""
    reasons = []
    points = 0

    # 1. Distance risk
    if distance_km > 250.0:
        points += 30
        reasons.append(f"Long transit distance ({distance_km} km > 250 km)")
    elif distance_km > 150.0:
        points += 15
        reasons.append(f"Moderate transit distance ({distance_km} km)")

    # 2. Date disparity / recency risk
    if date_diff_days > 4:
        points += 35
        reasons.append(f"Observation lag of {date_diff_days} days at destination mandi")
    elif date_diff_days > 2:
        points += 20
        reasons.append(f"Observation lag of {date_diff_days} days at destination mandi")

    # 3. Variety match alignment
    if variety_match == "cross_variety_approximate":
        points += 25
        reasons.append("Cross-variety approximate comparison (grade price spread risk)")

    # 4. Spoilage risk for perishables
    if spoilage_cost > 0.0:
        points += 10
        reasons.append(f"Transit spoilage risk ({spoilage_risk_pct}%) applied")

    # 5. Thin destination volume liquidity
    if arrival_quantity is not None and float(arrival_quantity) < 5.0:
        points += 15
        reasons.append(f"Thin destination arrival liquidity ({arrival_quantity} tonnes)")

    # Categorize discrete rating
    if points < 30:
        rating = "low"
    elif points < 60:
        rating = "moderate"
    else:
        rating = "high"

    return points, rating, reasons


def find_market_arbitrage(
    db: Session,
    crop_id: UUID,
    origin_market_id: UUID,
    max_distance_km: float = 300.0,
    vehicle_profile: str = "lcv",
    base_transport_cost: Optional[float] = None,
    rate_per_km_quintal: Optional[float] = None,
    handling_cost_per_qtl: Optional[float] = None,
    commission_pct: Optional[float] = None,
    spoilage_risk_pct: Optional[float] = None,
    min_shipment_qtl: Optional[float] = None,
    days_window: int = 7,
) -> Dict:
    """Evaluate inter-district arbitrage opportunities for a crop with defensible cost modeling."""
    from app.core.sources import get_real_price_sources

    origin_market = db.query(Market).filter(Market.id == origin_market_id).first()
    crop = db.query(Crop).filter(Crop.id == crop_id).first()

    if not origin_market or not crop:
        return {"error": "Invalid origin market or crop ID", "opportunities": []}

    # Resolve vehicle preset parameters
    profile_data = VEHICLE_PROFILES.get(vehicle_profile, VEHICLE_PROFILES["lcv"])
    if base_transport_cost is None:
        base_transport_cost = profile_data["base_cost_per_qtl"]
    if rate_per_km_quintal is None:
        rate_per_km_quintal = profile_data["rate_per_km_quintal"]
    if min_shipment_qtl is None:
        min_shipment_qtl = profile_data["min_shipment_qtl"]

    # Handling, commission, and commodity-specific spoilage defaults
    if handling_cost_per_qtl is None:
        handling_cost_per_qtl = 0.0
    if commission_pct is None:
        commission_pct = 0.0
    if spoilage_risk_pct is None:
        spoilage_risk_pct = get_default_spoilage_risk(crop)

    # Fetch newest verified price at origin
    origin_price_rec = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == origin_market_id,
            MarketPrice.source.in_(get_real_price_sources()),
        )
        .order_by(MarketPrice.price_date.desc())
        .first()
    )

    if not origin_price_rec:
        return {
            "crop_id": str(crop_id),
            "crop_name": crop.name,
            "crop_tamil_name": crop.tamil_name,
            "origin_market_id": str(origin_market_id),
            "origin_market_name": origin_market.name,
            "origin_district": origin_market.district,
            "origin_price": None,
            "opportunities": [],
            "disclaimer_ta": DISCLAIMER_TA,
            "disclaimer_en": DISCLAIMER_EN,
        }

    origin_price = float(origin_price_rec.modal_price)
    origin_variety_id = origin_price_rec.variety_id
    origin_variety = (
        db.query(Variety).filter(Variety.id == origin_variety_id).first()
        if origin_variety_id
        else None
    )
    origin_variety_name = origin_variety.name if origin_variety else None

    cutoff_date = origin_price_rec.price_date - timedelta(days=days_window)

    # Subquery for latest price in all other reporting markets within the window
    subq = (
        db.query(
            MarketPrice.market_id,
            func.max(MarketPrice.price_date).label("max_date"),
        )
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id != origin_market_id,
            MarketPrice.source.in_(get_real_price_sources()),
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
        .filter(
            MarketPrice.crop_id == crop_id,
            MarketPrice.source.in_(get_real_price_sources()),
        )
        .all()
    )

    origin_lat = float(origin_market.latitude) if origin_market.latitude is not None else 11.3410
    origin_lon = float(origin_market.longitude) if origin_market.longitude is not None else 77.7172

    opportunities = []
    for mp, target_market in candidate_prices:
        target_lat = (
            float(target_market.latitude) if target_market.latitude is not None else origin_lat
        )
        target_lon = (
            float(target_market.longitude) if target_market.longitude is not None else origin_lon
        )

        distance_km = haversine_distance_km(origin_lat, origin_lon, target_lat, target_lon)
        if distance_km > max_distance_km:
            continue

        target_modal = float(mp.modal_price)
        gross_spread = round(target_modal - origin_price, 2)

        # Transparent line-item cost deductions
        freight_cost = round(base_transport_cost + (distance_km * rate_per_km_quintal), 2)
        handling_cost = round(handling_cost_per_qtl, 2)
        commission_cost = round(target_modal * (commission_pct / 100.0), 2)
        spoilage_cost = round(origin_price * (spoilage_risk_pct / 100.0), 2)
        total_costs = round(freight_cost + handling_cost + commission_cost + spoilage_cost, 2)

        net_spread = round(gross_spread - total_costs, 2)
        date_diff = max(0, (origin_price_rec.price_date - mp.price_date).days)

        # Variety alignment check
        target_variety_id = mp.variety_id
        target_variety = (
            db.query(Variety).filter(Variety.id == target_variety_id).first()
            if target_variety_id
            else None
        )
        target_variety_name = target_variety.name if target_variety else None

        if origin_variety_id and target_variety_id:
            if origin_variety_id == target_variety_id:
                variety_match = "exact"
            else:
                variety_match = "cross_variety_approximate"
        elif not origin_variety_id and not target_variety_id:
            variety_match = "exact_modal_benchmark"
        else:
            variety_match = "cross_variety_approximate"

        # Multi-factor uncertainty scoring
        _unc_points, unc_rating, unc_reasons = compute_uncertainty_score(
            distance_km=distance_km,
            date_diff_days=date_diff,
            variety_match=variety_match,
            spoilage_cost=spoilage_cost,
            spoilage_risk_pct=spoilage_risk_pct,
            arrival_quantity=float(mp.arrival_quantity) if mp.arrival_quantity else None,
        )

        # Defensible recommendation classification
        if net_spread >= 100.0 and unc_rating != "high":
            recommendation = "strong_arbitrage"
        elif net_spread > 0.0:
            recommendation = "profitable_dispatch"
        else:
            recommendation = "local_preferred"

        opportunities.append(
            {
                "target_market_id": str(target_market.id),
                "target_market_name": target_market.name,
                "district": target_market.district,
                "target_price": target_modal,
                "price_date": mp.price_date.isoformat(),
                "distance_km": distance_km,
                "gross_spread": gross_spread,
                "transport_cost": freight_cost,
                "net_spread": net_spread,
                "recommendation": recommendation,
                "variety_name": target_variety_name,
                "variety_match": variety_match,
                "date_difference_days": date_diff,
                "uncertainty_rating": unc_rating,
                "uncertainty_reasons": unc_reasons,
                "costs_breakdown": {
                    "freight": freight_cost,
                    "handling": handling_cost,
                    "commission": commission_cost,
                    "spoilage_risk": spoilage_cost,
                    "total_cost": total_costs,
                },
            }
        )

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
        "origin_variety_name": origin_variety_name,
        "vehicle_profile": vehicle_profile,
        "total_destinations_analyzed": len(opportunities),
        "assumptions": {
            "vehicle_profile": vehicle_profile,
            "base_transport_cost": base_transport_cost,
            "rate_per_km_quintal": rate_per_km_quintal,
            "handling_cost_per_qtl": handling_cost_per_qtl,
            "commission_pct": commission_pct,
            "spoilage_risk_pct": spoilage_risk_pct,
            "min_shipment_qtl": min_shipment_qtl,
        },
        "disclaimer": DISCLAIMER_EN,
        "disclaimer_ta": DISCLAIMER_TA,
        "disclaimer_en": DISCLAIMER_EN,
        "opportunities": opportunities,
    }
