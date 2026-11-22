from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Crypto Intelligence API"
    environment: str = "development"
    database_url: str
    redis_url: str
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_max_requests: int = 60
    rate_limit_window_seconds: int = 60
    rate_limit_fail_open: bool = False
    rate_limit_trust_proxy: bool = False
    rate_limit_trusted_proxies: list[str] = []
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
