"""ロギングミドルウェアのテスト - リクエストID付与"""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.middleware.logging_middleware import RequestLoggingMiddleware


def _create_test_app() -> FastAPI:
    """テスト用FastAPIアプリを作成（ロギングミドルウェア付き）"""
    test_app = FastAPI()
    test_app.add_middleware(RequestLoggingMiddleware)

    @test_app.get("/test/hello")
    async def hello():
        return {"message": "hello"}

    return test_app


class TestLoggingMiddleware:
    """RequestLoggingMiddlewareのテスト"""

    @pytest.mark.asyncio
    async def test_request_id_header(self):
        """レスポンスにX-Request-IDヘッダーが付与される"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/hello")

        assert response.status_code == 200
        assert "x-request-id" in response.headers
        # 自動生成されたUUID形式のリクエストID
        request_id = response.headers["x-request-id"]
        assert len(request_id) > 0

    @pytest.mark.asyncio
    async def test_custom_request_id(self):
        """カスタムX-Request-IDヘッダーが引き継がれる"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        custom_id = "custom-request-id-12345"

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/test/hello",
                headers={"X-Request-ID": custom_id},
            )

        assert response.status_code == 200
        assert response.headers["x-request-id"] == custom_id

    @pytest.mark.asyncio
    async def test_different_requests_get_different_ids(self):
        """異なるリクエストには異なるIDが付与される"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp1 = await client.get("/test/hello")
            resp2 = await client.get("/test/hello")

        id1 = resp1.headers["x-request-id"]
        id2 = resp2.headers["x-request-id"]
        assert id1 != id2
