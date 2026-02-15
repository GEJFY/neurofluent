"""サブスクリプションルーターのテスト - プラン・決済管理"""

import pytest


class TestSubscriptionRouter:
    """Subscriptionルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_plans(self, auth_client, mock_stripe):
        """プラン一覧の取得"""
        response = await auth_client.get("/api/subscription/plans")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # mock_stripeのget_plansが空リストを返す設定
        mock_stripe.get_plans.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_subscription(self, auth_client, mock_stripe):
        """現在のサブスクリプション情報の取得"""
        response = await auth_client.get("/api/subscription/current")

        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "free"
        assert data["status"] == "active"
        assert data["cancel_at_period_end"] is False

    @pytest.mark.asyncio
    async def test_create_checkout_session(self, auth_client, mock_stripe):
        """チェックアウトセッションの作成"""
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
    async def test_create_checkout_invalid_plan(self, auth_client, mock_stripe):
        """無効なプランで400エラー"""
        response = await auth_client.post(
            "/api/subscription/checkout",
            json={
                "plan": "invalid_plan",
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_cancel_subscription_free_plan(self, auth_client, mock_stripe):
        """フリープランのキャンセルは400エラー"""
        response = await auth_client.post("/api/subscription/cancel")

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401エラー"""
        response = await client.get("/api/subscription/plans")
        assert response.status_code == 403
