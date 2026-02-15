"""セキュリティヘッダーミドルウェアのテスト"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    """全レスポンスにセキュリティヘッダーが含まれる"""
    response = await client.get("/health")
    assert response.status_code == 200

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Permissions-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers


@pytest.mark.asyncio
async def test_permissions_policy(client: AsyncClient):
    """Permissions-Policyが正しく設定される"""
    response = await client.get("/health")
    policy = response.headers["Permissions-Policy"]
    assert "camera=()" in policy
    assert "microphone=(self)" in policy
    assert "geolocation=()" in policy
    assert "payment=()" in policy


@pytest.mark.asyncio
async def test_csp_header(client: AsyncClient):
    """Content-Security-Policyが設定される"""
    response = await client.get("/health")
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


@pytest.mark.asyncio
async def test_no_hsts_in_dev(client: AsyncClient):
    """dev環境ではHSTSヘッダーが設定されない"""
    response = await client.get("/health")
    assert "Strict-Transport-Security" not in response.headers
