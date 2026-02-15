"""Anthropic Direct API プロバイダー

Anthropic API直接呼び出し。httpxベース。
https://api.anthropic.com/v1/messages への POST。
ヘッダーは x-api-key + anthropic-version。
"""

import logging

import httpx

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# Anthropic直接APIのモデルマッピング
MODEL_MAP = {
    "sonnet": settings.claude_sonnet_model,
    "haiku": settings.claude_haiku_model,
}

# Anthropic API のベースURL
ANTHROPIC_API_BASE = "https://api.anthropic.com"


class AnthropicDirectProvider(LLMProvider):
    """Anthropic API直接呼び出しプロバイダー"""

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.timeout = httpx.Timeout(60.0, connect=10.0)

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY が未設定です")

    @property
    def name(self) -> str:
        return "anthropic"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスを実際のモデルIDに解決"""
        return MODEL_MAP.get(model, model)

    def _build_url(self) -> str:
        """APIエンドポイントURLを構築"""
        return f"{ANTHROPIC_API_BASE}/v1/messages"

    def _build_headers(self) -> dict:
        """リクエストヘッダーを構築"""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _build_body(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """リクエストボディを構築"""
        resolved_model = self._resolve_model(model)
        body = {
            "model": resolved_model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["system"] = system
        return body

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """Anthropic APIにメッセージを送信してテキスト応答を取得"""
        body = self._build_body(messages, model, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "Anthropic API エラー: status=%d body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise httpx.HTTPStatusError(
                    f"Anthropic API returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            data = response.json()
            return self._extract_text_from_anthropic_response(data)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Anthropic APIにメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Anthropic APIを呼び出し、レスポンスとトークン使用量を返す"""
        body = self._build_body(messages, model, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            text = self._extract_text_from_anthropic_response(data)
            usage = self._extract_usage_from_anthropic_response(data)

            return {
                "text": text,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "model": self._resolve_model(model),
            }
