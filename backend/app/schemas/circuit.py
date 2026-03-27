from pydantic import BaseModel


class CircuitBase(BaseModel):
    name: str
    country: str
    continent: str
    city: str
    latitude: float
    longitude: float
    track_type: str
    track_length_km: float
    number_of_turns: int
    drs_zones_count: int
    overtake_difficulty: int
    avg_overtakes_per_race: float
    rain_probability_pct: int
    nearest_airport: str
    local_transport_notes: str | None = None
    atmosphere_rating: float | None = None
    fan_reviews_summary: str | None = None
    elevation_change: float | None = None


class CircuitRead(CircuitBase):
    id: int

    model_config = {"from_attributes": True}


class CircuitList(BaseModel):
    id: int
    name: str
    country: str
    continent: str
    track_type: str
    overtake_difficulty: int
    avg_overtakes_per_race: float
    rain_probability_pct: int

    model_config = {"from_attributes": True}
