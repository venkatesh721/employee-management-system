import logging
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("globalco.requests")


class ProductionMiddleware(BaseHTTPMiddleware):
    """Request observability, security headers, and auth abuse protection."""

    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",", 1)[0].strip() if forwarded else None
        return client_ip or (request.client.host if request.client else "unknown")

    def _rate_limited(self, request: Request) -> bool:
        if settings.ENVIRONMENT.lower() != "production" or request.url.path not in {
            "/api/auth/login",
            "/api/auth/forgot-password",
            "/api/auth/reset-password",
        }:
            return False
        now = time.monotonic()
        cutoff = now - settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
        key = f"{self._client_key(request)}:{request.url.path}"
        with self.lock:
            bucket = self.requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= settings.AUTH_RATE_LIMIT_REQUESTS:
                return True
            bucket.append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        # CORS preflight is owned exclusively by CORSMiddleware. If an OPTIONS
        # request ever reaches this inner middleware, pass it through untouched.
        if request.method == "OPTIONS":
            return await call_next(request)

        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        if self._rate_limited(request):
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={
                    "Retry-After": str(settings.AUTH_RATE_LIMIT_WINDOW_SECONDS),
                    "X-Request-ID": request_id,
                },
            )
        else:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT.lower() == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        logger.info(
            "request_complete method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
            request_id,
        )
        return response
