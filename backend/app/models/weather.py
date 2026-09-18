import uuid
from sqlalchemy import Column, String, Float, Date, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    district = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    temperature_max = Column(Float, nullable=False)
    temperature_min = Column(Float, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    source = Column(String(50), default='open_meteo')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('district', 'date', name='uix_weather_district_date'),
    )
