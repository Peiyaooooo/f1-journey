import json
from pydantic import BaseModel, field_validator


class SeatSectionRead(BaseModel):
    id: int
    circuit_id: int
    name: str
    section_type: str
    location_on_track: str | None = None
    has_roof: bool
    has_screen: bool
    pit_view: bool
    podium_view: bool
    capacity: int | None = None
    view_description: str | None = None
    latitude: float
    longitude: float
    view_photos: list[str] | None = None

    model_config = {"from_attributes": True}

    @field_validator("view_photos", mode="before")
    @classmethod
    def parse_view_photos(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


class SeatSectionList(BaseModel):
    id: int
    circuit_id: int
    name: str
    section_type: str
    location_on_track: str | None = None
    has_roof: bool
    has_screen: bool
    pit_view: bool
    podium_view: bool
    latitude: float
    longitude: float

    model_config = {"from_attributes": True}
