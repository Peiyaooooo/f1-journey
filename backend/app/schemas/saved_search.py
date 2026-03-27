import json
from datetime import datetime
from pydantic import BaseModel, field_validator


class SavedSearchCreate(BaseModel):
    search_type: str  # "filters" or "trip"
    name: str
    data: dict


class SavedSearchRead(BaseModel):
    id: int
    user_id: int
    search_type: str
    name: str
    data: dict
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("data", mode="before")
    @classmethod
    def parse_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return {}
        return v
