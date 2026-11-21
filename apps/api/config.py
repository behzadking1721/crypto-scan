from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Crypto Intelligence API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_intel"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
