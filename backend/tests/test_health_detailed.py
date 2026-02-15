"""ヘルスチェックAPI 詳細テスト"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_basic_response(client: AsyncClient):
    """基本ヘルスチェックのレスポンス構造"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fluentedge-api"


@pytest.mark.asyncio
async def test_health_detailed_response_structure(client: AsyncClient):
    """詳細ヘルスチェックのレスポンス構造"""
    with patch("app.routers.health._check_database") as mock_db, \
         patch("app.routers.health._check_redis") as mock_redis, \
         patch("app.routers.health._check_llm_provider") as mock_llm:

        mock_db.return_value = {"status": "healthy", "response_time_ms": 1.0}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 0.5}
        mock_llm.return_value = {"status": "healthy", "response_time_ms": 2.0, "provider": "azure_foundry"}

        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "components" in data
        assert "response_time_ms" in data
        assert "database" in data["components"]
        assert "redis" in data["components"]
        assert "llm_provider" in data["components"]


@pytest.mark.asyncio
async def test_health_detailed_all_healthy(client: AsyncClient):
    """全コンポーネント正常時はhealthy"""
    with patch("app.routers.health._check_database") as mock_db, \
         patch("app.routers.health._check_redis") as mock_redis, \
         patch("app.routers.health._check_llm_provider") as mock_llm:

        mock_db.return_value = {"status": "healthy", "response_time_ms": 1.0}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 0.5}
        mock_llm.return_value = {"status": "healthy", "response_time_ms": 2.0}

        response = await client.get("/health/detailed")
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_detailed_db_unhealthy(client: AsyncClient):
    """DB障害時はunhealthy"""
    with patch("app.routers.health._check_database") as mock_db, \
         patch("app.routers.health._check_redis") as mock_redis, \
         patch("app.routers.health._check_llm_provider") as mock_llm:

        mock_db.return_value = {"status": "unhealthy", "response_time_ms": 0, "error": "Connection refused"}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 0.5}
        mock_llm.return_value = {"status": "healthy", "response_time_ms": 2.0}

        response = await client.get("/health/detailed")
        data = response.json()
        assert data["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_health_detailed_llm_degraded(client: AsyncClient):
    """LLM障害時はdegraded"""
    with patch("app.routers.health._check_database") as mock_db, \
         patch("app.routers.health._check_redis") as mock_redis, \
         patch("app.routers.health._check_llm_provider") as mock_llm:

        mock_db.return_value = {"status": "healthy", "response_time_ms": 1.0}
        mock_redis.return_value = {"status": "healthy", "response_time_ms": 0.5}
        mock_llm.return_value = {"status": "degraded", "response_time_ms": 0, "error": "Timeout"}

        response = await client.get("/health/detailed")
        data = response.json()
        assert data["status"] == "degraded"
