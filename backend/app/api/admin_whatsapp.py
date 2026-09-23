"""Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker status (T4.4)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.user import User
from app.models.whatsapp import WhatsAppInbound
from app.schemas.whatsapp_usage import (
    InboundMessageItem,
    InboundMessageListResponse,
    WhatsAppUsageSummary,
)
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


@router.get("/inbound", response_model=InboundMessageListResponse)
def get_admin_inbound(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_role(["admin", "fpo_staff"])),
    db: Session = Depends(get_db),
) -> InboundMessageListResponse:
    """Get recent inbound WhatsApp messages for audit."""
    rows = db.query(WhatsAppInbound).order_by(WhatsAppInbound.received_at.desc()).limit(limit).all()
    total = db.query(WhatsAppInbound).count()
    return InboundMessageListResponse(
        messages=[
            InboundMessageItem(
                message_id=r.message_id,
                status=r.status,
                retry_count=r.retry_count,
                received_at=r.received_at.isoformat() if r.received_at else "",
            )
            for r in rows
        ],
        total=total,
    )
