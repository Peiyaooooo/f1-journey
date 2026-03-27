from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/f1journey"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "F1_"}


settings = Settings()
