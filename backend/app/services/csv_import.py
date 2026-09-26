"""CSV Import Harness for Bulk Ingestion of Farm Plots and Commercial Buyers."""

import csv
import io
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.buyer import Buyer, BuyerRequirement
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.harvest import HarvestGrade
from app.models.user import User
from app.services.crop_resolver import resolve_crop
from app.services.yield_estimator import estimate_crop_yield


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse string to date with multiple format support."""
    if not date_str or not date_str.strip():
        return None
    cleaned = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None


def import_farms_csv(db: Session, fpo_id: UUID, csv_text: str) -> Dict:
    """Import multiple farm plots from CSV text into the database."""
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    if not reader.fieldnames:
        return {"error": "Empty or invalid CSV file", "imported": 0, "errors": []}

    imported = 0
    errors: List[Dict] = []

    # Pre-cache farmers by normalized phone
    farmers = db.query(Farmer).join(User, Farmer.user_id == User.id).filter(Farmer.fpo_id == fpo_id).all()
    farmer_phone_map = {f.phone: f for f in farmers if f.phone}
    # Also index by User.phone
    for f in farmers:
        if f.user and f.user.phone:
            farmer_phone_map[f.user.phone] = f

    for row_idx, row in enumerate(reader, start=2):
        try:
            phone_raw = row.get("farmer_phone", "").strip()
            # Normalize phone (remove +91, spaces)
            phone = phone_raw.replace("+91", "").replace(" ", "").replace("-", "")[-10:]
            if not phone or phone not in farmer_phone_map:
                errors.append({
                    "row": row_idx,
                    "phone": phone_raw,
                    "error": f"Farmer with phone '{phone_raw}' not found under this FPO",
                })
                continue

            farmer = farmer_phone_map[phone]

            # Resolve crop
            crop_name_raw = row.get("crop_name", "").strip()
            if not crop_name_raw:
                errors.append({"row": row_idx, "error": "Missing crop_name column"})
                continue

            crop = resolve_crop(crop_name_raw, db)
            if not crop:
                errors.append({
                    "row": row_idx,
                    "crop": crop_name_raw,
                    "error": f"Crop '{crop_name_raw}' could not be resolved",
                })
                continue

            # Parse area
            try:
                area_acres = float(row.get("area_acres", 1.0))
                if area_acres <= 0.0:
                    raise ValueError
            except (ValueError, TypeError):
                errors.append({"row": row_idx, "error": "Invalid area_acres (must be > 0.0)"})
                continue

            plot_name = row.get("plot_name", "").strip() or None
            village = row.get("village", "").strip() or farmer.village
            soil_type = row.get("soil_type", "").strip() or None
            irrigation_type = row.get("irrigation_type", "").strip() or None
            sowing_date = parse_date(row.get("sowing_date"))
            expected_harvest_date = parse_date(row.get("expected_harvest_date"))

            # Calculate yield estimate
            yield_est = estimate_crop_yield(
                crop_name=crop.name,
                area_acres=area_acres,
                soil_type=soil_type,
                irrigation_type=irrigation_type,
                sowing_date=sowing_date,
            )
            expected_yield = yield_est["estimated_yield_kg"]
            if not expected_harvest_date and yield_est.get("estimated_harvest_window_start"):
                expected_harvest_date = yield_est["estimated_harvest_window_start"]

            farm = Farm(
                farmer_id=farmer.id,
                crop_id=crop.id,
                plot_name=plot_name,
                area_acres=area_acres,
                village=village,
                soil_type=soil_type,
                irrigation_type=irrigation_type,
                sowing_date=sowing_date,
                expected_harvest_date=expected_harvest_date,
                expected_yield_kg=expected_yield,
                status="active",
                district_id=farmer.district_id,
                taluk_id=farmer.taluk_id,
                village_id=farmer.village_id,
            )
            db.add(farm)
            imported += 1

        except Exception as e:
            errors.append({"row": row_idx, "error": str(e)})

    db.commit()
    return {"imported": imported, "errors_count": len(errors), "errors": errors}


def import_buyers_csv(
    db: Session,
    fpo_id: Optional[UUID],
    csv_text: str,
    created_by_user_id: Optional[UUID] = None,
) -> Dict:
    """Import commercial buyers and optional procurement requirements from CSV text."""
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    if not reader.fieldnames:
        return {"error": "Empty or invalid CSV file", "buyers_imported": 0, "requirements_imported": 0, "errors": []}

    buyers_imported = 0
    requirements_imported = 0
    errors: List[Dict] = []

    for row_idx, row in enumerate(reader, start=2):
        try:
            company_name = row.get("company_name", "").strip()
            contact_phone = row.get("contact_phone", "").strip()
            location = row.get("location", "").strip()

            if not company_name or not contact_phone or not location:
                errors.append({
                    "row": row_idx,
                    "error": "Missing required buyer fields (company_name, contact_phone, location)",
                })
                continue

            # Look up or create buyer
            buyer = (
                db.query(Buyer)
                .filter(Buyer.company_name == company_name, Buyer.contact_phone == contact_phone)
                .first()
            )
            if not buyer:
                buyer = Buyer(
                    company_name=company_name,
                    contact_phone=contact_phone,
                    location=location,
                    buyer_type=row.get("buyer_type", "wholesaler").strip() or "wholesaler",
                    contact_name=row.get("contact_name", "").strip() or None,
                    contact_email=row.get("contact_email", "").strip() or None,
                    district=row.get("district", "").strip() or None,
                    gstin=row.get("gstin", "").strip() or None,
                    fpo_id=fpo_id,
                    created_by_user_id=created_by_user_id,
                )
                db.add(buyer)
                db.flush()
                buyers_imported += 1

            # Check if row also defines a requirement
            crop_name_raw = row.get("crop_name", "").strip()
            qty_raw = row.get("quantity_kg", "").strip()
            if crop_name_raw and qty_raw:
                crop = resolve_crop(crop_name_raw, db)
                if not crop:
                    errors.append({
                        "row": row_idx,
                        "error": f"Crop '{crop_name_raw}' for requirement could not be resolved",
                    })
                    continue

                try:
                    qty = float(qty_raw)
                    if qty <= 0.0:
                        raise ValueError
                except (ValueError, TypeError):
                    errors.append({"row": row_idx, "error": "Invalid quantity_kg (must be > 0.0)"})
                    continue

                req_date = parse_date(row.get("required_date")) or (date.today() + timedelta(days=30))

                # Parse grade
                grade_raw = row.get("min_grade", "B").strip().upper()
                grade = HarvestGrade.B
                if grade_raw in ("A", "B", "C"):
                    grade = HarvestGrade(grade_raw)

                # Parse price
                price_raw = row.get("max_price_per_kg", "").strip()
                max_price = Decimal(price_raw) if price_raw else None

                req = BuyerRequirement(
                    buyer_id=buyer.id,
                    fpo_id=fpo_id,
                    crop_id=crop.id,
                    quantity_kg=qty,
                    min_grade=grade,
                    required_date=req_date,
                    max_price_per_kg=max_price,
                    delivery_location=row.get("delivery_location", "").strip() or buyer.location,
                    created_by_user_id=created_by_user_id,
                )
                db.add(req)
                requirements_imported += 1

        except Exception as e:
            errors.append({"row": row_idx, "error": str(e)})

    db.commit()
    return {
        "buyers_imported": buyers_imported,
        "requirements_imported": requirements_imported,
        "errors_count": len(errors),
        "errors": errors,
    }
