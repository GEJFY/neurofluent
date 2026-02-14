"""LLMプロバイダーの抽象基底クラス"""

import json
import logging
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """LLMプロバイダーの抽象基底クラス

    全てのLLMプロバイダー（Azure Foundry, Anthropic Direct, Bedrock, Vertex, OpenAI互換）は
    このクラスを継承し、共通インターフェースを実装する。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """プロバイダー名（例: "azure_foundry", "anthropic", "bedrock"）"""
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """メッセージを送信してテキスト応答を取得

        Args:
            messages: メッセージリスト（role/content形式）
            model: モデルエイリアス（"sonnet", "haiku"）またはフルモデルID
            max_tokens: 最大出力トークン数
            system: システムプロンプト

        Returns:
            LLMの応答テキスト
        """
        ...

    @abstractmethod
    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """メッセージを送信してJSON応答を取得・パース

        Args:
            messages: メッセージリスト
            model: モデルエイリアスまたはフルモデルID
            max_tokens: 最大出力トークン数
            system: システムプロンプト

        Returns:
            パース済みJSONオブジェクト
        """
        ...

    @abstractmethod
    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """メッセージを送信してレスポンスとトークン使用量を返す

        Returns:
            {"text": str, "input_tokens": int, "output_tokens": int, "model": str}
        """
        ...

    async def health_check(self) -> bool:
        """プロバイダーの健全性チェック

        軽量なリクエストを送信して接続可能かどうかを確認する。
        """
        try:
            await self.chat(
                [{"role": "user", "content": "ping"}],
                max_tokens=10,
            )
            return True
        except Exception:
            logger.warning("ヘルスチェック失敗: provider=%s", self.name)
            return False

    @staticmethod
    def _parse_json_response(raw: str) -> dict:
        """LLMの生テキストからJSONをパース

        Markdownコードフェンス（```json ... ```）を除去してからパースする。
        全プロバイダー共通のヘルパーメソッド。

        Args:
            raw: LLMからの生テキスト応答

        Returns:
            パース済みJSONオブジェクト

        Raises:
            ValueError: JSONパースに失敗した場合
        """
        text = raw.strip()

        # Markdownコードフェンスの除去
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.startswith("```"):
            text = text[len("```"):].strip()
        if text.endswith("```"):
            text = text[:-len("```")].strip()

        # JSONブロックの抽出（テキスト中に埋め込まれている場合）
        if not text.startswith(("{", "[")):
            json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
            if json_match:
                text = json_match.group(1)

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("JSONパースエラー: %s\n生テキスト: %s", e, raw[:500])
            raise ValueError(f"LLM応答のJSONパースに失敗: {e}") from e

    @staticmethod
    def _extract_text_from_anthropic_response(data: dict) -> str:
        """Anthropic Messages APIのレスポンスからテキストを抽出

        Args:
            data: APIレスポンスのJSONデータ

        Returns:
            結合されたテキスト応答
        """
        content_blocks = data.get("content", [])
        text_parts = [
            block["text"]
            for block in content_blocks
            if block.get("type") == "text"
        ]
        return "\n".join(text_parts)

    @staticmethod
    def _extract_usage_from_anthropic_response(data: dict) -> dict:
        """Anthropic Messages APIのレスポンスからトークン使用量を抽出

        Args:
            data: APIレスポンスのJSONデータ

        Returns:
            {"input_tokens": int, "output_tokens": int}
        """
        usage = data.get("usage", {})
        return {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }
