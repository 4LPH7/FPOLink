"""Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker status (T4.4)."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_role
from app.models.user import User
from app.schemas.whatsapp_usage import WhatsAppUsageSummary
from app.services.whatsapp_usage import WhatsAppUsageService

router = APIRouter(prefix="/api/admin/whatsapp", tags=["admin-whatsapp"])


def get_usage_service() -> WhatsAppUsageService:
    return WhatsAppUsageService()


@router.get("/usage", response_model=WhatsAppUsageSummary)
def get_whatsapp_usage(
    month: str = Query(
        default=None,
        description="Month in YYYY-MM format (e.g. 2026-09). Defaults to current month.",
    ),
    current_user: User = Depends(require_role(["admin"])),
    service: WhatsAppUsageService = Depends(get_usage_service),
) -> WhatsAppUsageSummary:
    """Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and circuit breaker state."""
    return service.get_usage_summary(month_str=month)
