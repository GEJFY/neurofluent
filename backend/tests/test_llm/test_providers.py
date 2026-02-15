"""LLMプロバイダーのテスト - Azure Foundry, Anthropic Direct, OpenAI互換"""

import json
from unittest.mock import patch

import httpx
import pytest
import respx

from app.llm.base import LLMProvider
from app.llm.providers.anthropic_direct import AnthropicDirectProvider
from app.llm.providers.azure_foundry import AzureFoundryProvider
from app.llm.providers.openai_compat import OpenAICompatibleProvider


# ============================================================
# ヘルパー: Anthropic形式のモックレスポンス
# ============================================================
def _anthropic_response(
    text: str, input_tokens: int = 50, output_tokens: int = 20
) -> dict:
    """Anthropic Messages API形式の正常レスポンスを生成"""
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
        "model": "claude-haiku-4-5-20251001",
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    }


def _openai_response(
    text: str, prompt_tokens: int = 50, completion_tokens: int = 20
) -> dict:
    """OpenAI Chat Completions形式の正常レスポンスを生成"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


# ============================================================
# Azure Foundry Provider テスト
# ============================================================
class TestAzureFoundryProvider:
    """Azure AI Foundry プロバイダーのテスト"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_azure_foundry_chat_success(self):
        """正常なchat呼び出しがテキスト応答を返す"""
        with patch("app.llm.providers.azure_foundry.settings") as mock_settings:
            mock_settings.azure_ai_foundry_endpoint = "https://test.azure.com"
            mock_settings.azure_ai_foundry_api_key = "test-key"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AzureFoundryProvider()

            respx.post("https://test.azure.com/anthropic/v1/messages").mock(
                return_value=httpx.Response(
                    200, json=_anthropic_response("Hello, world!")
                )
            )

            result = await provider.chat(
                messages=[{"role": "user", "content": "Hi"}],
                model="haiku",
            )

            assert result == "Hello, world!"

    @pytest.mark.asyncio
    @respx.mock
    async def test_azure_foundry_chat_json(self):
        """chat_jsonがJSON応答をパースして返す"""
        with patch("app.llm.providers.azure_foundry.settings") as mock_settings:
            mock_settings.azure_ai_foundry_endpoint = "https://test.azure.com"
            mock_settings.azure_ai_foundry_api_key = "test-key"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AzureFoundryProvider()

            json_text = json.dumps({"key": "value", "count": 42})
            respx.post("https://test.azure.com/anthropic/v1/messages").mock(
                return_value=httpx.Response(200, json=_anthropic_response(json_text))
            )

            result = await provider.chat_json(
                messages=[{"role": "user", "content": "Give me JSON"}],
            )

            assert result == {"key": "value", "count": 42}

    @pytest.mark.asyncio
    @respx.mock
    async def test_azure_foundry_get_usage_info(self):
        """get_usage_infoがトークン使用量を含むレスポンスを返す"""
        with patch("app.llm.providers.azure_foundry.settings") as mock_settings:
            mock_settings.azure_ai_foundry_endpoint = "https://test.azure.com"
            mock_settings.azure_ai_foundry_api_key = "test-key"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AzureFoundryProvider()

            respx.post("https://test.azure.com/anthropic/v1/messages").mock(
                return_value=httpx.Response(
                    200,
                    json=_anthropic_response(
                        "Response text", input_tokens=100, output_tokens=50
                    ),
                )
            )

            result = await provider.get_usage_info(
                messages=[{"role": "user", "content": "Test"}],
            )

            assert result["text"] == "Response text"
            assert result["input_tokens"] == 100
            assert result["output_tokens"] == 50
            assert result["model"] == "claude-haiku-test"

    @pytest.mark.asyncio
    @respx.mock
    async def test_azure_foundry_api_error(self):
        """APIエラー時にHTTPStatusErrorが発生する"""
        with patch("app.llm.providers.azure_foundry.settings") as mock_settings:
            mock_settings.azure_ai_foundry_endpoint = "https://test.azure.com"
            mock_settings.azure_ai_foundry_api_key = "test-key"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AzureFoundryProvider()

            respx.post("https://test.azure.com/anthropic/v1/messages").mock(
                return_value=httpx.Response(429, json={"error": "rate limited"})
            )

            with pytest.raises(httpx.HTTPStatusError):
                await provider.chat(
                    messages=[{"role": "user", "content": "Hi"}],
                )


# ============================================================
# Anthropic Direct Provider テスト
# ============================================================
class TestAnthropicDirectProvider:
    """Anthropic Direct APIプロバイダーのテスト"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_anthropic_direct_chat(self):
        """Anthropic Direct APIへのchat呼び出しが正常に動作する"""
        with patch("app.llm.providers.anthropic_direct.settings") as mock_settings:
            mock_settings.anthropic_api_key = "sk-ant-test"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AnthropicDirectProvider()

            respx.post("https://api.anthropic.com/v1/messages").mock(
                return_value=httpx.Response(
                    200, json=_anthropic_response("Direct response")
                )
            )

            result = await provider.chat(
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert result == "Direct response"
            assert provider.name == "anthropic"

    @pytest.mark.asyncio
    @respx.mock
    async def test_anthropic_direct_get_usage_info(self):
        """Anthropic Direct APIのget_usage_infoが正常に動作する"""
        with patch("app.llm.providers.anthropic_direct.settings") as mock_settings:
            mock_settings.anthropic_api_key = "sk-ant-test"
            mock_settings.claude_sonnet_model = "claude-sonnet-test"
            mock_settings.claude_haiku_model = "claude-haiku-test"

            provider = AnthropicDirectProvider()

            respx.post("https://api.anthropic.com/v1/messages").mock(
                return_value=httpx.Response(
                    200,
                    json=_anthropic_response(
                        "usage test", input_tokens=200, output_tokens=100
                    ),
                )
            )

            result = await provider.get_usage_info(
                messages=[{"role": "user", "content": "Test"}],
            )

            assert result["text"] == "usage test"
            assert result["input_tokens"] == 200
            assert result["output_tokens"] == 100


# ============================================================
# OpenAI Compatible Provider テスト
# ============================================================
class TestOpenAICompatProvider:
    """OpenAI互換APIプロバイダーのテスト"""

    @pytest.mark.asyncio
    @respx.mock
    async def test_openai_compat_chat(self):
        """OpenAI互換APIへのchat呼び出しが正常に動作する"""
        with patch("app.llm.providers.openai_compat.settings") as mock_settings:
            mock_settings.local_llm_base_url = "http://localhost:11434"
            mock_settings.local_llm_api_key = "ollama"
            mock_settings.local_model_fast = "llama3.1:8b"
            mock_settings.local_model_smart = "llama3.1:70b"

            provider = OpenAICompatibleProvider()

            respx.post("http://localhost:11434/v1/chat/completions").mock(
                return_value=httpx.Response(
                    200, json=_openai_response("OpenAI response")
                )
            )

            result = await provider.chat(
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert result == "OpenAI response"
            assert provider.name == "openai_compat"

    @pytest.mark.asyncio
    @respx.mock
    async def test_openai_compat_chat_with_system(self):
        """systemプロンプト指定時にOpenAI形式のsystemメッセージに変換される"""
        with patch("app.llm.providers.openai_compat.settings") as mock_settings:
            mock_settings.local_llm_base_url = "http://localhost:11434"
            mock_settings.local_llm_api_key = "ollama"
            mock_settings.local_model_fast = "llama3.1:8b"
            mock_settings.local_model_smart = "llama3.1:70b"

            provider = OpenAICompatibleProvider()

            route = respx.post("http://localhost:11434/v1/chat/completions").mock(
                return_value=httpx.Response(200, json=_openai_response("OK"))
            )

            await provider.chat(
                messages=[{"role": "user", "content": "Hi"}],
                system="You are a helpful assistant.",
            )

            # リクエストボディを検証: systemメッセージが先頭にある
            request_body = json.loads(route.calls[0].request.content)
            assert request_body["messages"][0]["role"] == "system"
            assert (
                request_body["messages"][0]["content"] == "You are a helpful assistant."
            )

    @pytest.mark.asyncio
    @respx.mock
    async def test_openai_compat_get_usage_info(self):
        """OpenAI互換APIのget_usage_infoが正常に動作する"""
        with patch("app.llm.providers.openai_compat.settings") as mock_settings:
            mock_settings.local_llm_base_url = "http://localhost:11434"
            mock_settings.local_llm_api_key = "ollama"
            mock_settings.local_model_fast = "llama3.1:8b"
            mock_settings.local_model_smart = "llama3.1:70b"

            provider = OpenAICompatibleProvider()

            respx.post("http://localhost:11434/v1/chat/completions").mock(
                return_value=httpx.Response(
                    200,
                    json=_openai_response(
                        "test", prompt_tokens=150, completion_tokens=75
                    ),
                )
            )

            result = await provider.get_usage_info(
                messages=[{"role": "user", "content": "Test"}],
            )

            assert result["text"] == "test"
            assert result["input_tokens"] == 150
            assert result["output_tokens"] == 75


# ============================================================
# _parse_json_response ヘルパーテスト
# ============================================================
class TestParseJsonResponse:
    """LLMProvider._parse_json_responseのテスト"""

    def test_parse_plain_json(self):
        """プレーンなJSON文字列のパース"""
        result = LLMProvider._parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_json_with_markdown_fence(self):
        """Markdownコードフェンス付きJSONのパース"""
        raw = '```json\n{"key": "value"}\n```'
        result = LLMProvider._parse_json_response(raw)
        assert result == {"key": "value"}

    def test_parse_json_with_plain_fence(self):
        """言語指定なしのコードフェンス付きJSONのパース"""
        raw = '```\n{"items": [1, 2, 3]}\n```'
        result = LLMProvider._parse_json_response(raw)
        assert result == {"items": [1, 2, 3]}

    def test_parse_json_embedded_in_text(self):
        """テキスト中に埋め込まれたJSONの抽出"""
        raw = 'Here is the result:\n{"score": 0.95}\nThat is all.'
        result = LLMProvider._parse_json_response(raw)
        assert result == {"score": 0.95}

    def test_parse_json_array(self):
        """JSON配列のパース"""
        raw = '[{"a": 1}, {"b": 2}]'
        result = LLMProvider._parse_json_response(raw)
        assert result == [{"a": 1}, {"b": 2}]

    def test_parse_invalid_json_raises(self):
        """不正なJSONでValueErrorが発生する"""
        with pytest.raises(ValueError, match="JSONパース"):
            LLMProvider._parse_json_response("this is not json at all")
