from datetime import date

from sqlalchemy import String, Integer, Float, ForeignKey, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RaceEvent(Base):
    __tablename__ = "race_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    season_year: Mapped[int] = mapped_column(Integer)
    race_name: Mapped[str] = mapped_column(String(200))
    race_date: Mapped[date] = mapped_column(Date)
    sprint_weekend: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20))  # "upcoming" or "completed"
    total_overtakes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weather_actual: Mapped[str | None] = mapped_column(String(100), nullable=True)

    circuit: Mapped["Circuit"] = relationship(back_populates="race_events")
