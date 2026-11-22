import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from config import settings
from redis_client import close_redis, get_redis

PREFIX = "ratelimit"

# Atomic: INCR the counter and set TTL only on the first increment, in a single
# Redis round-trip via Lua. Returns the new counter value.
_LUA_INCR_WITH_TTL = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


async def _consume(redis, redis_key: str, window: int) -> int:
    return await redis.eval(_LUA_INCR_WITH_TTL, 1, redis_key, window)


def _rate_limited_response(request_id: str, status_code: int, detail: str):
    return JSONResponse(
        content={"error": detail, "status_code": status_code},
        status_code=status_code,
        headers={"x-request-id": request_id},
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Health endpoints bypass rate limiting entirely so they remain
        # available even when Redis is down (fail-closed would otherwise
        # block them before they can report dependency status).
        if request.method == "GET" and request.url.path in ("/health", "/ready"):
            return await call_next(request)

        client_host = self._client_ip(request)
        redis_key = f"{PREFIX}:{client_host}"
        max_requests = settings.rate_limit_max_requests
        window = settings.rate_limit_window_seconds
        request_id = (
            getattr(request.state, "request_id", None) or str(uuid.uuid4())
        )

        current = None
        try:
            redis = get_redis()
            current = await _consume(redis, redis_key, window)
        except Exception:
            # The cached client may be dead (e.g. its event loop was torn down).
            # Recreate it once before applying the failure policy.
            try:
                await close_redis()
            except Exception:
                pass
            get_redis.cache_clear()
            try:
                redis = get_redis()
                current = await _consume(redis, redis_key, window)
            except Exception:
                if settings.rate_limit_fail_open:
                    return await call_next(request)
                return _rate_limited_response(
                    request_id, 503, "Rate limiting unavailable"
                )

        if current > max_requests:
            return _rate_limited_response(request_id, 429, "Too many requests")

        return await call_next(request)

    @staticmethod
    def _client_ip(request: Request) -> str:
        direct = request.client.host if request.client else "anon"
        if not settings.rate_limit_trust_proxy:
            return direct
        # Honor X-Forwarded-For only when the direct client is a trusted proxy.
        if direct in settings.rate_limit_trusted_proxies:
            xff = request.headers.get("x-forwarded-for")
            if xff:
                return xff.split(",")[0].strip()
        return direct
