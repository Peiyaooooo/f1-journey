from datetime import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency_code: Mapped[str] = mapped_column(String(10), unique=True)
    rate_from_usd: Mapped[float] = mapped_column(Float)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime)
