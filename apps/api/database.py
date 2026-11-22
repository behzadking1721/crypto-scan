from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_POOL_SIZE = 10
_MAX_OVERFLOW = 20


def _build_engine() -> AsyncEngine:
    from config import settings

    return create_async_engine(
        settings.database_url,
        pool_size=_POOL_SIZE,
        max_overflow=_MAX_OVERFLOW,
        pool_pre_ping=True,
    )


@lru_cache
def get_engine() -> AsyncEngine:
    return _build_engine()


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        yield session


def _engine_built() -> bool:
    return get_engine.cache_info().currsize > 0


async def dispose_engine() -> None:
    if not _engine_built():
        get_sessionmaker.cache_clear()
        return
    engine = get_engine()
    await engine.dispose()
    get_sessionmaker.cache_clear()
    get_engine.cache_clear()