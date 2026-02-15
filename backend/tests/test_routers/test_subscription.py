"""サブスクリプションルーターのテスト - プラン・決済管理"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSubscriptionRouter:
    """Subscriptionルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_plans(self, auth_client):
        """プラン一覧の取得"""
        with patch("app.routers.subscription.stripe_service") as mock_stripe:
            mock_stripe.get_plans = MagicMock(return_value=[])

            response = await auth_client.get("/api/subscription/plans")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            mock_stripe.get_plans.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_subscription(self, auth_client):
        """現在のサブスクリプション情報の取得"""
        with patch("app.routers.subscription.stripe_service") as mock_stripe:
            mock_stripe.get_subscription = AsyncMock(
                return_value=MagicMock(
                    plan="free",
                    status="active",
                    current_period_start=None,
                    current_period_end=None,
                    cancel_at_period_end=False,
                    stripe_customer_id=None,
                )
            )

            response = await auth_client.get("/api/subscription/current")

            assert response.status_code == 200
            data = response.json()
            assert data["plan"] == "free"
            assert data["status"] == "active"
            assert data["cancel_at_period_end"] is False

    @pytest.mark.asyncio
    async def test_create_checkout_session(self, auth_client):
        """チェックアウトセッションの作成"""
        with patch("app.routers.subscription.stripe_service") as mock_stripe:
            mock_stripe.create_checkout_session = AsyncMock(
                return_value=MagicMock(
                    checkout_url="https://checkout.stripe.com/test",
                    session_id="cs_test_123",
                )
            )

            response = await auth_client.post(
                "/api/subscription/checkout",
                json={
                    "plan": "standard",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                    "billing_cycle": "monthly",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["checkout_url"] == "https://checkout.stripe.com/test"
            assert data["session_id"] == "cs_test_123"

    @pytest.mark.asyncio
    async def test_create_checkout_invalid_plan(self, auth_client):
        """無効なプランでエラー"""
        with patch("app.routers.subscription.stripe_service") as mock_stripe:
            mock_stripe.create_checkout_session = AsyncMock(
                side_effect=ValueError("Invalid plan")
            )

            response = await auth_client.post(
                "/api/subscription/checkout",
                json={
                    "plan": "invalid_plan",
                    "success_url": "https://example.com/success",
                    "cancel_url": "https://example.com/cancel",
                },
            )

            # バリデーションエラーか業務エラー
            assert response.status_code in (400, 422, 502)

    @pytest.mark.asyncio
    async def test_cancel_subscription_free_plan(self, auth_client):
        """フリープランのキャンセルはエラー"""
        with patch("app.routers.subscription.stripe_service") as mock_stripe:
            mock_stripe.cancel_subscription = AsyncMock(
                side_effect=ValueError("Cannot cancel free plan")
            )

            response = await auth_client.post("/api/subscription/cancel")

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401/403エラー（HTTPBearer）"""
        response = await client.get("/api/subscription/plans")
        assert response.status_code in (401, 403)
