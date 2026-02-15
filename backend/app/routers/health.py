"""ヘルスチェックルーター - 基本 & 詳細エンドポイント"""

import time

import httpx
import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import async_session

router = APIRouter()
logger = structlog.get_logger()


@router.get("/health")
async def health_check():
    """基本ヘルスチェック（ロードバランサー用）"""
    return {"status": "healthy", "service": "fluentedge-api"}


@router.get("/health/detailed")
async def detailed_health_check():
    """詳細ヘルスチェック - 全依存サービスの接続状態を確認"""
    start = time.perf_counter()
    components = {}

    components["database"] = await _check_database()
    components["redis"] = await _check_redis()
    components["llm_provider"] = await _check_llm_provider()

    statuses = [c["status"] for c in components.values()]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif components["database"]["status"] == "unhealthy":
        overall = "unhealthy"
    else:
        overall = "degraded"

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    return {
        "status": overall,
        "service": "fluentedge-api",
        "environment": settings.environment,
        "response_time_ms": elapsed_ms,
        "components": components,
    }


async def _check_database() -> dict:
    start = time.perf_counter()
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "response_time_ms": _elapsed(start)}
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))
        return {
            "status": "unhealthy",
            "response_time_ms": _elapsed(start),
            "error": str(e)[:200],
        }


async def _check_redis() -> dict:
    start = time.perf_counter()
    try:
        from app.redis_client import get_redis

        client = get_redis()
        if client is None:
            return {
                "status": "unhealthy",
                "response_time_ms": _elapsed(start),
                "error": "Not initialized",
            }
        await client.ping()
        return {"status": "healthy", "response_time_ms": _elapsed(start)}
    except Exception as e:
        logger.error("health_check_redis_failed", error=str(e))
        return {
            "status": "unhealthy",
            "response_time_ms": _elapsed(start),
            "error": str(e)[:200],
        }


async def _check_llm_provider() -> dict:
    start = time.perf_counter()
    try:
        if settings.llm_provider == "azure_foundry":
            url = settings.azure_ai_foundry_endpoint
        elif settings.llm_provider == "anthropic":
            url = "https://api.anthropic.com"
        else:
            return {
                "status": "healthy",
                "response_time_ms": _elapsed(start),
                "note": f"Provider {settings.llm_provider} - skipped",
            }

        if not url:
            return {
                "status": "degraded",
                "response_time_ms": _elapsed(start),
                "error": "Endpoint not configured",
            }

        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.head(url)
        return {
            "status": "healthy",
            "response_time_ms": _elapsed(start),
            "provider": settings.llm_provider,
        }
    except Exception as e:
        logger.warning("health_check_llm_failed", error=str(e))
        return {
            "status": "degraded",
            "response_time_ms": _elapsed(start),
            "error": str(e)[:200],
            "provider": settings.llm_provider,
        }


def _elapsed(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
