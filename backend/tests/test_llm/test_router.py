"""LLMルーターのテスト - フォールバック・プライマリ成功・全失敗"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm.resilience import RateLimiter, RetryPolicy
from app.llm.router import LLMRouter


# ============================================================
# ヘルパー: モックプロバイダー
# ============================================================
def _make_provider(name: str, chat_return: str = "ok", should_fail: bool = False):
    """テスト用のモックLLMプロバイダーを生成"""
    provider = MagicMock()
    provider.name = name

    if should_fail:
        provider.chat = AsyncMock(side_effect=Exception(f"{name} failed"))
        provider.chat_json = AsyncMock(side_effect=Exception(f"{name} failed"))
        provider.get_usage_info = AsyncMock(side_effect=Exception(f"{name} failed"))
    else:
        provider.chat = AsyncMock(return_value=chat_return)
        provider.chat_json = AsyncMock(return_value={"result": chat_return})
        provider.get_usage_info = AsyncMock(
            return_value={
                "text": chat_return,
                "input_tokens": 10,
                "output_tokens": 5,
                "model": name,
            }
        )

    return provider


class TestLLMRouter:
    """LLMRouterのテスト"""

    @pytest.mark.asyncio
    async def test_primary_success(self):
        """プライマリプロバイダーが成功する場合はそのまま結果を返す"""
        primary = _make_provider("primary", chat_return="primary response")
        fallback = _make_provider("fallback", chat_return="fallback response")

        # リトライなし・レートリミットなしで高速テスト
        router = LLMRouter(
            primary=primary,
            fallbacks=[fallback],
            retry_policy=RetryPolicy(max_retries=0),
            rate_limiter=RateLimiter(requests_per_minute=1000),
        )

        result = await router.chat(
            messages=[{"role": "user", "content": "test"}],
        )

        assert result == "primary response"
        primary.chat.assert_called_once()
        fallback.chat.assert_not_called()

    @pytest.mark.asyncio
    async def test_primary_failure_fallback(self):
        """プライマリが失敗した場合、フォールバックに切り替わる"""
        primary = _make_provider("primary", should_fail=True)
        fallback = _make_provider("fallback", chat_return="fallback response")

        router = LLMRouter(
            primary=primary,
            fallbacks=[fallback],
            retry_policy=RetryPolicy(max_retries=0),
            rate_limiter=RateLimiter(requests_per_minute=1000),
        )

        result = await router.chat(
            messages=[{"role": "user", "content": "test"}],
        )

        assert result == "fallback response"
        primary.chat.assert_called_once()
        fallback.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_providers_failure(self):
        """全プロバイダーが失敗した場合、ValueErrorが発生する"""
        primary = _make_provider("primary", should_fail=True)
        fallback = _make_provider("fallback", should_fail=True)

        router = LLMRouter(
            primary=primary,
            fallbacks=[fallback],
            retry_policy=RetryPolicy(max_retries=0),
            rate_limiter=RateLimiter(requests_per_minute=1000),
        )

        with pytest.raises(ValueError, match="全LLMプロバイダーが失敗"):
            await router.chat(
                messages=[{"role": "user", "content": "test"}],
            )

    @pytest.mark.asyncio
    async def test_chat_json_primary_success(self):
        """chat_jsonがプライマリで成功する"""
        primary = _make_provider("primary")

        router = LLMRouter(
            primary=primary,
            retry_policy=RetryPolicy(max_retries=0),
            rate_limiter=RateLimiter(requests_per_minute=1000),
        )

        result = await router.chat_json(
            messages=[{"role": "user", "content": "test"}],
        )

        assert result == {"result": "ok"}

    @pytest.mark.asyncio
    async def test_get_usage_info_fallback(self):
        """get_usage_infoでプライマリ失敗時にフォールバックが使われる"""
        primary = _make_provider("primary", should_fail=True)
        fallback = _make_provider("fallback")

        router = LLMRouter(
            primary=primary,
            fallbacks=[fallback],
            retry_policy=RetryPolicy(max_retries=0),
            rate_limiter=RateLimiter(requests_per_minute=1000),
        )

        result = await router.get_usage_info(
            messages=[{"role": "user", "content": "test"}],
        )

        assert result["text"] == "ok"
        assert result["model"] == "fallback"
