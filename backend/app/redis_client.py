"""Redis接続管理 - アプリケーション全体で共有するRedisクライアント"""

import redis.asyncio as redis
import structlog

from app.config import settings

logger = structlog.get_logger()

_redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis | None:
    """Redis接続を初期化（接続失敗時はNoneを返す）"""
    global _redis_client
    try:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        await _redis_client.ping()
        logger.info("redis_connected", url=settings.redis_url)
        return _redis_client
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e))
        _redis_client = None
        return None


async def close_redis() -> None:
    """Redis接続をクローズ"""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> redis.Redis | None:
    """現在のRedisクライアントを取得"""
    return _redis_client
