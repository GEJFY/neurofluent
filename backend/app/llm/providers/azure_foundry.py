"""Azure AI Foundry プロバイダー

Azure AI Foundry Marketplace経由でClaudeモデルを呼び出す。
現行の claude_service.py のロジックをそのまま移植。
httpxベース、{endpoint}/anthropic/v1/messages への POST。
"""

import logging

import httpx

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

class AzureFoundryProvider(LLMProvider):
    """Azure AI Foundry上のClaudeモデルとの通信を管理するプロバイダー"""

    def __init__(self):
        self.endpoint = settings.azure_ai_foundry_endpoint.rstrip("/")
        self.api_key = settings.azure_ai_foundry_api_key
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    @property
    def name(self) -> str:
        return "azure_foundry"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスを実際のモデルIDに解決"""
        model_map = {
            "sonnet": settings.claude_sonnet_model,
            "haiku": settings.claude_haiku_model,
        }
        return model_map.get(model, model)

    def _build_url(self) -> str:
        """APIエンドポイントURLを構築"""
        return f"{self.endpoint}/anthropic/v1/messages"

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
        """Claudeにメッセージを送信してテキスト応答を取得"""
        body = self._build_body(messages, model, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "Azure Foundry API エラー: status=%d body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise httpx.HTTPStatusError(
                    f"Azure Foundry API returned {response.status_code}",
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
        """Claudeにメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Claude APIを呼び出し、レスポンスとトークン使用量を返す"""
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
