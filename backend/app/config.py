from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./f1journey.db"
    cors_origins: str = "http://localhost:3000"
    kiwi_api_key: str = ""
    rome2rio_api_key: str = ""
    seatgeek_client_id: str = ""
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 7
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/calendar/callback"
    resend_api_key: str = ""

    model_config = {"env_prefix": "F1_"}


settings = Settings()
