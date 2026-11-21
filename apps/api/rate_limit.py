import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

_LIMITS: dict[str, deque] = defaultdict(lambda: deque())
_WINDOW = 60
_MAX = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else "anon"
        now = time.time()
        q = _LIMITS[key]
        while q and now - q[0] > _WINDOW:
            q.popleft()
        if len(q) >= _MAX:
            raise HTTPException(status_code=429, detail="Too many requests")
        q.append(now)
        return await call_next(request)
