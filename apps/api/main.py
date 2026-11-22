from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from audit import audit
from auth import router as auth_router
from config import settings
from database import dispose_engine, get_engine
from health import health_check
from logger import LoggingMiddleware, setup_logging
from rate_limit import RateLimitMiddleware
from redis_client import close_redis, get_redis


import logging as _stdlib_logging

logger = _stdlib_logging.getLogger("crypto.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        redis = get_redis()
        await redis.ping()
        logger.info("startup", extra={"event": "startup"})
        yield
    except Exception:
        logger.exception("startup_failed", extra={"event": "startup_failed"})
        await _shutdown()
        raise
    logger.info("shutdown", extra={"event": "shutdown"})
    await _shutdown()


async def _shutdown():
    try:
        await close_redis()
    finally:
        await dispose_engine()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
async def health():
    await audit("health_check")
    result = await health_check()
    return result


@app.get("/ready")
async def ready():
    await audit("readiness_check")
    result = await health_check()
    if result["status"] != "healthy":
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Service not ready")
    return result
