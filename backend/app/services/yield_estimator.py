"""Rule-Based Yield Estimator for Tamil Nadu Agricultural Commodities.

Estimates expected crop yield (kg) per plot based on TNAU and regional agro-climatic
benchmarks, adjusted by acreage, irrigation method, soil type, and sowing timelines.
"""

from datetime import date, timedelta
from typing import Dict, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.farm import Farm

# Base yield in kg per acre based on TNAU / Govt of TN agricultural statistics
BASE_YIELDS_KG_PER_ACRE: Dict[str, float] = {
    "turmeric": 2500.0,      # Cured rhizomes (~10,000 kg fresh)
    "banana": 18000.0,       # Commercial bunches (~18 tonnes/acre)
    "coconut": 9600.0,       # ~8,000 nuts / ~9,600 kg fresh weight
    "paddy": 2400.0,         # ~24 quintals paddy grain
    "groundnut": 900.0,      # Pods in shell
    "tomato": 12000.0,       # Fresh market tomatoes
    "small onion": 4500.0,   # Shallot (chinnavegayam)
    "onion": 6000.0,         # Big onion
    "green chilli": 3500.0,  # Fresh green chillies
    "red chilli": 800.0,     # Dry red chillies
    "maize": 2800.0,         # Grain yield
    "cotton": 900.0,         # Seed cotton (kapas)
    "sugarcane": 40000.0,    # Mill cane (~40 tonnes/acre)
    "black gram": 400.0,     # Pulses (urad dal)
    "green gram": 350.0,     # Moong dal
    "tapioca": 14000.0,      # Fresh tubers (cassava)
    "mango": 4000.0,         # Orchard yield
    "brinjal": 10000.0,      # Eggplant
    "ladies finger": 5000.0, # Okra
    "ginger": 8000.0,        # Fresh rhizomes
}
DEFAULT_BASE_YIELD_KG_PER_ACRE = 2000.0

# Typical gestation / maturity days from sowing to peak harvest
CROP_GESTATION_DAYS: Dict[str, int] = {
    "turmeric": 270,      # 9 months
    "banana": 330,        # 11 months
    "coconut": 30,        # Monthly harvest cycle for perennial palms
    "paddy": 120,         # 4 months
    "groundnut": 105,
    "tomato": 90,
    "small onion": 75,
    "onion": 90,
    "green chilli": 120,
    "red chilli": 150,
    "maize": 100,
    "cotton": 160,
    "sugarcane": 360,
    "black gram": 70,
    "green gram": 65,
    "tapioca": 300,
    "mango": 120,
    "brinjal": 120,
    "ladies finger": 60,
    "ginger": 240,
}
DEFAULT_GESTATION_DAYS = 90

# Irrigation multipliers
IRRIGATION_MULTIPLIERS: Dict[str, float] = {
    "drip": 1.15,        # Precision fertigation +15%
    "sprinkler": 1.10,   # Micro-sprinklers +10%
    "canal": 1.00,       # Surface canal irrigation baseline
    "borewell": 1.00,    # Well/borewell baseline
    "rainfed": 0.70,     # Dryland agriculture -30%
    "dryland": 0.70,
}

# Soil multipliers
SOIL_MULTIPLIERS: Dict[str, float] = {
    "red loam": 1.10,     # Optimal well-drained loam +10%
    "alluvial": 1.10,     # High organic matter river basins +10%
    "clay loam": 1.00,    # Baseline loam
    "black cotton": 0.95, # High moisture retention (penalized for roots, good for cotton)
    "sandy loam": 0.95,   # Lower nutrient retention -5%
    "clay": 0.85,         # Heavy drainage issues -15%
}


def get_irrigation_factor(irrigation_type: Optional[str]) -> float:
    """Return multiplier based on irrigation method."""
    if not irrigation_type:
        return 1.0
    norm = irrigation_type.strip().lower()
    return IRRIGATION_MULTIPLIERS.get(norm, 1.0)


def get_soil_factor(soil_type: Optional[str], crop_name: Optional[str] = None) -> float:
    """Return multiplier based on soil suitability."""
    if not soil_type:
        return 1.0
    norm = soil_type.strip().lower()
    base_factor = SOIL_MULTIPLIERS.get(norm, 1.0)

    # Black cotton soil is optimal for cotton and pulses, but suboptimal for root crops
    if norm == "black cotton" and crop_name:
        c_lower = crop_name.lower()
        if any(k in c_lower for k in ("cotton", "gram", "maize")):
            return 1.10
        elif any(k in c_lower for k in ("turmeric", "ginger", "tapioca", "onion")):
            return 0.90

    return base_factor


def estimate_crop_yield(
    crop_name: str,
    area_acres: float,
    soil_type: Optional[str] = None,
    irrigation_type: Optional[str] = None,
    sowing_date: Optional[date] = None,
) -> Dict:
    """Calculate deterministic rule-based yield estimate and harvest timeline."""
    c_norm = crop_name.strip().lower()

    # Find closest base yield
    base_yield = BASE_YIELDS_KG_PER_ACRE.get(c_norm)
    if base_yield is None:
        # Check substring match (e.g. "erode turmeric" -> "turmeric")
        for key, val in BASE_YIELDS_KG_PER_ACRE.items():
            if key in c_norm:
                base_yield = val
                break
    if base_yield is None:
        base_yield = DEFAULT_BASE_YIELD_KG_PER_ACRE

    soil_factor = get_soil_factor(soil_type, crop_name)
    irrig_factor = get_irrigation_factor(irrigation_type)

    # Total estimated yield (kg) = area * base_yield * soil_factor * irrig_factor
    estimated_yield_kg = round(area_acres * base_yield * soil_factor * irrig_factor, 1)

    # Harvest window calculation
    gestation = CROP_GESTATION_DAYS.get(c_norm)
    if gestation is None:
        for key, val in CROP_GESTATION_DAYS.items():
            if key in c_norm:
                gestation = val
                break
    if gestation is None:
        gestation = DEFAULT_GESTATION_DAYS

    window_start: Optional[date] = None
    window_end: Optional[date] = None
    if sowing_date:
        window_start = sowing_date + timedelta(days=gestation)
        window_end = window_start + timedelta(days=14)

    confidence_note = (
        f"Rule-based agro-climatic estimate for {crop_name.title()} "
        f"({base_yield:.0f} kg/acre baseline, "
        f"soil factor {soil_factor:.2f}, irrigation factor {irrig_factor:.2f})"
    )

    return {
        "crop_name": crop_name,
        "area_acres": area_acres,
        "base_yield_kg_per_acre": base_yield,
        "soil_factor": soil_factor,
        "irrigation_factor": irrig_factor,
        "estimated_yield_kg": estimated_yield_kg,
        "estimated_harvest_window_start": window_start,
        "estimated_harvest_window_end": window_end,
        "confidence_note": confidence_note,
    }


def estimate_farm_yield(db: Session, farm_id: UUID) -> Optional[Dict]:
    """Look up a Farm record, calculate yield estimate, and populate defaults if missing."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm or not farm.crop:
        return None

    crop_name = farm.crop.name
    estimate = estimate_crop_yield(
        crop_name=crop_name,
        area_acres=farm.area_acres,
        soil_type=farm.soil_type,
        irrigation_type=farm.irrigation_type,
        sowing_date=farm.sowing_date,
    )

    # If farm did not have expected yield or date populated, persist the estimate
    needs_update = False
    if farm.expected_yield_kg is None:
        farm.expected_yield_kg = estimate["estimated_yield_kg"]
        needs_update = True
    if farm.expected_harvest_date is None and estimate["estimated_harvest_window_start"]:
        farm.expected_harvest_date = estimate["estimated_harvest_window_start"]
        needs_update = True

    if needs_update:
        db.commit()
        db.refresh(farm)

    estimate["farm_id"] = str(farm.id)
    return estimate
