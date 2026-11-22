import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_intel"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")