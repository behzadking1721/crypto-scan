from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Crypto Intelligence API"
    environment: str = "development"
    database_url: str
    redis_url: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
