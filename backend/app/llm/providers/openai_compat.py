"""OpenAI互換API プロバイダー

Ollama, vLLM, LM Studio など OpenAI互換APIを持つローカルLLMサーバーを呼び出す。
httpxで {base_url}/v1/chat/completions への POST。
OpenAI形式のリクエスト/レスポンスを使用。
"""

import logging

import httpx

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# OpenAI互換モデルマッピング
# "haiku" -> 高速モデル（軽量タスク用）
# "sonnet" -> 高性能モデル（複雑なタスク用）
MODEL_MAP = {
    "haiku": settings.local_model_fast,
    "sonnet": settings.local_model_smart,
}


class OpenAICompatibleProvider(LLMProvider):
    """OpenAI互換APIプロバイダー（Ollama, vLLM, LM Studio対応）"""

    def __init__(self):
        self.base_url = settings.local_llm_base_url.rstrip("/")
        self.api_key = settings.local_llm_api_key
        self.timeout = httpx.Timeout(
            120.0, connect=10.0
        )  # ローカルモデルは生成に時間がかかる

        logger.info(
            "OpenAI互換プロバイダー初期化: base_url=%s",
            self.base_url,
        )

    @property
    def name(self) -> str:
        return "openai_compat"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスをローカルモデル名に解決"""
        return MODEL_MAP.get(model, model)

    def _build_url(self) -> str:
        """APIエンドポイントURLを構築

        base_urlに /v1 が既に含まれている場合は重複を避ける。
        """
        if self.base_url.endswith("/v1"):
            return f"{self.base_url}/chat/completions"
        return f"{self.base_url}/v1/chat/completions"

    def _build_headers(self) -> dict:
        """リクエストヘッダーを構築"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_body(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """OpenAI形式のリクエストボディを構築

        Anthropic形式のsystemプロンプトをOpenAI形式のsystemメッセージに変換。
        """
        resolved_model = self._resolve_model(model)

        # OpenAI形式: systemはmessagesの先頭に含める
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        openai_messages.extend(messages)

        return {
            "model": resolved_model,
            "messages": openai_messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

    @staticmethod
    def _extract_text_from_openai_response(data: dict) -> str:
        """OpenAI形式のレスポンスからテキストを抽出"""
        choices = data.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")

    @staticmethod
    def _extract_usage_from_openai_response(data: dict) -> dict:
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
        """OpenAI互換APIにメッセージを送信してテキスト応答を取得"""
        body = self._build_body(messages, model, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "OpenAI互換 API エラー: status=%d body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise httpx.HTTPStatusError(
                    f"OpenAI-compatible API returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            data = response.json()
            return self._extract_text_from_openai_response(data)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """OpenAI互換APIにメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """OpenAI互換APIを呼び出し、レスポンスとトークン使用量を返す"""
        body = self._build_body(messages, model, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            text = self._extract_text_from_openai_response(data)
            usage = self._extract_usage_from_openai_response(data)

            return {
                "text": text,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "model": self._resolve_model(model),
            }
