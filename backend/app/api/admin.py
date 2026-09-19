"""Admin endpoints — manual ingestion trigger, system status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import require_role
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
