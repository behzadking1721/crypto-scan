import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import health


@pytest.fixture(autouse=True)
def clear_caches():
    health.get_engine.cache_clear()
    health.get_redis.cache_clear()
    yield
    health.get_engine.cache_clear()
    health.get_redis.cache_clear()


class FakeConn:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def execute(self, *args, **kwargs):
        return None


class FakeEngine:
    def connect(self):
        return FakeConn()


class FakeRedis:
    async def ping(self):
        return True


@pytest.mark.asyncio
async def test_check_postgres_healthy():
    fake_engine = FakeEngine()
    with patch.object(health, "get_engine", return_value=fake_engine):
        result = await health.check_postgres()
    assert result == {"status": "healthy"}


@pytest.mark.asyncio
async def test_check_postgres_unhealthy():
    with patch.object(
        health,
        "get_engine",
        side_effect=Exception("connection refused"),
    ):
        result = await health.check_postgres()
    assert result["status"] == "unhealthy"
    assert result["error"] == "connection_failed"


@pytest.mark.asyncio
async def test_check_redis_healthy():
    fake_redis = FakeRedis()
    with patch.object(health, "get_redis", return_value=fake_redis):
        result = await health.check_redis()
    assert result == {"status": "healthy"}


@pytest.mark.asyncio
async def test_check_redis_unhealthy():
    with patch.object(
        health,
        "get_redis",
        side_effect=Exception("connection refused"),
    ):
        result = await health.check_redis()
    assert result["status"] == "unhealthy"
    assert result["error"] == "connection_failed"


@pytest.mark.asyncio
async def test_health_check_all_healthy():
    fake_engine = FakeEngine()
    fake_redis = FakeRedis()
    with patch.object(health, "get_engine", return_value=fake_engine), patch.object(
        health, "get_redis", return_value=fake_redis
    ):
        result = await health.health_check()
    assert result["status"] == "healthy"
    assert result["dependencies"]["postgresql"]["status"] == "healthy"
    assert result["dependencies"]["redis"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_postgres_unhealthy():
    with patch.object(
        health,
        "get_engine",
        side_effect=Exception("connection refused"),
    ), patch.object(health, "get_redis", return_value=FakeRedis()):
        result = await health.health_check()
    assert result["status"] == "degraded"
    assert result["dependencies"]["postgresql"]["status"] == "unhealthy"
    assert result["dependencies"]["redis"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_redis_unhealthy():
    fake_engine = FakeEngine()
    with patch.object(health, "get_engine", return_value=fake_engine), patch.object(
        health, "get_redis", side_effect=Exception("connection refused")
    ):
        result = await health.health_check()
    assert result["status"] == "degraded"
    assert result["dependencies"]["postgresql"]["status"] == "healthy"
    assert result["dependencies"]["redis"]["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_health_check_both_unhealthy():
    with patch.object(
        health,
        "get_engine",
        side_effect=Exception("connection refused"),
    ), patch.object(
        health, "get_redis", side_effect=Exception("connection refused")
    ):
        result = await health.health_check()
    assert result["status"] == "degraded"
    assert result["dependencies"]["postgresql"]["status"] == "unhealthy"
    assert result["dependencies"]["redis"]["status"] == "unhealthy"
