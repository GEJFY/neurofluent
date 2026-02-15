"""Stripe決済サービス - サブスクリプション管理

Stripe APIを使用したサブスクリプション決済の管理。
チェックアウトセッション作成、Webhook処理、サブスクリプション情報取得・キャンセルを行う。
"""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from uuid import UUID

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.subscription import (
    CheckoutSessionResponse,
    PlanFeature,
    PlanInfo,
    PlanLimits,
    SubscriptionInfo,
)

logger = structlog.get_logger()


# --- プラン定義 ---

PLANS: dict = {
    "free": {
        "name": "Free Plan",
        "stripe_price_monthly": None,
        "stripe_price_yearly": None,
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "features": [
            {
                "name": "Basic Conversation",
                "description": "AI英会話 基本機能",
                "included": True,
            },
            {
                "name": "Flash Translation",
                "description": "瞬間英作文（1日5問）",
                "included": True,
            },
            {
                "name": "Spaced Repetition",
                "description": "間隔反復学習",
                "included": True,
            },
            {
                "name": "Basic Analytics",
                "description": "基本的な学習統計",
                "included": True,
            },
            {
                "name": "Advanced Analytics",
                "description": "詳細な学習分析",
                "included": False,
            },
            {
                "name": "AI Curriculum",
                "description": "AIカリキュラム最適化",
                "included": False,
            },
            {
                "name": "Pronunciation Training",
                "description": "発音トレーニング",
                "included": False,
            },
            {
                "name": "Priority Support",
                "description": "優先サポート",
                "included": False,
            },
        ],
        "limits": {
            "daily_sessions": 3,
            "monthly_api_calls": 100,
            "flash_exercises_per_day": 5,
            "conversation_minutes_per_day": 5,
            "pronunciation_evaluations_per_day": 0,
            "advanced_analytics": False,
            "ai_curriculum": False,
            "priority_support": False,
        },
    },
    "standard": {
        "name": "Standard Plan",
        "stripe_price_monthly": "price_standard_monthly",
        "stripe_price_yearly": "price_standard_yearly",
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "features": [
            {
                "name": "Basic Conversation",
                "description": "AI英会話 基本機能",
                "included": True,
            },
            {
                "name": "Flash Translation",
                "description": "瞬間英作文（無制限）",
                "included": True,
            },
            {
                "name": "Spaced Repetition",
                "description": "間隔反復学習",
                "included": True,
            },
            {
                "name": "Basic Analytics",
                "description": "基本的な学習統計",
                "included": True,
            },
            {
                "name": "Advanced Analytics",
                "description": "詳細な学習分析",
                "included": True,
            },
            {
                "name": "Mogomogo English",
                "description": "もごもごイングリッシュ",
                "included": True,
            },
            {
                "name": "AI Curriculum",
                "description": "AIカリキュラム最適化",
                "included": False,
            },
            {
                "name": "Pronunciation Training",
                "description": "発音トレーニング",
                "included": False,
            },
            {
                "name": "Priority Support",
                "description": "優先サポート",
                "included": False,
            },
        ],
        "limits": {
            "daily_sessions": 10,
            "monthly_api_calls": 1000,
            "flash_exercises_per_day": 50,
            "conversation_minutes_per_day": 30,
            "pronunciation_evaluations_per_day": 5,
            "advanced_analytics": True,
            "ai_curriculum": False,
            "priority_support": False,
        },
    },
    "premium": {
        "name": "Premium Plan",
        "stripe_price_monthly": "price_premium_monthly",
        "stripe_price_yearly": "price_premium_yearly",
        "price_monthly": 19.99,
        "price_yearly": 199.99,
        "features": [
            {
                "name": "Basic Conversation",
                "description": "AI英会話 全機能",
                "included": True,
            },
            {
                "name": "Flash Translation",
                "description": "瞬間英作文（無制限）",
                "included": True,
            },
            {
                "name": "Spaced Repetition",
                "description": "間隔反復学習",
                "included": True,
            },
            {
                "name": "Basic Analytics",
                "description": "基本的な学習統計",
                "included": True,
            },
            {
                "name": "Advanced Analytics",
                "description": "詳細な学習分析",
                "included": True,
            },
            {
                "name": "Mogomogo English",
                "description": "もごもごイングリッシュ",
                "included": True,
            },
            {
                "name": "AI Curriculum",
                "description": "AIカリキュラム最適化",
                "included": True,
            },
            {
                "name": "Pronunciation Training",
                "description": "発音トレーニング（無制限）",
                "included": True,
            },
            {
                "name": "Comprehension",
                "description": "リスニングコンプリヘンション",
                "included": True,
            },
            {
                "name": "Priority Support",
                "description": "優先サポート",
                "included": True,
            },
        ],
        "limits": {
            "daily_sessions": -1,
            "monthly_api_calls": 10000,
            "flash_exercises_per_day": -1,
            "conversation_minutes_per_day": -1,
            "pronunciation_evaluations_per_day": -1,
            "advanced_analytics": True,
            "ai_curriculum": True,
            "priority_support": True,
        },
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "stripe_price_monthly": "price_enterprise_monthly",
        "stripe_price_yearly": "price_enterprise_yearly",
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "features": [
            {
                "name": "All Features",
                "description": "全機能（カスタム設定）",
                "included": True,
            },
            {
                "name": "Team Management",
                "description": "チーム管理機能",
                "included": True,
            },
            {
                "name": "Custom Reports",
                "description": "カスタムレポート",
                "included": True,
            },
            {"name": "API Access", "description": "API連携", "included": True},
            {
                "name": "Dedicated Support",
                "description": "専任サポート",
                "included": True,
            },
            {"name": "SLA", "description": "SLA保証", "included": True},
        ],
        "limits": {
            "daily_sessions": -1,
            "monthly_api_calls": -1,
            "flash_exercises_per_day": -1,
            "conversation_minutes_per_day": -1,
            "pronunciation_evaluations_per_day": -1,
            "advanced_analytics": True,
            "ai_curriculum": True,
            "priority_support": True,
        },
    },
}


class StripeService:
    """Stripe決済サービス - httpxベースの実装（Idempotency・Retry対応）"""

    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 0.5

    def __init__(self):
        self.api_base = "https://api.stripe.com/v1"
        self.api_key = getattr(settings, "stripe_secret_key", "")
        self.webhook_secret = getattr(settings, "stripe_webhook_secret", "")
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _build_headers(self, idempotency_key: str | None = None) -> dict:
        """Stripe API用ヘッダーを構築"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        idempotency_key: str | None = None,
        **kwargs,
    ) -> httpx.Response:
        """指数バックオフによるリトライ付きHTTPリクエスト"""
        headers = self._build_headers(idempotency_key)
        last_exception = None

        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method, url, headers=headers, **kwargs
                    )
                    # 429 or 5xx はリトライ対象
                    if response.status_code in (429, 500, 502, 503, 504):
                        if attempt < self.MAX_RETRIES - 1:
                            delay = self.RETRY_BASE_DELAY * (2**attempt)
                            logger.warning(
                                "stripe_retry",
                                attempt=attempt + 1,
                                status=response.status_code,
                                delay=delay,
                            )
                            await asyncio.sleep(delay)
                            continue
                    return response
            except httpx.HTTPError as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "stripe_retry_error",
                        attempt=attempt + 1,
                        error=str(e),
                        delay=delay,
                    )
                    await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
        return response  # type: ignore[possibly-undefined]

    @staticmethod
    def _generate_idempotency_key(user_id: UUID, plan: str, billing_cycle: str) -> str:
        """Checkout用のIdempotency Keyを生成（1時間単位で重複防止）"""
        hour_bucket = int(time.time() // 3600)
        raw = f"{user_id}:{plan}:{billing_cycle}:{hour_bucket}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    async def _is_webhook_duplicate(self, event_id: str) -> bool:
        """Redis でWebhookイベントの重複チェック（TTL 24h）"""
        try:
            from app.redis_client import get_redis

            redis_client = get_redis()
            if redis_client is None:
                return False
            key = f"stripe:webhook:{event_id}"
            result = await redis_client.set(key, "1", ex=86400, nx=True)
            return result is None  # None = 既に存在 = 重複
        except Exception:
            return False

    async def create_checkout_session(
        self,
        user_id: UUID,
        plan: str,
        success_url: str,
        cancel_url: str,
        billing_cycle: str = "monthly",
    ) -> CheckoutSessionResponse:
        """
        Stripeチェックアウトセッションを作成

        Args:
            user_id: ユーザーID
            plan: プランID (standard, premium, enterprise)
            success_url: 成功時リダイレクトURL
            cancel_url: キャンセル時リダイレクトURL
            billing_cycle: 課金サイクル (monthly, yearly)

        Returns:
            CheckoutSessionResponse: チェックアウトURL・セッションID
        """
        if plan not in PLANS or plan == "free":
            raise ValueError(f"無効なプランです: {plan}")

        plan_data = PLANS[plan]
        if billing_cycle == "yearly":
            price_id = plan_data.get("stripe_price_yearly", "")
        else:
            price_id = plan_data.get("stripe_price_monthly", "")

        if not price_id:
            raise ValueError(f"プラン {plan} の価格IDが設定されていません")

        form_data = {
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "client_reference_id": str(user_id),
            "metadata[user_id]": str(user_id),
            "metadata[plan]": plan,
        }

        idempotency_key = self._generate_idempotency_key(user_id, plan, billing_cycle)

        response = await self._request_with_retry(
            "POST",
            f"{self.api_base}/checkout/sessions",
            idempotency_key=idempotency_key,
            data=form_data,
        )

        if response.status_code != 200:
            logger.error("stripe_checkout_error", status=response.status_code)
            raise httpx.HTTPStatusError(
                f"Stripe API returned {response.status_code}",
                request=response.request,
                response=response,
            )

        session_data = response.json()

        return CheckoutSessionResponse(
            checkout_url=session_data.get("url", ""),
            session_id=session_data.get("id", ""),
        )

    async def handle_webhook(
        self,
        payload: bytes,
        signature: str,
        db: AsyncSession,
    ) -> dict:
        """
        Stripe Webhookイベントを処理

        対応イベント:
        - checkout.session.completed: 初回決済完了
        - customer.subscription.updated: サブスクリプション更新
        - customer.subscription.deleted: サブスクリプション削除

        Args:
            payload: Webhookリクエストボディ
            signature: Stripe-Signature ヘッダー
            db: データベースセッション

        Returns:
            処理結果のdict
        """
        # 署名検証
        if self.webhook_secret:
            self._verify_webhook_signature(payload, signature)

        event = json.loads(payload)
        event_id = event.get("id", "")
        event_type = event.get("type", "")
        event_data = event.get("data", {}).get("object", {})

        # Webhook重複排除
        if event_id and await self._is_webhook_duplicate(event_id):
            logger.info(
                "stripe_webhook_duplicate", event_id=event_id, event_type=event_type
            )
            return {"event_type": event_type, "status": "duplicate"}

        logger.info("stripe_webhook_received", event_id=event_id, event_type=event_type)

        if event_type == "checkout.session.completed":
            await self._handle_checkout_completed(event_data, db)
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(event_data, db)
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(event_data, db)
        else:
            logger.info("未対応のWebhookイベント: %s", event_type)

        return {"event_type": event_type, "status": "processed"}

    async def get_subscription(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> SubscriptionInfo:
        """
        ユーザーのサブスクリプション情報を取得

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            SubscriptionInfo: サブスクリプション情報
        """
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        sub = result.scalar_one_or_none()

        if sub is None:
            return SubscriptionInfo(
                plan="free",
                status="active",
                current_period_start=None,
                current_period_end=None,
                cancel_at_period_end=False,
                stripe_customer_id=None,
            )

        return SubscriptionInfo(
            plan=sub.plan,
            status=sub.status,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            stripe_customer_id=sub.stripe_customer_id,
        )

    async def cancel_subscription(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> bool:
        """
        サブスクリプションをキャンセル（期間終了時に解約）

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            成功かどうか
        """
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == "active",
            )
        )
        sub = result.scalar_one_or_none()

        if sub is None:
            return False

        # Stripe APIでサブスクリプションをキャンセル
        if sub.stripe_subscription_id and self.api_key:
            try:
                response = await self._request_with_retry(
                    "POST",
                    f"{self.api_base}/subscriptions/{sub.stripe_subscription_id}",
                    data={"cancel_at_period_end": "true"},
                )
                if response.status_code != 200:
                    logger.error("stripe_cancel_error", status=response.status_code)
                    return False
            except httpx.HTTPError as e:
                logger.error("stripe_cancel_network_error", error=str(e))
                return False

        # ローカルDB更新
        sub.cancel_at_period_end = True
        await db.commit()

        return True

    def get_plans(self, current_plan: str = "free") -> list[PlanInfo]:
        """
        利用可能なプラン一覧を取得

        Args:
            current_plan: ユーザーの現在のプランID

        Returns:
            PlanInfoのリスト
        """
        plan_list = []
        for plan_id, data in PLANS.items():
            features = [
                PlanFeature(
                    name=f["name"],
                    description=f["description"],
                    included=f["included"],
                )
                for f in data["features"]
            ]

            limits_data = data["limits"]
            limits = PlanLimits(
                daily_sessions=limits_data["daily_sessions"],
                monthly_api_calls=limits_data["monthly_api_calls"],
                flash_exercises_per_day=limits_data["flash_exercises_per_day"],
                conversation_minutes_per_day=limits_data[
                    "conversation_minutes_per_day"
                ],
                pronunciation_evaluations_per_day=limits_data[
                    "pronunciation_evaluations_per_day"
                ],
                advanced_analytics=limits_data["advanced_analytics"],
                ai_curriculum=limits_data["ai_curriculum"],
                priority_support=limits_data["priority_support"],
            )

            plan_list.append(
                PlanInfo(
                    id=plan_id,
                    name=data["name"],
                    price_monthly=data["price_monthly"],
                    price_yearly=data["price_yearly"],
                    features=features,
                    limits=limits,
                    is_current=(plan_id == current_plan),
                )
            )

        return plan_list

    # --- プライベートヘルパーメソッド ---

    def _verify_webhook_signature(self, payload: bytes, signature: str) -> None:
        """Stripe Webhook署名を検証"""
        if not signature or not self.webhook_secret:
            raise ValueError("Webhook署名またはシークレットが不足しています")

        # Stripe署名フォーマット: t=timestamp,v1=signature
        sig_parts = {}
        for part in signature.split(","):
            key, _, value = part.partition("=")
            sig_parts[key.strip()] = value.strip()

        timestamp = sig_parts.get("t", "")
        sig_v1 = sig_parts.get("v1", "")

        if not timestamp or not sig_v1:
            raise ValueError("無効なWebhook署名フォーマットです")

        # タイムスタンプの鮮度チェック（5分以内）
        try:
            ts = int(timestamp)
        except (ValueError, TypeError):
            raise ValueError("無効なWebhookタイムスタンプです")

        if abs(time.time() - ts) > 300:
            raise ValueError("Webhook署名のタイムスタンプが古すぎます")

        # HMAC-SHA256署名検証
        signed_payload = f"{timestamp}.".encode() + payload
        expected_sig = hmac.new(
            self.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, sig_v1):
            raise ValueError("Webhook署名の検証に失敗しました")

    async def _handle_checkout_completed(self, data: dict, db: AsyncSession) -> None:
        """チェックアウト完了イベント処理"""
        user_id_str = data.get("metadata", {}).get("user_id") or data.get(
            "client_reference_id"
        )
        if not user_id_str:
            logger.warning("チェックアウト完了: user_idが見つかりません")
            return

        plan = data.get("metadata", {}).get("plan", "standard")
        customer_id = data.get("customer", "")
        subscription_id = data.get("subscription", "")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            logger.error("無効なuser_id: %s", user_id_str)
            return

        # 既存のサブスクリプションを検索
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        sub = result.scalar_one_or_none()

        now = datetime.now(UTC)

        if sub is None:
            sub = Subscription(
                user_id=user_id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                plan=plan,
                status="active",
                current_period_start=now,
                current_period_end=None,
                cancel_at_period_end=False,
            )
            db.add(sub)
        else:
            sub.stripe_customer_id = customer_id
            sub.stripe_subscription_id = subscription_id
            sub.plan = plan
            sub.status = "active"
            sub.current_period_start = now
            sub.cancel_at_period_end = False

        # ユーザーのサブスクリプションプランも更新
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.subscription_plan = plan

        await db.commit()
        logger.info("チェックアウト完了: user=%s plan=%s", user_id, plan)

    async def _handle_subscription_updated(self, data: dict, db: AsyncSession) -> None:
        """サブスクリプション更新イベント処理"""
        subscription_id = data.get("id", "")
        status = data.get("status", "")
        cancel_at_period_end = data.get("cancel_at_period_end", False)

        # 期間情報
        period_start = data.get("current_period_start")
        period_end = data.get("current_period_end")

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        sub = result.scalar_one_or_none()

        if sub is None:
            logger.warning(
                "サブスクリプション更新: 該当レコードなし subscription_id=%s",
                subscription_id,
            )
            return

        sub.status = status
        sub.cancel_at_period_end = cancel_at_period_end

        if period_start:
            sub.current_period_start = datetime.fromtimestamp(period_start, tz=UTC)
        if period_end:
            sub.current_period_end = datetime.fromtimestamp(period_end, tz=UTC)

        await db.commit()
        logger.info("サブスクリプション更新: user=%s status=%s", sub.user_id, status)

    async def _handle_subscription_deleted(self, data: dict, db: AsyncSession) -> None:
        """サブスクリプション削除イベント処理"""
        subscription_id = data.get("id", "")

        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        )
        sub = result.scalar_one_or_none()

        if sub is None:
            logger.warning(
                "サブスクリプション削除: 該当レコードなし subscription_id=%s",
                subscription_id,
            )
            return

        sub.status = "canceled"
        sub.cancel_at_period_end = False

        # ユーザーのプランをfreeに戻す
        user_result = await db.execute(select(User).where(User.id == sub.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            user.subscription_plan = "free"

        await db.commit()
        logger.info("サブスクリプション削除: user=%s", sub.user_id)


# シングルトンインスタンス
stripe_service = StripeService()
