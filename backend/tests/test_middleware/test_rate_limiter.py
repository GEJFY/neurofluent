"""レートリミッターミドルウェアのテスト"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.middleware.rate_limiter import EXEMPT_PATHS, RateLimitMiddleware


class TestRateLimitMiddleware:
    """RateLimitMiddleware のテスト"""

    def test_exempt_paths(self):
        """免除パスが正しく定義されている"""
        assert "/health" in EXEMPT_PATHS
        assert "/health/detailed" in EXEMPT_PATHS
        assert "/docs" in EXEMPT_PATHS
        assert "/openapi.json" in EXEMPT_PATHS

    def test_window_seconds(self):
        """ウィンドウサイズが60秒"""
        assert RateLimitMiddleware.WINDOW_SECONDS == 60

    def test_identify_client_unauthenticated(self):
        """未認証リクエストはIP + 30req/min"""
        middleware = RateLimitMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"

        key, limit = middleware._identify_client(mock_request)
        assert key == "rate:ip:192.168.1.1"
        assert limit == 30  # デフォルト unauthenticated limit

    def test_identify_client_authenticated(self):
        """認証済みリクエストはuser_id + 100req/min"""
        middleware = RateLimitMiddleware(app=MagicMock())

        # 有効なJWTトークンを生成
        from app.routers.auth import create_access_token

        token = create_access_token("test-user-id")

        mock_request = MagicMock()
        mock_request.headers = {"Authorization": f"Bearer {token}"}
        mock_request.client.host = "192.168.1.1"

        key, limit = middleware._identify_client(mock_request)
        assert key == "rate:user:test-user-id"
        assert limit == 100  # デフォルト authenticated limit

    def test_identify_client_invalid_token(self):
        """無効なトークンの場合はIPベースにフォールバック"""
        middleware = RateLimitMiddleware(app=MagicMock())

        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer invalid-token"}
        mock_request.client.host = "10.0.0.1"

        key, limit = middleware._identify_client(mock_request)
        assert key == "rate:ip:10.0.0.1"
        assert limit == 30

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self):
        """レートリミット内であればリクエストが許可される"""
        middleware = RateLimitMiddleware(app=MagicMock())

        # pipeline() は同期メソッド、execute() は非同期
        mock_pipe = MagicMock()
        mock_pipe.execute = AsyncMock(return_value=[None, None, 5, None])

        mock_redis = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe

        allowed, count, retry = await middleware._check_rate_limit(
            mock_redis, "rate:ip:1.2.3.4", 30
        )

        assert allowed is True
        assert count == 5
        assert retry == 0

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self):
        """レートリミット超過時はリクエストが拒否される"""
        middleware = RateLimitMiddleware(app=MagicMock())

        mock_pipe = MagicMock()
        mock_pipe.execute = AsyncMock(return_value=[None, None, 31, None])

        mock_redis = MagicMock()
        mock_redis.pipeline.return_value = mock_pipe
        mock_redis.zrange = AsyncMock(return_value=[("1234567890.0", 1234567890.0)])

        allowed, count, retry = await middleware._check_rate_limit(
            mock_redis, "rate:ip:1.2.3.4", 30
        )

        assert allowed is False
        assert count == 31
        assert retry >= 1

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_error_allows(self):
        """Redisエラー時はリクエストを許可する（フェイルオープン）"""
        middleware = RateLimitMiddleware(app=MagicMock())

        mock_redis = MagicMock()
        mock_redis.pipeline.side_effect = Exception("Redis connection refused")

        allowed, count, retry = await middleware._check_rate_limit(
            mock_redis, "rate:ip:1.2.3.4", 30
        )

        assert allowed is True
        assert count == 0
