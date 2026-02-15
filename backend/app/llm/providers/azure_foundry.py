"""Azure AI Foundry プロバイダー (GPT-5 via Azure OpenAI)

Azure OpenAI の GPT-5 シリーズモデルを呼び出す。
httpxベース、{endpoint}/openai/deployments/{model}/chat/completions への POST。
"""

import logging

import httpx

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# モデルエイリアス → Azure OpenAI デプロイ名マッピング
MODEL_MAP = {
    "haiku": settings.gpt5_fast_model,  # gpt-5-nano（高速・低コスト）
    "sonnet": settings.gpt5_smart_model,  # gpt-5-mini（バランス型）
    "opus": settings.gpt5_powerful_model,  # gpt-5（最高性能）
}


class AzureFoundryProvider(LLMProvider):
    """Azure OpenAI GPT-5 プロバイダー"""

    def __init__(self):
        self.endpoint = settings.azure_ai_foundry_endpoint.rstrip("/")
        self.api_key = settings.azure_ai_foundry_api_key
        self.api_version = settings.azure_openai_api_version
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    @property
    def name(self) -> str:
        return "azure_foundry"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスを Azure OpenAI デプロイ名に解決"""
        return MODEL_MAP.get(model, model)

    def _build_url(self, deployment: str) -> str:
        """APIエンドポイントURLを構築"""
        return (
            f"{self.endpoint}/openai/deployments/{deployment}"
            f"/chat/completions?api-version={self.api_version}"
        )

    def _build_headers(self) -> dict:
        """リクエストヘッダーを構築"""
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def _build_body(
        self,
        messages: list[dict],
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """OpenAI形式のリクエストボディを構築"""
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        openai_messages.extend(messages)

        return {
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

    @staticmethod
    def _extract_text(data: dict) -> str:
        """OpenAI形式のレスポンスからテキストを抽出"""
        choices = data.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")

    @staticmethod
    def _extract_usage(data: dict) -> dict:
        """OpenAI形式のレスポンスからトークン使用量を抽出"""
        usage = data.get("usage", {})
        return {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """GPT-5にメッセージを送信してテキスト応答を取得"""
        deployment = self._resolve_model(model)
        body = self._build_body(messages, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(deployment),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "Azure OpenAI API エラー: status=%d body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise httpx.HTTPStatusError(
                    f"Azure OpenAI API returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            data = response.json()
            return self._extract_text(data)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """GPT-5にメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """GPT-5 APIを呼び出し、レスポンスとトークン使用量を返す"""
        deployment = self._resolve_model(model)
        body = self._build_body(messages, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(deployment),
                headers=self._build_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            text = self._extract_text(data)
            usage = self._extract_usage(data)

            return {
                "text": text,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "model": deployment,
            }
