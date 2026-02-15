"""構造化ログミドルウェア - リクエストID自動付与とリクエスト/レスポンスログ"""

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # structlog にリクエストIDをバインド
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()

        logger.info(
            "request_started",
            client=request.client.host if request.client else "unknown",
            query=str(request.query_params) if request.query_params else None,
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise
