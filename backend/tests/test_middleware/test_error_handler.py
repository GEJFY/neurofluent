"""エラーハンドラーミドルウェアのテスト - 例外の統一フォーマット"""

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport, AsyncClient

from app.exceptions import (
    AppError,
    AuthenticationError,
    NotFoundError,
    LLMProviderError,
)
from app.middleware.error_handler import register_error_handlers


def _create_test_app() -> FastAPI:
    """テスト用FastAPIアプリを作成（エラーハンドラー登録済み）"""
    test_app = FastAPI()
    register_error_handlers(test_app)

    @test_app.get("/test/app-error")
    async def raise_app_error():
        raise AppError(
            message="テストエラー",
            error_code="TEST_ERROR",
            status_code=400,
            details={"field": "value"},
        )

    @test_app.get("/test/auth-error")
    async def raise_auth_error():
        raise AuthenticationError(message="認証失敗")

    @test_app.get("/test/not-found")
    async def raise_not_found():
        raise NotFoundError(message="リソースなし")

    @test_app.get("/test/llm-error")
    async def raise_llm_error():
        raise LLMProviderError(
            message="LLMエラー",
            provider="azure_foundry",
        )

    @test_app.get("/test/unhandled")
    async def raise_unhandled():
        raise RuntimeError("予期しないエラー")

    return test_app


class TestErrorHandler:
    """エラーハンドラーのテスト"""

    @pytest.mark.asyncio
    async def test_app_error_format(self):
        """AppErrorが正しいJSON形式でレスポンスされる"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/app-error")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "TEST_ERROR"
        assert data["error"]["message"] == "テストエラー"
        assert data["error"]["details"] == {"field": "value"}

    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """AuthenticationErrorが401を返す"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/auth-error")

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "AUTHENTICATION_ERROR"

    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """NotFoundErrorが404を返す"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/not-found")

        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_llm_provider_error(self):
        """LLMProviderErrorが502を返し、providerがdetailsに含まれる"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/llm-error")

        assert response.status_code == 502
        data = response.json()
        assert data["error"]["code"] == "LLM_PROVIDER_ERROR"
        assert data["error"]["details"]["provider"] == "azure_foundry"

    @pytest.mark.asyncio
    async def test_unhandled_error(self):
        """未処理例外が500の統一フォーマットで返される"""
        app = _create_test_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test/unhandled")

        assert response.status_code == 500
        data = response.json()
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert data["error"]["message"] == "内部サーバーエラーが発生しました"
        # 内部エラーの詳細は漏洩しない
        assert data["error"]["details"] == {}

    @pytest.mark.asyncio
    async def test_validation_error(self):
        """RequestValidationErrorが422の統一フォーマットで返される"""
        app = _create_test_app()

        @app.post("/test/validate")
        async def validate_endpoint(name: str):
            return {"name": name}

        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # nameパラメータなしでPOST -> バリデーションエラー
            response = await client.post("/test/validate")

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "errors" in data["error"]["details"]
