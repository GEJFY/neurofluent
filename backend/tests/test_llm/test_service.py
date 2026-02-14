"""LLMサービスのテスト - LLMService & claude_serviceブリッジ"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.llm.service import LLMService


class TestLLMService:
    """LLMServiceのテスト"""

    @pytest.mark.asyncio
    async def test_llm_service_chat(self):
        """LLMService.chatがルーター経由で応答を返す"""
        service = LLMService.__new__(LLMService)
        service.router = MagicMock()
        service.router.chat = AsyncMock(return_value="test response")

        result = await service.chat(
            messages=[{"role": "user", "content": "hello"}],
            model="haiku",
            max_tokens=512,
            system="Be helpful",
        )

        assert result == "test response"
        service.router.chat.assert_called_once_with(
            [{"role": "user", "content": "hello"}],
            "haiku",
            512,
            "Be helpful",
        )

    @pytest.mark.asyncio
    async def test_llm_service_chat_json(self):
        """LLMService.chat_jsonがルーター経由でJSON応答を返す"""
        service = LLMService.__new__(LLMService)
        service.router = MagicMock()
        service.router.chat_json = AsyncMock(return_value={"key": "value"})

        result = await service.chat_json(
            messages=[{"role": "user", "content": "give json"}],
        )

        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_llm_service_get_usage_info(self):
        """LLMService.get_usage_infoがルーター経由で使用量情報を返す"""
        service = LLMService.__new__(LLMService)
        service.router = MagicMock()
        service.router.get_usage_info = AsyncMock(
            return_value={"text": "hi", "input_tokens": 10, "output_tokens": 5, "model": "test"}
        )

        result = await service.get_usage_info(
            messages=[{"role": "user", "content": "hi"}],
        )

        assert result["text"] == "hi"
        assert result["input_tokens"] == 10
        assert result["output_tokens"] == 5

    def test_claude_bridge_compatibility(self):
        """claude_serviceがLLMServiceインスタンスとして動作する

        from app.services.claude_service import claude_service
        が正しく LLMService インスタンスを返すことを確認。
        """
        with patch("app.llm.service.LLMService._build_router") as mock_build:
            mock_build.return_value = MagicMock()

            # シングルトンをリセット
            LLMService._instance = None

            from app.services.claude_service import claude_service

            # claude_serviceはLLMServiceのインスタンスであること
            assert hasattr(claude_service, "chat")
            assert hasattr(claude_service, "chat_json")
            assert hasattr(claude_service, "get_usage_info")

            # テスト後にシングルトンをリセット
            LLMService._instance = None
