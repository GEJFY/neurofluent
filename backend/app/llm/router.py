"""LLMプロバイダーのルーティングとフォールバック

プライマリプロバイダーでリクエストを実行し、
失敗時にフォールバックプロバイダーに自動切替する。
サーキットブレーカーとリトライポリシーを統合。
"""

import logging
from collections.abc import Callable
from typing import Any

from app.llm.base import LLMProvider
from app.llm.resilience import CircuitBreaker, RateLimiter, RetryPolicy

logger = logging.getLogger(__name__)


class LLMRouter:
    """LLMプロバイダーのルーティングとフォールバック

    プライマリプロバイダーを優先的に使用し、
    サーキットブレーカーが開いた場合やエラー発生時に
    フォールバックプロバイダーに自動切替する。
    """

    def __init__(
        self,
        primary: LLMProvider,
        fallbacks: list[LLMProvider] | None = None,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
    ):
        """
        Args:
            primary: プライマリLLMプロバイダー
            fallbacks: フォールバックプロバイダーリスト（優先順）
            retry_policy: リトライポリシー（Noneの場合はデフォルト設定）
            rate_limiter: レートリミッター（Noneの場合はデフォルト設定）
            circuit_breaker_threshold: サーキットブレーカーの失敗閾値
            circuit_breaker_timeout: サーキットブレーカーの回復タイムアウト（秒）
        """
        self.primary = primary
        self.fallbacks = fallbacks or []
        self.retry_policy = retry_policy or RetryPolicy()
        self.rate_limiter = rate_limiter or RateLimiter()

        # 全プロバイダーにサーキットブレーカーを割り当て
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        all_providers = [primary] + self.fallbacks
        for provider in all_providers:
            self.circuit_breakers[provider.name] = CircuitBreaker(
                failure_threshold=circuit_breaker_threshold,
                recovery_timeout=circuit_breaker_timeout,
            )

        logger.info(
            "LLMRouter初期化: primary=%s, fallbacks=%s",
            primary.name,
            [p.name for p in self.fallbacks],
        )

    def _get_ordered_providers(self) -> list[LLMProvider]:
        """実行可能なプロバイダーを優先順に返す

        サーキットブレーカーが開いているプロバイダーはスキップ。
        """
        all_providers = [self.primary] + self.fallbacks
        available = []

        for provider in all_providers:
            cb = self.circuit_breakers[provider.name]
            if cb.can_execute():
                available.append(provider)
            else:
                logger.debug(
                    "プロバイダースキップ（サーキットブレーカー開）: %s",
                    provider.name,
                )

        if not available:
            # 全プロバイダーがオープン状態 -> プライマリで強制試行
            logger.warning(
                "全プロバイダーのサーキットブレーカーが開いています。"
                "プライマリ(%s)で強制試行します。",
                self.primary.name,
            )
            available = [self.primary]

        return available

    async def _execute_with_fallback(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """フォールバック付きでメソッドを実行

        Args:
            method_name: 実行するメソッド名（"chat", "chat_json", "get_usage_info"）
            *args: メソッドの位置引数
            **kwargs: メソッドのキーワード引数

        Returns:
            メソッドの戻り値

        Raises:
            ValueError: 全プロバイダーが失敗した場合
        """
        providers = self._get_ordered_providers()
        last_exception: Exception | None = None

        for provider in providers:
            cb = self.circuit_breakers[provider.name]

            try:
                # レートリミット適用
                await self.rate_limiter.acquire()

                # リトライポリシー付きで実行
                method: Callable = getattr(provider, method_name)
                result = await self.retry_policy.execute(method, *args, **kwargs)

                # 成功 -> サーキットブレーカーリセット
                cb.record_success()

                if provider != self.primary:
                    logger.info(
                        "フォールバック成功: %s -> %s",
                        self.primary.name,
                        provider.name,
                    )

                return result

            except Exception as e:
                cb.record_failure()
                last_exception = e
                logger.warning(
                    "プロバイダー失敗: %s (%s.%s) - %s",
                    provider.name,
                    method_name,
                    type(e).__name__,
                    str(e)[:200],
                )
                # 次のフォールバックプロバイダーを試行
                continue

        # 全プロバイダーが失敗
        error_msg = (
            f"全LLMプロバイダーが失敗しました "
            f"(primary={self.primary.name}, "
            f"fallbacks={[p.name for p in self.fallbacks]})"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from last_exception

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """プライマリで実行、失敗時にフォールバック"""
        return await self._execute_with_fallback(
            "chat",
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            system=system,
        )

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """プライマリで実行、失敗時にフォールバック（JSON応答）"""
        return await self._execute_with_fallback(
            "chat_json",
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            system=system,
        )

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """プライマリで実行、失敗時にフォールバック（使用量情報付き）"""
        return await self._execute_with_fallback(
            "get_usage_info",
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            system=system,
        )
