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
    result = service.run_ingestion(source="manual_trigger")
    return {"message": "Ingestion completed", "result": result}


@router.post("/weather/ingest")
def trigger_weather_ingest(
    district: str = "Erode",
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
):
    """Trigger live weather forecast ingestion from Open-Meteo."""
    from app.services.weather_service import WeatherService

    service = WeatherService(db)
    count = service.ingest_forecast(district=district, days=days)
    return {
        "message": f"Successfully ingested {count} forecast days for {district}",
        "district": district,
        "days_ingested": count,
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
