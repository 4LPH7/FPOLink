"""CLI Evaluation Tool for Inter-District Arbitrage and Transport Realization.

Evaluates arbitrage opportunities across Tamil Nadu agricultural markets,
applying configurable vehicle profiles, itemized deductions (handling, mandi fee, spoilage),
variety matching, and multi-factor uncertainty scoring.

Usage:
    python backend/scripts/evaluate_arbitrage.py --crop Turmeric --market "Erode" --vehicle lcv
    python backend/scripts/evaluate_arbitrage.py --crop Banana --market "Gobichettipalayam" --vehicle pickup
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import func  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models.crop import Crop  # noqa: E402
from app.models.market import Market  # noqa: E402
from app.services.arbitrage import VEHICLE_PROFILES, find_market_arbitrage  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate_arbitrage")


def run_arbitrage_evaluation(
    crop_name: str,
    market_name: str,
    vehicle_profile: str = "lcv",
    radius_km: float = 300.0,
    handling_cost: Optional[float] = None,
    commission_pct: Optional[float] = None,
    spoilage_risk_pct: Optional[float] = None,
) -> int:
    """Run inter-district arbitrage analysis from command line and print formatted report."""
    db = SessionLocal()
    try:
        # Resolve crop
        crop = (
            db.query(Crop)
            .filter(
                (func.lower(Crop.name) == crop_name.lower().strip())
                | (Crop.name.ilike(f"%{crop_name.strip()}%"))
                | (Crop.tamil_name == crop_name.strip())
            )
            .first()
        )
        if not crop:
            print(f"Error: Crop '{crop_name}' not found in database.")
            return 1

        # Resolve origin market
        market = (
            db.query(Market)
            .filter(
                (func.lower(Market.name) == market_name.lower().strip())
                | (Market.name.ilike(f"%{market_name.strip()}%"))
            )
            .first()
        )
        if not market:
            print(f"Error: Market '{market_name}' not found in database.")
            return 1

        print("=" * 105)
        print("FPOLINK TN — INTER-DISTRICT MARKET ARBITRAGE & DISPATCH EVALUATION")
        print("=" * 105)
        print(
            f"Commodity        : {crop.name} ({crop.tamil_name or 'N/A'}) [Category: {crop.category}]"
        )
        print(f"Origin Mandi     : {market.name} ({market.district}, TN)")
        print(
            f"Vehicle Profile  : {vehicle_profile.upper()} ({VEHICLE_PROFILES.get(vehicle_profile, {}).get('name', 'Custom')})"
        )
        print(f"Search Radius    : {radius_km} km")
        print("-" * 105)

        result = find_market_arbitrage(
            db=db,
            crop_id=crop.id,
            origin_market_id=market.id,
            max_distance_km=radius_km,
            vehicle_profile=vehicle_profile,
            handling_cost_per_qtl=handling_cost,
            commission_pct=commission_pct,
            spoilage_risk_pct=spoilage_risk_pct,
        )

        if "error" in result:
            print(f"Analysis failed: {result['error']}")
            return 1

        origin_price = result.get("origin_price")
        if origin_price is None:
            print(f"No recent verified price observations found for {crop.name} at {market.name}.")
            return 0

        print(
            f"Origin Benchmark : ₹{origin_price:,.2f}/quintal (Observed: {result.get('origin_price_date')})"
        )
        print(
            f"Cost Deductions  : Base Freight ₹{result['assumptions']['base_transport_cost']}/qtl | "
            f"Rate ₹{result['assumptions']['rate_per_km_quintal']}/km/qtl | "
            f"Handling ₹{result['assumptions']['handling_cost_per_qtl']}/qtl | "
            f"Commission {result['assumptions']['commission_pct']}% | "
            f"Spoilage Buffer {result['assumptions']['spoilage_risk_pct']}%"
        )
        print("=" * 105)

        opps = result.get("opportunities", [])
        if not opps:
            print(f"No destinations found within {radius_km} km reporting prices for {crop.name}.")
            return 0

        headers = f"{'Destination Mandi':<28} | {'Dist':<7} | {'Rate (₹)':<10} | {'Gross':<9} | {'Costs':<10} | {'Net (₹)':<10} | {'Uncertainty':<11} | {'Decision'}"
        print(headers)
        print("-" * 105)

        for opp in opps:
            m_label = f"{opp['target_market_name']} ({opp['district'][:3]})"
            dist_str = f"{opp['distance_km']} km"
            rate_str = f"₹{opp['target_price']:,.0f}"
            gross_str = (
                f"+₹{opp['gross_spread']:,.0f}"
                if opp["gross_spread"] > 0
                else f"₹{opp['gross_spread']:,.0f}"
            )
            cost_str = f"-₹{opp['costs_breakdown']['total_cost']:,.0f}"
            net_str = (
                f"+₹{opp['net_spread']:,.0f}"
                if opp["net_spread"] > 0
                else f"₹{opp['net_spread']:,.0f}"
            )
            unc_str = opp.get("uncertainty_rating", "low").upper()
            dec_str = opp["recommendation"].replace("_", " ").upper()

            print(
                f"{m_label:<28} | {dist_str:<7} | {rate_str:<10} | {gross_str:<9} | {cost_str:<10} | {net_str:<10} | {unc_str:<11} | {dec_str}"
            )
            if opp.get("uncertainty_reasons"):
                reasons_preview = "; ".join(opp["uncertainty_reasons"][:2])
                print(f"  ↳ Risk Factors: {reasons_preview}")

        print("=" * 105)
        print("DEFENSIBILITY ADVISORY:")
        print(f"Tamil   : {result['disclaimer_ta']}")
        print(f"English : {result['disclaimer_en']}")
        print("=" * 105)
        return 0
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Evaluate Inter-District Market Arbitrage")
    parser.add_argument("--crop", default="Turmeric", help="Crop name (default: Turmeric)")
    parser.add_argument("--market", default="Erode", help="Origin market name (default: Erode)")
    parser.add_argument(
        "--vehicle",
        default="lcv",
        choices=["pickup", "lcv", "medium_truck"],
        help="Vehicle profile",
    )
    parser.add_argument("--radius", type=float, default=300.0, help="Search radius in km")
    parser.add_argument(
        "--handling", type=float, default=None, help="Override handling cost per quintal"
    )
    parser.add_argument("--commission", type=float, default=None, help="Override commission %")
    parser.add_argument("--spoilage", type=float, default=None, help="Override spoilage risk %")

    args = parser.parse_args()
    sys.exit(
        run_arbitrage_evaluation(
            crop_name=args.crop,
            market_name=args.market,
            vehicle_profile=args.vehicle,
            radius_km=args.radius,
            handling_cost=args.handling,
            commission_pct=args.commission,
            spoilage_risk_pct=args.spoilage,
        )
    )


if __name__ == "__main__":
    main()
