from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    home_city: str | None = None
    preferred_currency: str = "USD"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: int
    email: str
    home_city: str | None
    preferred_currency: str
    model_config = {"from_attributes": True}
