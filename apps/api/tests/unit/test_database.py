import inspect

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

import database


@pytest.fixture(autouse=True)
def clear_db_caches():
    database.get_engine.cache_clear()
    database.get_sessionmaker.cache_clear()
    yield
    database.get_engine.cache_clear()
    database.get_sessionmaker.cache_clear()


def test_get_session_is_async_generator():
    assert inspect.isasyncgenfunction(database.get_session)


def test_engine_not_built_before_use():
    assert database.get_engine.cache_info().currsize == 0
    assert database.get_sessionmaker.cache_info().currsize == 0


async def test_dispose_engine_without_engine_does_not_build_one():
    await database.dispose_engine()
    assert database.get_engine.cache_info().currsize == 0
    assert database.get_sessionmaker.cache_info().currsize == 0


async def test_get_engine_returns_async_engine_without_connecting():
    engine = database.get_engine()
    assert isinstance(engine, AsyncEngine)
    assert database.get_engine.cache_info().currsize == 1
    assert database.get_sessionmaker.cache_info().currsize == 0


async def test_get_engine_is_cached_singleton():
    first = database.get_engine()
    second = database.get_engine()
    assert first is second


async def test_dispose_engine_clears_caches():
    database.get_engine()
    database.get_sessionmaker()
    assert database.get_engine.cache_info().currsize == 1
    assert database.get_sessionmaker.cache_info().currsize == 1

    await database.dispose_engine()

    assert database.get_engine.cache_info().currsize == 0
    assert database.get_sessionmaker.cache_info().currsize == 0