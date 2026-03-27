from datetime import datetime
from pydantic import BaseModel


class PriceAlertCreate(BaseModel):
    circuit_id: int
    seat_section_id: int | None = None
    target_price: float


class PriceAlertRead(BaseModel):
    id: int
    user_id: int
    circuit_id: int
    seat_section_id: int | None
    target_price: float
    is_active: bool
    triggered_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
