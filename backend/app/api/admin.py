"""Admin endpoints — manual ingestion trigger, system status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.user import User
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/ingest")
def trigger_ingestion(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Manually trigger price data ingestion (admin only)."""
    service = IngestionService(db)
    result = service.run_ingestion()
    return {"message": "Ingestion completed", "result": result}


@router.post("/weather/ingest")
def trigger_weather_ingest(
    district: str = "all",
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin", "data_operator"])),
):
    """Trigger live weather forecast ingestion from Open-Meteo for a district or statewide."""
    from app.models.geography import District
    from app.services.weather_service import WeatherService

    service = WeatherService(db)
    if district.lower() in ("all", "statewide"):
        district_rows = db.query(District.name).order_by(District.name).all()
        target_districts = [d[0] for d in district_rows] if district_rows else ["Erode"]
        total_count = 0
        for d in target_districts:
            try:
                total_count += service.ingest_forecast(district=d, days=days)
            except Exception:
                pass
        return {
            "message": f"Successfully ingested {total_count} forecast days across {len(target_districts)} districts",
            "district": "statewide",
            "days_ingested": total_count,
        }

    count = service.ingest_forecast(district=district, days=days)
    return {
        "message": f"Successfully ingested {count} forecast days for {district}",
        "district": district,
        "days_ingested": count,
    }


@router.post("/purge-testing-data")
def purge_testing_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Purge synthetic/demo test data so only real ground-truth data remains."""
    from app.models.market_price import MarketPrice
    from app.models.weather import WeatherData

    deleted_prices = (
        db.query(MarketPrice)
        .filter(
            (MarketPrice.source.in_(("seed_demo", "demo_seed")))
            | (MarketPrice.source.like("%synthetic%"))
            | (MarketPrice.source.like("%sample%"))
            | (MarketPrice.source.like("%test%"))
        )
        .delete(synchronize_session=False)
    )

    deleted_weather = (
        db.query(WeatherData)
        .filter(WeatherData.source.in_(("seed", "synthetic", "sample")))
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "status": "success",
        "purged_prices": deleted_prices,
        "purged_weather": deleted_weather,
        "message": f"Successfully purged {deleted_prices} test price records and {deleted_weather} test weather records.",
    }


@router.post("/retention/purge")
def trigger_retention_purge(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Manually trigger DPDP retention purge."""
    from app.services.retention import (
        purge_conversation_state,
        purge_inbound,
        purge_outbound,
    )

    inbound_count = purge_inbound(retention_days=7)
    state_count = purge_conversation_state(ttl_hours=24)
    outbound_count = purge_outbound(retention_months=12)

    return {
        "message": "DPDP retention purge completed",
        "purged": {
            "inbound": inbound_count,
            "conversation_state": state_count,
            "outbound": outbound_count,
        },
    }
