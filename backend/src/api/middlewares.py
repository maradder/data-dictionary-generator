"""Middleware for request logging and processing."""
import logging
import time
from collections.abc import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def log_requests_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log all HTTP requests and responses.

    Captures request method, path, response status, and processing time.

    Args:
        request: Incoming HTTP request
        call_next: Next middleware or route handler

    Returns:
        Response: HTTP response with added timing header
    """
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(round(duration_ms, 2))

    return response
