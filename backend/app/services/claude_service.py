"""Claude APIサービス - Azure AI Foundry経由のClaude呼び出し"""

import json
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# モデル名のマッピング
MODEL_MAP = {
    "sonnet": settings.claude_sonnet_model,
    "haiku": settings.claude_haiku_model,
}


class ClaudeService:
    """Azure AI Foundry上のClaudeモデルとの通信を管理するサービス"""

    def __init__(self):
        self.endpoint = settings.azure_ai_foundry_endpoint.rstrip("/")
        self.api_key = settings.azure_ai_foundry_api_key
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスを実際のモデルIDに解決"""
        return MODEL_MAP.get(model, model)

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

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """
        Claudeにメッセージを送信してテキスト応答を取得

        Args:
            messages: メッセージリスト（role/content形式）
            model: モデル名（"sonnet", "haiku", またはフルモデルID）
            max_tokens: 最大出力トークン数
            system: システムプロンプト

        Returns:
            Claudeの応答テキスト
        """
        resolved_model = self._resolve_model(model)

        body = {
            "model": resolved_model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "Claude API エラー: status=%d body=%s",
                    response.status_code,
                    response.text,
                )
                raise httpx.HTTPStatusError(
                    f"Claude API returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            data = response.json()
            # Anthropic Messages APIのレスポンス形式からテキストを抽出
            content_blocks = data.get("content", [])
            text_parts = [
                block["text"]
                for block in content_blocks
                if block.get("type") == "text"
            ]
            return "\n".join(text_parts)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """
        Claudeにメッセージを送信してJSON応答を取得・パース

        Args:
            messages: メッセージリスト
            model: モデル名
            max_tokens: 最大出力トークン数
            system: システムプロンプト

        Returns:
            パース済みJSONオブジェクト
        """
        raw = await self.chat(messages, model, max_tokens, system)

        # JSONブロックの抽出（```json ... ``` 形式にも対応）
        text = raw.strip()
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.startswith("```"):
            text = text[len("```"):].strip()
        if text.endswith("```"):
            text = text[:-len("```")].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Claude JSON パースエラー: %s\n生テキスト: %s", e, raw)
            raise ValueError(f"Claude応答のJSONパースに失敗: {e}") from e

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """
        Claude APIを呼び出し、レスポンスとトークン使用量を返す

        Returns:
            {"text": str, "input_tokens": int, "output_tokens": int}
        """
        resolved_model = self._resolve_model(model)

        body = {
            "model": resolved_model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(),
                headers=self._build_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            content_blocks = data.get("content", [])
            text_parts = [
                block["text"]
                for block in content_blocks
                if block.get("type") == "text"
            ]
            usage = data.get("usage", {})

            return {
                "text": "\n".join(text_parts),
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "model": resolved_model,
            }


# シングルトンインスタンス
claude_service = ClaudeService()
