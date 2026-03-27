from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./f1journey.db"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "F1_"}


settings = Settings()
