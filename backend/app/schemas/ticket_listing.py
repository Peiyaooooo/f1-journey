import json
from datetime import datetime
from pydantic import BaseModel, field_validator


class TicketListingRead(BaseModel):
    id: int
    circuit_id: int
    race_event_id: int
    seat_section_id: int | None = None
    source_site: str
    source_url: str
    source_section_name: str
    ticket_type: str
    price: float
    currency: str
    available_quantity: int | None = None
    includes: list[str] | None = None
    last_scraped_at: datetime
    is_available: bool

    model_config = {"from_attributes": True}

    @field_validator("includes", mode="before")
    @classmethod
    def parse_includes(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
            # Plain text string — wrap in a list
            return [v]
        return v
