import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class FPO(Base, TimestampMixin):
    __tablename__ = "fpos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False)
    district = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    state = Column(String(100), default="Tamil Nadu")
    contact_phone = Column(String(15), nullable=False)
    contact_email = Column(String, nullable=True)
    address = Column(Text, nullable=True)

    farmers = relationship("Farmer", back_populates="fpo")
