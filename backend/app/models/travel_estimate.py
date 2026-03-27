from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TravelEstimate(Base):
    __tablename__ = "travel_estimates"
    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    origin_city: Mapped[str] = mapped_column(String(100))
    origin_country: Mapped[str] = mapped_column(String(100))
    origin_airport_code: Mapped[str] = mapped_column(String(10))
    flight_price_min: Mapped[float] = mapped_column(Float)
    flight_price_max: Mapped[float] = mapped_column(Float)
    flight_duration_hours: Mapped[float] = mapped_column(Float)
    flight_stops: Mapped[int] = mapped_column(Integer)
    train_available: Mapped[bool] = mapped_column(Boolean, default=False)
    train_price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    train_price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    train_duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_transport_cost: Mapped[float] = mapped_column(Float)
    hotel_avg_per_night: Mapped[float] = mapped_column(Float)
    last_fetched_at: Mapped[datetime] = mapped_column(DateTime)
    circuit: Mapped["Circuit"] = relationship()
