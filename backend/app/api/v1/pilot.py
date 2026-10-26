"""Pilot metrics: how much each FPO's farmers actually use the bot, and what it led to."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.database import get_db
from app.models.bot_activity import BotActivity
from app.models.farmer import Farmer
from app.models.fpo import FPO
from app.models.harvest import Harvest
from app.models.user import User

router = APIRouter(prefix="/pilot", tags=["pilot-v1"])


@router.get("/metrics")
def pilot_metrics(
    days: int = Query(default=7, ge=1, le=90, description="Look-back window in days"),
    fpo_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "state_admin"])),
):
    """Per-FPO use over the last `days`: active farmers, queries, advice shown, harvest pooled."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    fpos = db.query(FPO)
    if fpo_id:
        fpos = fpos.filter(FPO.id == fpo_id)
    fpos = fpos.order_by(FPO.name).all()

    def per_fpo(*cols, source, window):
        q = db.query(Farmer.fpo_id, *cols).select_from(Farmer).join(source[0], source[1])
        return {r[0]: r[1:] for r in q.filter(window).group_by(Farmer.fpo_id).all()}

    registered = {
        r[0]: r[1] for r in db.query(Farmer.fpo_id, func.count(Farmer.id)).group_by(Farmer.fpo_id)
    }
    use = per_fpo(
        func.count(func.distinct(BotActivity.farmer_id)),
        func.count(BotActivity.id).filter(BotActivity.intent == "price"),
        func.count(BotActivity.id).filter(BotActivity.advice_shown.is_(True)),
        source=(BotActivity, BotActivity.farmer_id == Farmer.id),
        window=BotActivity.created_at >= since,
    )
    harvest = per_fpo(
        func.count(Harvest.id),
        func.coalesce(func.sum(Harvest.quantity_kg), 0),
        source=(Harvest, Harvest.farmer_id == Farmer.id),
        window=Harvest.harvest_date >= since.date(),
    )

    rows = []
    for f in fpos:
        active, queries, advice = use.get(f.id, (0, 0, 0))
        n_harvests, kg = harvest.get(f.id, (0, 0))
        rows.append(
            {
                "fpo_id": str(f.id),
                "fpo_name": f.name,
                "farmers_registered": registered.get(f.id, 0),
                "active_farmers": active,
                "price_queries": queries,
                "advice_shown": advice,
                "harvests_reported": n_harvests,
                "harvest_kg": float(kg),
            }
        )
    return {"window_days": days, "fpos": rows}
