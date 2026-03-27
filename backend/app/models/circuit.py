from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Circuit(Base):
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(100))
    continent: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(100))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    track_type: Mapped[str] = mapped_column(String(20))  # "street" or "permanent"
    track_length_km: Mapped[float] = mapped_column(Float)
    number_of_turns: Mapped[int] = mapped_column(Integer)
    drs_zones_count: Mapped[int] = mapped_column(Integer)
    overtake_difficulty: Mapped[int] = mapped_column(Integer)  # 1-10
    avg_overtakes_per_race: Mapped[float] = mapped_column(Float)
    rain_probability_pct: Mapped[int] = mapped_column(Integer)
    nearest_airport: Mapped[str] = mapped_column(String(200))
    local_transport_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    atmosphere_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    fan_reviews_summary: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    elevation_change: Mapped[float | None] = mapped_column(Float, nullable=True)

    race_events: Mapped[list["RaceEvent"]] = relationship(back_populates="circuit")
