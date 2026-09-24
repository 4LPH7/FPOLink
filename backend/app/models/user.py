import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STATE_ADMIN = "state_admin"
    DISTRICT_ADMIN = "district_admin"
    FPO_ADMIN = "fpo_admin"
    FPO_STAFF = "fpo_staff"
    DATA_OPERATOR = "data_operator"
    ANALYST = "analyst"
    BUYER = "buyer"
    FIELD_AGENT = "field_agent"
    FARMER = "farmer"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    language_preference = Column(String(2), default="en")
    telegram_chat_id = Column(String, nullable=True)
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime(timezone=True), nullable=True)

    # Multi-tenant scoping
    fpo_id = Column(UUID(as_uuid=True), ForeignKey("fpos.id"), nullable=True)
    district_id = Column(UUID(as_uuid=True), ForeignKey("districts.id"), nullable=True)

    fpo = relationship("FPO")
    district = relationship("District")

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"
