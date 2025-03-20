from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, Float, DateTime, func

class Base(DeclarativeBase):
    pass

class TemperatureEvent(Base):
    __tablename__ = "temperature_events"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id = mapped_column(String(255), nullable=False, index=True)
    sensor_id = mapped_column(String(255), nullable=False, index=True)
    timestamp = mapped_column(DateTime, nullable=False)
    temperature = mapped_column(Float, nullable=False)
    city_zone = mapped_column(String(255), nullable=True)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    trace_id = mapped_column(String(255), nullable=False, index=True)

class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id = mapped_column(String(255), nullable=False, index=True)
    sensor_id = mapped_column(String(255), nullable=False, index=True)
    timestamp = mapped_column(DateTime, nullable=False)
    traffic_density = mapped_column(Integer, nullable=False)
    incident_report = mapped_column(String(255), nullable=True)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    trace_id = mapped_column(String(255), nullable=False, index=True)
