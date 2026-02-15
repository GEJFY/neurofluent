"""Redisクライアントのテスト"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.redis_client import close_redis, get_redis, init_redis


class TestRedisClient:
    """Redis接続管理のテスト"""

    def test_get_redis_initially_none(self):
        """初期状態ではNoneを返す"""
        import app.redis_client

        # グローバル状態をリセット
        original = app.redis_client._redis_client
        app.redis_client._redis_client = None
        try:
            assert get_redis() is None
        finally:
            app.redis_client._redis_client = original

    @pytest.mark.asyncio
    async def test_init_redis_success(self):
        """正常なRedis接続"""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch("app.redis_client.redis.from_url", return_value=mock_redis):
            result = await init_redis()
            assert result is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_redis_failure(self):
        """Redis接続失敗時はNoneを返す"""
        with patch("app.redis_client.redis.from_url", side_effect=Exception("Connection refused")):
            result = await init_redis()
            assert result is None

    @pytest.mark.asyncio
    async def test_close_redis(self):
        """Redis接続クローズ"""
        import app.redis_client

        mock_client = AsyncMock()
        app.redis_client._redis_client = mock_client

        await close_redis()

        mock_client.aclose.assert_called_once()
        assert app.redis_client._redis_client is None

    @pytest.mark.asyncio
    async def test_close_redis_when_not_connected(self):
        """未接続時のクローズはエラーなし"""
        import app.redis_client

        app.redis_client._redis_client = None
        await close_redis()  # エラーなく完了
