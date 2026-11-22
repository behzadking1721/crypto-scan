import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

import config
import database
import main
import redis_client

pytestmark = pytest.mark.integration


def _services_available() -> bool:
    async def check():
        try:
            engine = database.get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await redis_client.get_redis().ping()
            return True
        except Exception:
            return False
        finally:
            await redis_client.close_redis()
            await database.dispose_engine()

    return asyncio.run(check())


def _clear_all_caches():
    database.get_engine.cache_clear()
    database.get_sessionmaker.cache_clear()
    redis_client.get_redis.cache_clear()


def test_lifespan_startup_and_shutdown():
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()

    with TestClient(main.app) as client:
        response = client.get("/health")
        assert response.status_code == 200

    assert database.get_engine.cache_info().currsize == 0
    assert redis_client.get_redis.cache_info().currsize == 0


def test_lifespan_redis_failure_disposes_postgres(monkeypatch):
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()
    monkeypatch.setattr(config.settings, "redis_url", "redis://localhost:6399/0")

    with pytest.raises(Exception):
        with TestClient(main.app):
            pass

    assert database.get_engine.cache_info().currsize == 0
    assert redis_client.get_redis.cache_info().currsize == 0