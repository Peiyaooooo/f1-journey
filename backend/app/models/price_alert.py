from datetime import datetime

from sqlalchemy import Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"))
    seat_section_id: Mapped[int | None] = mapped_column(ForeignKey("seat_sections.id"), nullable=True)
    target_price: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()
    circuit: Mapped["Circuit"] = relationship()
    seat_section: Mapped["SeatSection | None"] = relationship()
