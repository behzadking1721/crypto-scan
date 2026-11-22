import asyncio
from unittest.mock import patch

import pytest
from starlette.requests import Request

import rate_limit


def _make_request(
    client_host: str = "127.0.0.1",
    headers: list[tuple[str, str]] | None = None,
    path: str = "/test",
    method: str = "GET",
) -> Request:
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(b"host", b"testserver")]
        + [(k.encode(), v.encode()) for k, v in (headers or [])],
        "client": (client_host, 54321),
        "server": ("testserver", 80),
        "scheme": "http",
        "root_path": "",
    }
    return Request(scope)


_CALL_NEXT_RESULT = object()


async def _call_next(request: Request):
    return _CALL_NEXT_RESULT


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.expires = {}
        self.should_raise = False

    async def incr(self, key: str) -> int:
        if self.should_raise:
            raise ConnectionError("redis down")
        self.store[key] = self.store.get(key, 0) + 1
        return self.store[key]

    async def expire(self, key: str, ttl: int) -> None:
        self.expires[key] = ttl

    async def eval(self, script: str, numkeys: int, *keys_and_args) -> int:
        if self.should_raise:
            raise ConnectionError("redis down")
        key = keys_and_args[0]
        window = int(keys_and_args[numkeys])
        self.store[key] = self.store.get(key, 0) + 1
        current = self.store[key]
        if current == 1:
            self.expires[key] = window
        return current


@pytest.fixture
def fake_redis():
    fake = FakeRedis()
    with patch.object(rate_limit, "get_redis", return_value=fake):
        yield fake


@pytest.fixture(autouse=True)
def restore_settings():
    originals = {
        "rate_limit_max_requests": rate_limit.settings.rate_limit_max_requests,
        "rate_limit_window_seconds": rate_limit.settings.rate_limit_window_seconds,
        "rate_limit_fail_open": rate_limit.settings.rate_limit_fail_open,
        "rate_limit_trust_proxy": rate_limit.settings.rate_limit_trust_proxy,
        "rate_limit_trusted_proxies": list(
            rate_limit.settings.rate_limit_trusted_proxies
        ),
    }
    yield
    for k, v in originals.items():
        setattr(rate_limit.settings, k, v)


@pytest.mark.asyncio
async def test_allows_requests_within_limit(fake_redis):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    for _ in range(5):
        await rate_limit.RateLimitMiddleware(app=None).dispatch(
            request, _call_next
        )

    assert fake_redis.store[f"ratelimit:1.2.3.4"] == 5


@pytest.mark.asyncio
async def test_blocks_requests_over_limit(fake_redis, monkeypatch):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    monkeypatch.setattr(rate_limit.settings, "rate_limit_max_requests", 2)
    monkeypatch.setattr(rate_limit.settings, "rate_limit_window_seconds", 60)

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    resp = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    assert resp.status_code == 429
    assert "x-request-id" in resp.headers


@pytest.mark.asyncio
async def test_429_not_converted_to_500(fake_redis, monkeypatch):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    monkeypatch.setattr(rate_limit.settings, "rate_limit_max_requests", 1)
    monkeypatch.setattr(rate_limit.settings, "rate_limit_window_seconds", 60)

    await rate_limit.RateLimitMiddleware(app=None).dispatch(request, _call_next)
    resp = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert resp.status_code == 429


@pytest.mark.asyncio
async def test_ttl_set_on_first_request(fake_redis):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    assert fake_redis.expires[f"ratelimit:1.2.3.4"] == 60


@pytest.mark.asyncio
async def test_ttl_not_reset_on_subsequent_requests(fake_redis):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    assert len(fake_redis.expires) == 1


@pytest.mark.asyncio
async def test_atomic_incr_and_ttl_concurrent(fake_redis):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await asyncio.gather(
        *[
            rate_limit.RateLimitMiddleware(app=None).dispatch(
                request, _call_next
            )
            for _ in range(20)
        ]
    )

    assert fake_redis.store[f"ratelimit:1.2.3.4"] == 20
    assert fake_redis.expires[f"ratelimit:1.2.3.4"] == 60


@pytest.mark.asyncio
async def test_no_key_without_ttl_after_first_request(fake_redis):
    request = _make_request("1.2.3.4")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    key = f"ratelimit:1.2.3.4"
    assert key in fake_redis.store
    assert key in fake_redis.expires


@pytest.mark.asyncio
async def test_different_clients_get_different_keys(fake_redis):
    fake_redis.store.clear()

    req_a = _make_request("10.0.0.1")
    req_b = _make_request("10.0.0.2")

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        req_a, _call_next
    )
    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        req_b, _call_next
    )

    assert f"ratelimit:10.0.0.1" in fake_redis.store
    assert f"ratelimit:10.0.0.2" in fake_redis.store


@pytest.mark.asyncio
async def test_x_forwarded_for_not_trusted_by_default(fake_redis):
    request = _make_request(
        "10.0.0.5",
        headers=[("x-forwarded-for", "203.0.113.5")],
    )
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    assert f"ratelimit:10.0.0.5" in fake_redis.store
    assert f"ratelimit:203.0.113.5" not in fake_redis.store


@pytest.mark.asyncio
async def test_x_forwarded_for_trusted_when_configured(fake_redis, monkeypatch):
    monkeypatch.setattr(rate_limit.settings, "rate_limit_trust_proxy", True)
    monkeypatch.setattr(
        rate_limit.settings, "rate_limit_trusted_proxies", ["10.0.0.5"]
    )

    request = _make_request(
        "10.0.0.5",
        headers=[("x-forwarded-for", "203.0.113.5")],
    )
    fake_redis.store.clear()
    fake_redis.expires.clear()

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )

    assert f"ratelimit:203.0.113.5" in fake_redis.store
    assert f"ratelimit:10.0.0.5" not in fake_redis.store


@pytest.mark.asyncio
async def test_redis_down_fail_open_allows_request(fake_redis, monkeypatch):
    request = _make_request("1.2.3.4")
    fake_redis.should_raise = True
    monkeypatch.setattr(rate_limit.settings, "rate_limit_fail_open", True)

    response = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert response is _CALL_NEXT_RESULT


@pytest.mark.asyncio
async def test_redis_down_fail_closed_returns_503(fake_redis, monkeypatch):
    request = _make_request("1.2.3.4")
    fake_redis.should_raise = True
    monkeypatch.setattr(rate_limit.settings, "rate_limit_fail_open", False)

    resp = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert resp.status_code == 503
    assert "x-request-id" in resp.headers


@pytest.mark.asyncio
async def test_health_endpoint_bypasses_rate_limiting_when_redis_down(
    fake_redis, monkeypatch
):
    request = _make_request("1.2.3.4", path="/health")
    fake_redis.should_raise = True
    monkeypatch.setattr(rate_limit.settings, "rate_limit_fail_open", False)

    response = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert response is _CALL_NEXT_RESULT


@pytest.mark.asyncio
async def test_ready_endpoint_bypasses_rate_limiting_when_redis_down(
    fake_redis, monkeypatch
):
    request = _make_request("1.2.3.4", path="/ready")
    fake_redis.should_raise = True
    monkeypatch.setattr(rate_limit.settings, "rate_limit_fail_open", False)

    response = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert response is _CALL_NEXT_RESULT


@pytest.mark.asyncio
async def test_health_endpoint_post_not_exempted_when_redis_down(
    fake_redis, monkeypatch
):
    request = _make_request("1.2.3.4", path="/health", method="POST")
    fake_redis.should_raise = True
    monkeypatch.setattr(rate_limit.settings, "rate_limit_fail_open", False)

    resp = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_health_endpoint_bypasses_when_over_limit(fake_redis, monkeypatch):
    request = _make_request("1.2.3.4", path="/health")
    fake_redis.store.clear()
    fake_redis.expires.clear()

    monkeypatch.setattr(rate_limit.settings, "rate_limit_max_requests", 1)
    monkeypatch.setattr(rate_limit.settings, "rate_limit_window_seconds", 60)

    await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    response = await rate_limit.RateLimitMiddleware(app=None).dispatch(
        request, _call_next
    )
    assert response is _CALL_NEXT_RESULT
