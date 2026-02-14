"""LLMサービス - claude_service のドロップインリプレース

設定に基づいてプロバイダーを自動構築し、
既存の claude_service と同じインターフェースを提供する。
"""

import logging

from app.config import settings
from app.llm.base import LLMProvider
from app.llm.providers import PROVIDER_MAP
from app.llm.resilience import RateLimiter, RetryPolicy
from app.llm.router import LLMRouter

logger = logging.getLogger(__name__)


class LLMService:
    """LLMサービス - マルチクラウドLLM抽象化レイヤーのエントリーポイント

    claude_service のドロップインリプレースとして機能する。
    シングルトンパターンで全アプリケーションから共有。
    """

    _instance: "LLMService | None" = None

    def __init__(self):
        self.router = self._build_router()
        logger.info("LLMService初期化完了")

    def _build_router(self) -> LLMRouter:
        """設定からプロバイダーとルーターを構築

        settings.llm_provider でプライマリを決定。
        settings.llm_fallback_providers でフォールバックを構築。
        """
        # プライマリプロバイダーの構築
        primary = self._create_provider(settings.llm_provider)
        logger.info("プライマリプロバイダー: %s", primary.name)

        # フォールバックプロバイダーの構築
        fallbacks: list[LLMProvider] = []
        if settings.llm_fallback_providers:
            fallback_names = [
                name.strip()
                for name in settings.llm_fallback_providers.split(",")
                if name.strip()
            ]
            for name in fallback_names:
                try:
                    fallback = self._create_provider(name)
                    fallbacks.append(fallback)
                    logger.info("フォールバックプロバイダー追加: %s", fallback.name)
                except Exception as e:
                    logger.warning(
                        "フォールバックプロバイダー '%s' の初期化失敗: %s",
                        name,
                        str(e),
                    )

        # レジリエンス設定
        retry_policy = RetryPolicy(
            max_retries=settings.llm_retry_max,
        )
        rate_limiter = RateLimiter(
            requests_per_minute=settings.llm_rate_limit_rpm,
        )

        return LLMRouter(
            primary=primary,
            fallbacks=fallbacks,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            circuit_breaker_threshold=settings.llm_circuit_breaker_threshold,
            circuit_breaker_timeout=settings.llm_circuit_breaker_timeout,
        )

    @staticmethod
    def _create_provider(provider_name: str) -> LLMProvider:
        """プロバイダー名からプロバイダーインスタンスを生成

        Args:
            provider_name: プロバイダー名（PROVIDER_MAPのキー）

        Returns:
            LLMProviderインスタンス

        Raises:
            ValueError: 不明なプロバイダー名の場合
        """
        provider_class = PROVIDER_MAP.get(provider_name)
        if provider_class is None:
            available = ", ".join(PROVIDER_MAP.keys())
            raise ValueError(
                f"不明なLLMプロバイダー: '{provider_name}'. "
                f"利用可能: {available}"
            )

        try:
            return provider_class()
        except ImportError as e:
            raise ValueError(
                f"プロバイダー '{provider_name}' の依存関係が不足しています: {e}"
            ) from e

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """メッセージを送信してテキスト応答を取得"""
        return await self.router.chat(messages, model, max_tokens, system)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """メッセージを送信してJSON応答を取得・パース"""
        return await self.router.chat_json(messages, model, max_tokens, system)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """メッセージを送信してレスポンスとトークン使用量を返す"""
        return await self.router.get_usage_info(messages, model, max_tokens, system)


def get_llm_service() -> LLMService:
    """LLMServiceのシングルトンインスタンスを取得

    初回呼び出し時にインスタンスを生成し、以降は同じインスタンスを返す。
    """
    if LLMService._instance is None:
        LLMService._instance = LLMService()
    return LLMService._instance


# シングルトンインスタンス（claude_serviceとの後方互換用）
llm_service = get_llm_service()
