import inspect

import pytest
from redis.asyncio import Redis

import redis_client


@pytest.fixture(autouse=True)
def clear_redis_cache():
    redis_client.get_redis.cache_clear()
    yield
    redis_client.get_redis.cache_clear()


def test_get_redis_client_is_async_generator():
    assert inspect.isasyncgenfunction(redis_client.get_redis_client)


def test_redis_not_built_before_use():
    assert redis_client.get_redis.cache_info().currsize == 0


async def test_close_redis_without_client_does_not_build_one():
    await redis_client.close_redis()
    assert redis_client.get_redis.cache_info().currsize == 0


def test_get_redis_returns_client_without_connecting():
    client = redis_client.get_redis()
    assert isinstance(client, Redis)
    assert client.connection_pool.connection_kwargs.get("decode_responses") is True
    assert client.connection_pool.max_connections == 10
    assert redis_client.get_redis.cache_info().currsize == 1


async def test_close_redis_clears_cache():
    redis_client.get_redis()
    assert redis_client.get_redis.cache_info().currsize == 1

    await redis_client.close_redis()

    assert redis_client.get_redis.cache_info().currsize == 0


async def test_close_redis_is_idempotent():
    redis_client.get_redis()
    await redis_client.close_redis()
    await redis_client.close_redis()
    assert redis_client.get_redis.cache_info().currsize == 0