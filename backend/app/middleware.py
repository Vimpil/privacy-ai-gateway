"""Error handling middleware and custom exceptions."""

import json
import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter: 100 requests per minute per IP."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ip_times: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        minute_ago = now - 60

        # Clean old entries
        self.ip_times[ip] = [t for t in self.ip_times[ip] if t > minute_ago]

        # Check rate limit
        if len(self.ip_times[ip]) >= self.requests_per_minute:
            return JSONResponse(
                {"status": "error", "error": "Rate limit exceeded"},
                status_code=429,
            )

        self.ip_times[ip].append(now)
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch all exceptions and return consistent error responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                {
                    "status": "error",
                    "error": "Internal server error",
                },
                status_code=500,
            )

