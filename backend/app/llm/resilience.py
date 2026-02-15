"""LLMプロバイダーのレジリエンス機能

サーキットブレーカー、リトライポリシー、レートリミッターを提供する。
全てインメモリ実装（Redis不要）。
"""

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreaker:
    """サーキットブレーカー - 連続失敗時にプロバイダーを一時停止

    状態遷移:
        closed -> open: 連続失敗がthresholdに到達
        open -> half_open: recovery_timeout経過後
        half_open -> closed: 次のリクエストが成功
        half_open -> open: 次のリクエストが失敗
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        """
        Args:
            failure_threshold: オープン状態に遷移する連続失敗回数
            recovery_timeout: オープン状態からハーフオープンに遷移するまでの秒数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "closed"  # closed, open, half_open

    def record_success(self) -> None:
        """成功を記録 - 失敗カウントをリセットしclosed状態に"""
        self.failure_count = 0
        self.state = "closed"
        logger.debug("CircuitBreaker: 成功記録、状態=closed")

    def record_failure(self) -> None:
        """失敗を記録 - thresholdに達したらopen状態に遷移"""
        self.failure_count += 1
        self.last_failure_time = time.monotonic()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                "CircuitBreaker: オープン状態に遷移 (連続失敗=%d)",
                self.failure_count,
            )
        else:
            logger.debug(
                "CircuitBreaker: 失敗記録 (%d/%d)",
                self.failure_count,
                self.failure_threshold,
            )

    def can_execute(self) -> bool:
        """現在リクエストを実行可能かチェック

        Returns:
            True: closed状態、またはhalf_open遷移条件を満たす場合
            False: open状態でrecovery_timeout未経過の場合
        """
        if self.state == "closed":
            return True

        if self.state == "open":
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = "half_open"
                logger.info("CircuitBreaker: ハーフオープン状態に遷移")
                return True
            return False

        # half_open: 試行許可（結果でclosed/openに遷移）
        return True

    def __repr__(self) -> str:
        return (
            f"CircuitBreaker(state={self.state}, "
            f"failures={self.failure_count}/{self.failure_threshold})"
        )


class RetryPolicy:
    """リトライポリシー - exponential backoff with jitter

    失敗時に指数関数的に増加する待機時間でリトライする。
    ジッターを加えて thundering herd 問題を回避。
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        """
        Args:
            max_retries: 最大リトライ回数
            base_delay: 初回リトライの基本待機時間（秒）
            max_delay: 最大待機時間（秒）
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """リトライポリシーを適用して関数を実行

        Args:
            func: 実行する非同期関数
            *args: 関数の位置引数
            **kwargs: 関数のキーワード引数

        Returns:
            関数の戻り値

        Raises:
            Exception: 全リトライ失敗後の最後の例外
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff with jitter
                    delay = min(
                        self.base_delay * (2**attempt),
                        self.max_delay,
                    )
                    # 簡易ジッター: 待機時間の50-100%をランダムに
                    import random

                    jittered_delay = delay * (0.5 + random.random() * 0.5)
                    logger.warning(
                        "リトライ %d/%d: %.1f秒後に再試行 (エラー: %s)",
                        attempt + 1,
                        self.max_retries,
                        jittered_delay,
                        str(e)[:200],
                    )
                    await asyncio.sleep(jittered_delay)
                else:
                    logger.error(
                        "全リトライ失敗 (%d回): %s",
                        self.max_retries + 1,
                        str(e)[:200],
                    )

        raise last_exception  # type: ignore[misc]


class RateLimiter:
    """レートリミッター - Token bucket方式

    1分あたりのリクエスト数を制限する。
    バケットが空の場合は次のトークン補充まで待機。
    """

    def __init__(self, requests_per_minute: int = 60):
        """
        Args:
            requests_per_minute: 1分あたりの最大リクエスト数
        """
        self.requests_per_minute = requests_per_minute
        self.tokens = float(requests_per_minute)
        self.max_tokens = float(requests_per_minute)
        self.refill_rate = requests_per_minute / 60.0  # トークン/秒
        self.last_refill_time = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """トークンを1つ取得（トークンがない場合は待機）"""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill_time
            self.tokens = min(
                self.max_tokens,
                self.tokens + elapsed * self.refill_rate,
            )
            self.last_refill_time = now

            if self.tokens < 1.0:
                # トークン不足: 次のトークン補充まで待機
                wait_time = (1.0 - self.tokens) / self.refill_rate
                logger.debug("レートリミット: %.2f秒待機", wait_time)
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
                self.last_refill_time = time.monotonic()
            else:
                self.tokens -= 1.0

    def __repr__(self) -> str:
        return f"RateLimiter(rpm={self.requests_per_minute}, tokens={self.tokens:.1f})"
