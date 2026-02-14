"""AWS Bedrock プロバイダー

AWS Bedrock via boto3。bedrock-runtime クライアントの invoke_model() を使用。
モデルIDは anthropic.claude-3-5-sonnet-20241022-v2:0 形式。
Bedrockのレスポンス形式をAnthropic形式に変換。
boto3はオプショナルインポート（ImportError時にわかりやすいエラー）。
"""

import json
import logging
from typing import Any

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# オプショナルインポート: boto3
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    boto3 = None  # type: ignore[assignment]

# Bedrockモデルマッピング
MODEL_MAP = {
    "sonnet": settings.aws_bedrock_model_sonnet,
    "haiku": settings.aws_bedrock_model_haiku,
}


class AWSBedrockProvider(LLMProvider):
    """AWS Bedrock経由でClaudeモデルを呼び出すプロバイダー"""

    def __init__(self):
        if not HAS_BOTO3:
            raise ImportError(
                "AWS Bedrockプロバイダーには boto3 が必要です。"
                "インストール: pip install boto3"
            )

        # boto3クライアントの設定
        session_kwargs: dict[str, Any] = {
            "region_name": settings.aws_region,
        }
        if settings.aws_access_key_id:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
        if settings.aws_secret_access_key:
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        session = boto3.Session(**session_kwargs)
        self.client = session.client("bedrock-runtime")
        logger.info(
            "AWS Bedrock プロバイダー初期化: region=%s",
            settings.aws_region,
        )

    @property
    def name(self) -> str:
        return "bedrock"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスをBedrock用モデルIDに解決"""
        return MODEL_MAP.get(model, model)

    def _build_bedrock_body(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """Bedrock用リクエストボディを構築

        Bedrockの Anthropic Claude はAnthropic Messages APIと同じ形式を受け付ける。
        """
        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["system"] = system
        return body

    def _invoke_model(
        self,
        messages: list[dict],
        model: str,
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """Bedrock invoke_model を同期呼び出し

        注意: boto3は非同期対応していないため、同期呼び出しを使用。
        """
        resolved_model = self._resolve_model(model)
        body = self._build_bedrock_body(messages, model, max_tokens, system)

        response = self.client.invoke_model(
            modelId=resolved_model,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )

        response_body = json.loads(response["body"].read())
        return response_body

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """Bedrockにメッセージを送信してテキスト応答を取得

        boto3は同期のため、asyncio.to_thread で非同期化。
        """
        import asyncio

        data = await asyncio.to_thread(
            self._invoke_model, messages, model, max_tokens, system
        )
        return self._extract_text_from_anthropic_response(data)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Bedrockにメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Bedrockを呼び出し、レスポンスとトークン使用量を返す"""
        import asyncio

        data = await asyncio.to_thread(
            self._invoke_model, messages, model, max_tokens, system
        )

        text = self._extract_text_from_anthropic_response(data)
        usage = self._extract_usage_from_anthropic_response(data)

        return {
            "text": text,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "model": self._resolve_model(model),
        }
