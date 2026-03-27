from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeatSection(Base):
    __tablename__ = "seat_sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    name: Mapped[str] = mapped_column(String(200))
    section_type: Mapped[str] = mapped_column(String(30))
    location_on_track: Mapped[str | None] = mapped_column(String(200), nullable=True)
    has_roof: Mapped[bool] = mapped_column(Boolean, default=False)
    has_screen: Mapped[bool] = mapped_column(Boolean, default=False)
    pit_view: Mapped[bool] = mapped_column(Boolean, default=False)
    podium_view: Mapped[bool] = mapped_column(Boolean, default=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    view_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    view_photos: Mapped[str | None] = mapped_column(Text, nullable=True)

    circuit: Mapped["Circuit"] = relationship(back_populates="seat_sections")
