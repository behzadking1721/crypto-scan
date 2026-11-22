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


def test_health_endpoint_returns_200():
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()

    with TestClient(main.app) as client:
        response = client.get("/health")
        assert response.status_code == 200

    body = response.json()
    assert "status" in body
    assert "dependencies" in body
    assert "postgresql" in body["dependencies"]
    assert "redis" in body["dependencies"]


def test_readiness_endpoint_returns_200():
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()

    with TestClient(main.app) as client:
        response = client.get("/ready")
        assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"


def test_health_endpoint_includes_x_request_id():
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()

    with TestClient(main.app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers


def test_readiness_endpoint_includes_x_request_id():
    if not _services_available():
        pytest.skip("PostgreSQL/Redis not available")

    _clear_all_caches()

    with TestClient(main.app) as client:
        response = client.get("/ready")
        assert response.status_code == 200
        assert "x-request-id" in response.headers
