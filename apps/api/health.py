import logging

from sqlalchemy import text

from database import get_engine
from logger import get_logger
from redis_client import get_redis

logger = get_logger()


async def check_postgres() -> dict:
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:
        logger.error(
            "postgres_health_check_failed",
            extra={"exception_type": type(exc).__name__},
        )
        return {"status": "unhealthy", "error": "connection_failed"}


async def check_redis() -> dict:
    try:
        redis = get_redis()
        await redis.ping()
        return {"status": "healthy"}
    except Exception as exc:
        logger.error(
            "redis_health_check_failed",
            extra={"exception_type": type(exc).__name__},
        )
        return {"status": "unhealthy", "error": "connection_failed"}


async def health_check() -> dict:
    postgres = await check_postgres()
    redis = await check_redis()

    overall = "healthy"
    if postgres["status"] != "healthy" or redis["status"] != "healthy":
        overall = "degraded"

    return {
        "status": overall,
        "dependencies": {
            "postgresql": postgres,
            "redis": redis,
        },
    }
