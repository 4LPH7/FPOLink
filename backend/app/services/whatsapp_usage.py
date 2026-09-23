"""WhatsApp usage reporting, cost estimation, and circuit breaker service (T4.4)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.whatsapp import OutboundMessage, WhatsAppRecipientStatus
from app.schemas.whatsapp_usage import WhatsAppUsageSummary

log = logging.getLogger("whatsapp.usage")


class WhatsAppUsageService:
    """Calculates monthly message volumes, applies configurable cost rates, and gates circuit breakers."""

    def __init__(self, db_factory=SessionLocal) -> None:
        self.db_factory = db_factory

    def get_current_month_str(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def parse_month(self, month_str: str | None) -> tuple[int, int, str]:
        """Parse YYYY-MM into year, month integers. Fallback to current UTC month."""
        if month_str:
            try:
                parts = month_str.strip().split("-")
                year = int(parts[0])
                month = int(parts[1])
                if 1 <= month <= 12:
                    return year, month, f"{year:04d}-{month:02d}"
            except Exception:
                pass
        now = datetime.now(timezone.utc)
        return now.year, now.month, now.strftime("%Y-%m")

    def is_circuit_breaker_tripped(self) -> bool:
        """Evaluate whether monthly message caps or budget thresholds have been exceeded."""
        year, month, _ = self.parse_month(None)
        with self.db_factory() as db:
            count = (
                db.query(func.count(OutboundMessage.id))
                .filter(
                    extract("year", OutboundMessage.created_at) == year,
                    extract("month", OutboundMessage.created_at) == month,
                )
                .scalar()
                or 0
            )

            if count >= settings.WHATSAPP_MONTHLY_SEND_CAP:
                log.warning(
                    "WhatsApp circuit breaker tripped: monthly send cap reached (%d >= %d)",
                    count,
                    settings.WHATSAPP_MONTHLY_SEND_CAP,
                )
                return True

            # Also check budget threshold
            summary = self._calculate_usage_for_month(db, year, month)
            if summary["estimated_cost_inr"] >= settings.WHATSAPP_MONTHLY_BUDGET_INR:
                log.warning(
                    "WhatsApp circuit breaker tripped: budget limit reached (₹%.2f >= ₹%.2f)",
                    summary["estimated_cost_inr"],
                    settings.WHATSAPP_MONTHLY_BUDGET_INR,
                )
                return True

            return False

    def get_usage_summary(self, month_str: str | None = None) -> WhatsAppUsageSummary:
        """Generate usage and cost report for the requested month."""
        year, month, formatted_month = self.parse_month(month_str)
        with self.db_factory() as db:
            data = self._calculate_usage_for_month(db, year, month)
            unreachable_count = (
                db.query(func.count(WhatsAppRecipientStatus.wa_id))
                .filter(WhatsAppRecipientStatus.is_unreachable == True)  # noqa: E712
                .scalar()
                or 0
            )

            is_tripped = (
                data["total_messages"] >= settings.WHATSAPP_MONTHLY_SEND_CAP
                or data["estimated_cost_inr"] >= settings.WHATSAPP_MONTHLY_BUDGET_INR
            )

            return WhatsAppUsageSummary(
                month=formatted_month,
                total_messages=data["total_messages"],
                by_category=data["by_category"],
                by_status=data["by_status"],
                delivery_rate_pct=data["delivery_rate_pct"],
                estimated_cost_inr=data["estimated_cost_inr"],
                unreachable_recipients=unreachable_count,
                monthly_cap=settings.WHATSAPP_MONTHLY_SEND_CAP,
                monthly_budget_inr=settings.WHATSAPP_MONTHLY_BUDGET_INR,
                circuit_breaker_tripped=is_tripped,
            )

    def _calculate_usage_for_month(self, db: Session, year: int, month: int) -> dict:
        base_query = db.query(OutboundMessage).filter(
            extract("year", OutboundMessage.created_at) == year,
            extract("month", OutboundMessage.created_at) == month,
        )

        total_messages = base_query.count()

        # Group by category
        cat_counts = (
            db.query(OutboundMessage.category, func.count(OutboundMessage.id))
            .filter(
                extract("year", OutboundMessage.created_at) == year,
                extract("month", OutboundMessage.created_at) == month,
            )
            .group_by(OutboundMessage.category)
            .all()
        )
        by_category = {cat: count for cat, count in cat_counts}

        # Group by status
        status_counts = (
            db.query(OutboundMessage.status, func.count(OutboundMessage.id))
            .filter(
                extract("year", OutboundMessage.created_at) == year,
                extract("month", OutboundMessage.created_at) == month,
            )
            .group_by(OutboundMessage.status)
            .all()
        )
        by_status = {st: count for st, count in status_counts}

        # Calculate estimated cost in INR based on configured rates
        cost = 0.0
        cost += by_category.get("service", 0) * settings.WHATSAPP_RATE_SERVICE_INR
        cost += by_category.get("utility", 0) * settings.WHATSAPP_RATE_UTILITY_INR
        cost += by_category.get("marketing", 0) * settings.WHATSAPP_RATE_MARKETING_INR
        cost += (
            by_category.get("authentication", 0) + by_category.get("auth", 0)
        ) * settings.WHATSAPP_RATE_AUTH_INR

        # Delivery rate calculation: (delivered + read) / (delivered + read + failed)
        successful = by_status.get("delivered", 0) + by_status.get("read", 0)
        failed = by_status.get("failed", 0)
        resolved = successful + failed
        if resolved > 0:
            delivery_rate = round((successful / resolved) * 100.0, 2)
        elif total_messages > 0:
            delivery_rate = 100.0  # all currently in 'sent' state
        else:
            delivery_rate = 100.0

        return {
            "total_messages": total_messages,
            "by_category": by_category,
            "by_status": by_status,
            "delivery_rate_pct": delivery_rate,
            "estimated_cost_inr": round(cost, 2),
        }
