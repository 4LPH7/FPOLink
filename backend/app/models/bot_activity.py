"""One row per farmer request to the bot, for pilot usage reporting."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class BotActivity(Base):
    __tablename__ = "bot_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(
        UUID(as_uuid=True), ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False
    )
    intent = Column(String(30), nullable=False)  # price, forecast, weather, buyers, harvest
    advice_shown = Column(Boolean, nullable=False, default=False)  # a better market was named
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
