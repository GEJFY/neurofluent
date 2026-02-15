"""APIレートリミッターミドルウェア - Redis分散レート制限

認証済みユーザーと未認証リクエストで異なるレート制限を適用。
Redis Sorted Set + Sliding Window方式で制御。
"""

import time

import structlog
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.redis_client import get_redis

logger = structlog.get_logger()

EXEMPT_PATHS = {"/health", "/health/detailed", "/docs", "/openapi.json", "/redoc"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed スライディングウィンドウ方式のレートリミッター

    - 認証済みユーザー: 100 req/min
    - 未認証リクエスト: 30 req/min
    """

    WINDOW_SECONDS = 60

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        redis_client = get_redis()
        if redis_client is None:
            return await call_next(request)

        key, limit = self._identify_client(request)

        allowed, current_count, retry_after = await self._check_rate_limit(
            redis_client, key, limit
        )

        if not allowed:
            logger.warning(
                "rate_limit_exceeded", key=key, current=current_count, limit=limit
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_ERROR",
                        "message": "Too many requests. Please wait.",
                        "details": {"retry_after": retry_after},
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        response = await call_next(request)
        remaining = max(0, limit - current_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + self.WINDOW_SECONDS
        )
        return response

    def _identify_client(self, request: Request) -> tuple[str, int]:
        """クライアント識別キーとレート制限値を決定"""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from jose import jwt as jose_jwt

                token = auth_header[7:]
                payload = jose_jwt.decode(
                    token,
                    settings.jwt_secret_key,
                    algorithms=[settings.jwt_algorithm],
                    options={"verify_exp": False},
                )
                user_id = payload.get("sub", "unknown")
                return f"rate:user:{user_id}", settings.rate_limit_authenticated
            except Exception:
                pass

        client_ip = request.client.host if request.client else "unknown"
        return f"rate:ip:{client_ip}", settings.rate_limit_unauthenticated

    async def _check_rate_limit(
        self, redis_client, key: str, limit: int
    ) -> tuple[bool, int, int]:
        """Redis Sorted Setによるスライディングウィンドウチェック"""
        now = time.time()
        window_start = now - self.WINDOW_SECONDS

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {f"{now}": now})
            pipe.zcard(key)
            pipe.expire(key, self.WINDOW_SECONDS + 10)
            results = await pipe.execute()

            current_count = results[2]

            if current_count > limit:
                oldest = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(self.WINDOW_SECONDS - (now - oldest[0][1])) + 1
                else:
                    retry_after = self.WINDOW_SECONDS
                return False, current_count, max(1, retry_after)

            return True, current_count, 0
        except Exception as e:
            logger.warning("rate_limit_check_failed", error=str(e))
            return True, 0, 0
