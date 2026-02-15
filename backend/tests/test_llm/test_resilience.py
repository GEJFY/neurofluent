"""レジリエンス機能のテスト - サーキットブレーカー・リトライ・レートリミッター"""

import time
from unittest.mock import AsyncMock

import pytest

from app.llm.resilience import CircuitBreaker, RateLimiter, RetryPolicy


# ============================================================
# CircuitBreaker テスト
# ============================================================
class TestCircuitBreaker:
    """サーキットブレーカーのテスト"""

    def test_circuit_breaker_closed(self):
        """初期状態はclosedで実行可能"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)

        assert cb.state == "closed"
        assert cb.can_execute() is True
        assert cb.failure_count == 0

    def test_circuit_breaker_opens(self):
        """閾値の連続失敗でopen状態に遷移する"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)

        # 3回失敗を記録
        cb.record_failure()
        assert cb.state == "closed"  # まだ閾値未満

        cb.record_failure()
        assert cb.state == "closed"  # まだ閾値未満

        cb.record_failure()
        assert cb.state == "open"  # 閾値到達 -> open
        assert cb.can_execute() is False

    def test_circuit_breaker_recovery(self):
        """recovery_timeout経過後にhalf_openに遷移して実行可能になる"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        # 閾値まで失敗
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "open"
        assert cb.can_execute() is False

        # recovery_timeout経過を待つ
        time.sleep(0.15)

        # half_openに遷移し実行可能
        assert cb.can_execute() is True
        assert cb.state == "half_open"

        # 成功でclosedに戻る
        cb.record_success()
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_circuit_breaker_half_open_failure(self):
        """half_open状態での失敗でopenに戻る"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        # open状態にする
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "open"

        # recovery_timeout経過
        time.sleep(0.15)
        assert cb.can_execute() is True
        assert cb.state == "half_open"

        # half_openで失敗 -> openに戻る
        cb.record_failure()
        assert cb.state == "open"

    def test_circuit_breaker_success_resets(self):
        """成功記録で失敗カウントがリセットされる"""
        cb = CircuitBreaker(failure_threshold=3)

        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 2

        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == "closed"


# ============================================================
# RetryPolicy テスト
# ============================================================
class TestRetryPolicy:
    """リトライポリシーのテスト"""

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """数回の失敗後に成功する場合、リトライで回復する"""
        call_count = 0

        async def flaky_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("temporary failure")
            return "success"

        policy = RetryPolicy(max_retries=3, base_delay=0.01, max_delay=0.05)
        result = await policy.execute(flaky_func)

        assert result == "success"
        assert call_count == 3  # 2回失敗 + 1回成功

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """全リトライが失敗した場合、最後の例外が再raiseされる"""
        call_count = 0

        async def always_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent failure")

        policy = RetryPolicy(max_retries=2, base_delay=0.01, max_delay=0.05)

        with pytest.raises(ValueError, match="permanent failure"):
            await policy.execute(always_fail)

        # 初回 + 2回リトライ = 3回呼び出し
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_immediate_success(self):
        """初回で成功する場合はリトライなし"""
        mock_func = AsyncMock(return_value="immediate")

        policy = RetryPolicy(max_retries=3, base_delay=0.01)
        result = await policy.execute(mock_func)

        assert result == "immediate"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_passes_arguments(self):
        """引数が正しく渡される"""
        mock_func = AsyncMock(return_value="ok")

        policy = RetryPolicy(max_retries=0)
        await policy.execute(mock_func, "arg1", key="val")

        mock_func.assert_called_once_with("arg1", key="val")


# ============================================================
# RateLimiter テスト
# ============================================================
class TestRateLimiter:
    """レートリミッターのテスト"""

    @pytest.mark.asyncio
    async def test_rate_limiter_allows(self):
        """十分なトークンがある場合、即座にacquireできる"""
        limiter = RateLimiter(requests_per_minute=120)

        # 複数回acquireが成功することを確認
        start = time.monotonic()
        for _ in range(5):
            await limiter.acquire()
        elapsed = time.monotonic() - start

        # 十分なトークンがあるので待機はほぼゼロ
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_rate_limiter_initial_tokens(self):
        """初期化時にmax_tokensが設定される"""
        limiter = RateLimiter(requests_per_minute=60)

        assert limiter.requests_per_minute == 60
        assert limiter.max_tokens == 60.0
        assert limiter.tokens <= 60.0

    @pytest.mark.asyncio
    async def test_rate_limiter_repr(self):
        """__repr__が適切な文字列を返す"""
        limiter = RateLimiter(requests_per_minute=100)
        repr_str = repr(limiter)

        assert "RateLimiter" in repr_str
        assert "rpm=100" in repr_str
