import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

_lock = Lock()
_buckets: dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Optional in-memory rate limit for upload endpoints (single-instance demos)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        if request.method == "POST" and request.url.path == "/api/upload":
            client = request.client.host if request.client else "unknown"
            now = time.time()
            window = 60.0
            limit = settings.rate_limit_uploads_per_minute

            with _lock:
                hits = [t for t in _buckets[client] if now - t < window]
                if len(hits) >= limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many uploads. Please wait a minute and try again."},
                    )
                hits.append(now)
                _buckets[client] = hits

        return await call_next(request)
