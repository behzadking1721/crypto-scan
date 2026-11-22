from collections.abc import AsyncGenerator
from functools import lru_cache

from redis.asyncio import Redis

_MAX_CONNECTIONS = 10


@lru_cache
def get_redis() -> Redis:
    from config import settings

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=_MAX_CONNECTIONS,
    )


def _redis_built() -> bool:
    return get_redis.cache_info().currsize > 0


async def close_redis() -> None:
    if not _redis_built():
        get_redis.cache_clear()
        return
    client = get_redis()
    await client.aclose()
    get_redis.cache_clear()


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    yield get_redis()