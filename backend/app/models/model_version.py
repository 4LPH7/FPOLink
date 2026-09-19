"""Model version tracking — no MLflow needed."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # lightgbm, statsforecast, etc.
    metrics = Column(JSONB, nullable=True)  # {mase, mae, rmse}
    file_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
