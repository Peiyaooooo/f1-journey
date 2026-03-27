from datetime import datetime
from pydantic import BaseModel


class TravelEstimateRead(BaseModel):
    id: int
    circuit_id: int
    origin_city: str
    origin_country: str
    origin_airport_code: str
    flight_price_min: float
    flight_price_max: float
    flight_duration_hours: float
    flight_stops: int
    train_available: bool
    train_price_min: float | None = None
    train_price_max: float | None = None
    train_duration_hours: float | None = None
    local_transport_cost: float
    hotel_avg_per_night: float
    last_fetched_at: datetime

    model_config = {"from_attributes": True}


class ExchangeRateRead(BaseModel):
    currency_code: str
    rate_from_usd: float
    last_updated_at: datetime

    model_config = {"from_attributes": True}
