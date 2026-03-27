from datetime import date

from pydantic import BaseModel


class RaceEventBase(BaseModel):
    circuit_id: int
    season_year: int
    race_name: str
    race_date: date
    sprint_weekend: bool = False
    status: str
    total_overtakes: int | None = None
    weather_actual: str | None = None


class RaceEventRead(RaceEventBase):
    id: int

    model_config = {"from_attributes": True}


class RaceEventWithCircuit(RaceEventRead):
    circuit_name: str
    circuit_country: str
    continent: str
