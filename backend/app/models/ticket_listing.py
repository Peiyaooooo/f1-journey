from datetime import datetime

from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketListing(Base):
    __tablename__ = "ticket_listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    race_event_id: Mapped[int] = mapped_column(ForeignKey("race_events.id"))
    seat_section_id: Mapped[int | None] = mapped_column(ForeignKey("seat_sections.id"), nullable=True)
    source_site: Mapped[str] = mapped_column(String(50))
    source_url: Mapped[str] = mapped_column(String(500))
    source_section_name: Mapped[str] = mapped_column(String(200))
    ticket_type: Mapped[str] = mapped_column(String(30))
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    available_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    includes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    circuit: Mapped["Circuit"] = relationship()
    race_event: Mapped["RaceEvent"] = relationship()
    seat_section: Mapped["SeatSection | None"] = relationship()
