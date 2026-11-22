from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from audit import audit
from auth import router as auth_router
from config import settings
from database import dispose_engine, get_engine
from rate_limit import RateLimitMiddleware
from redis_client import close_redis, get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        redis = get_redis()
        await redis.ping()
        yield
    except Exception:
        await _shutdown()
        raise
    await _shutdown()


async def _shutdown():
    try:
        await close_redis()
    finally:
        await dispose_engine()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
def health():
    audit("health_check")
    return {"status": "ok", "environment": settings.environment}
