"""Geography models — State, District, Taluk, Block, Village hierarchy."""

import uuid

from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class State(Base, TimestampMixin):
    __tablename__ = "states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)

    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<State {self.name} ({self.code})>"


class District(Base, TimestampMixin):
    __tablename__ = "districts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_id = Column(
        UUID(as_uuid=True), ForeignKey("states.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    state = relationship("State", back_populates="districts")
    taluks = relationship("Taluk", back_populates="district", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<District {self.name} ({self.code})>"


class Taluk(Base, TimestampMixin):
    __tablename__ = "taluks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district_id = Column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)

    district = relationship("District", back_populates="taluks")
    blocks = relationship("Block", back_populates="taluk", cascade="all, delete-orphan")
    villages = relationship("Village", back_populates="taluk", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Taluk {self.name}>"


class Block(Base, TimestampMixin):
    __tablename__ = "blocks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taluk_id = Column(
        UUID(as_uuid=True), ForeignKey("taluks.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(100), nullable=False)

    taluk = relationship("Taluk", back_populates="blocks")

    def __repr__(self):
        return f"<Block {self.name}>"


class Village(Base, TimestampMixin):
    __tablename__ = "villages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    taluk_id = Column(
        UUID(as_uuid=True), ForeignKey("taluks.id", ondelete="CASCADE"), nullable=False
    )
    block_id = Column(
        UUID(as_uuid=True), ForeignKey("blocks.id", ondelete="SET NULL"), nullable=True
    )
    name = Column(String(100), nullable=False)

    taluk = relationship("Taluk", back_populates="villages")
    block = relationship("Block")

    def __repr__(self):
        return f"<Village {self.name}>"
