"""Stripe決済サービスのテスト"""

import hashlib
import hmac
import time
from uuid import uuid4

import pytest

from app.services.stripe_service import PLANS, StripeService


class TestPlans:
    """プラン定義のテスト"""

    def test_four_plans_exist(self):
        """4つのプラン（free, standard, premium, enterprise）が定義されている"""
        assert "free" in PLANS
        assert "standard" in PLANS
        assert "premium" in PLANS
        assert "enterprise" in PLANS

    def test_free_plan_prices(self):
        """Freeプランの料金が0"""
        assert PLANS["free"]["price_monthly"] == 0.0
        assert PLANS["free"]["price_yearly"] == 0.0

    def test_standard_plan_prices(self):
        """Standardプランの料金"""
        assert PLANS["standard"]["price_monthly"] == 9.99
        assert PLANS["standard"]["price_yearly"] == 99.99

    def test_premium_plan_prices(self):
        """Premiumプランの料金"""
        assert PLANS["premium"]["price_monthly"] == 19.99
        assert PLANS["premium"]["price_yearly"] == 199.99

    def test_free_plan_limits(self):
        """Freeプランの制限値"""
        limits = PLANS["free"]["limits"]
        assert limits["daily_sessions"] == 3
        assert limits["monthly_api_calls"] == 100
        assert limits["flash_exercises_per_day"] == 5

    def test_premium_plan_unlimited(self):
        """Premiumプランの無制限項目（-1 = 無制限）"""
        limits = PLANS["premium"]["limits"]
        assert limits["daily_sessions"] == -1
        assert limits["flash_exercises_per_day"] == -1
        assert limits["conversation_minutes_per_day"] == -1

    def test_all_plans_have_features(self):
        """全プランにfeaturesが存在する"""
        for plan_id, plan_data in PLANS.items():
            assert len(plan_data["features"]) > 0, f"Plan {plan_id} has no features"


class TestStripeService:
    """StripeServiceクラスのテスト"""

    def test_init(self):
        """初期化が正常に動作する"""
        service = StripeService()
        assert service.api_base == "https://api.stripe.com/v1"
        assert service.MAX_RETRIES == 3

    def test_build_headers_without_idempotency(self):
        """Idempotency Key なしのヘッダー構築"""
        service = StripeService()
        headers = service._build_headers()
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert "Idempotency-Key" not in headers

    def test_build_headers_with_idempotency(self):
        """Idempotency Key ありのヘッダー構築"""
        service = StripeService()
        headers = service._build_headers(idempotency_key="test-key-123")
        assert headers["Idempotency-Key"] == "test-key-123"

    def test_generate_idempotency_key(self):
        """Idempotency Key生成がhash形式であること"""
        user_id = uuid4()
        key = StripeService._generate_idempotency_key(user_id, "standard", "monthly")
        assert len(key) == 32
        assert isinstance(key, str)

    def test_idempotency_key_same_hour(self):
        """同一時間内で同じパラメータだと同じキーが生成される"""
        user_id = uuid4()
        key1 = StripeService._generate_idempotency_key(user_id, "standard", "monthly")
        key2 = StripeService._generate_idempotency_key(user_id, "standard", "monthly")
        assert key1 == key2

    def test_idempotency_key_different_plans(self):
        """異なるプランで異なるキーが生成される"""
        user_id = uuid4()
        key1 = StripeService._generate_idempotency_key(user_id, "standard", "monthly")
        key2 = StripeService._generate_idempotency_key(user_id, "premium", "monthly")
        assert key1 != key2

    def test_get_plans(self):
        """プラン一覧取得が正しい構造を返す"""
        service = StripeService()
        plans = service.get_plans()
        assert len(plans) == 4
        plan_ids = [p.id for p in plans]
        assert "free" in plan_ids
        assert "standard" in plan_ids
        assert "premium" in plan_ids
        assert "enterprise" in plan_ids

    def test_get_plans_current_plan(self):
        """現在のプランがis_current=Trueで返る"""
        service = StripeService()
        plans = service.get_plans(current_plan="standard")
        for plan in plans:
            if plan.id == "standard":
                assert plan.is_current is True
            else:
                assert plan.is_current is False

    def test_get_plans_features_structure(self):
        """プランのfeaturesが正しい構造を持つ"""
        service = StripeService()
        plans = service.get_plans()
        for plan in plans:
            for feature in plan.features:
                assert hasattr(feature, "name")
                assert hasattr(feature, "description")
                assert hasattr(feature, "included")

    def test_get_plans_limits_structure(self):
        """プランのlimitsが正しい構造を持つ"""
        service = StripeService()
        plans = service.get_plans()
        for plan in plans:
            assert hasattr(plan.limits, "daily_sessions")
            assert hasattr(plan.limits, "monthly_api_calls")
            assert hasattr(plan.limits, "flash_exercises_per_day")


class TestWebhookSignatureVerification:
    """Webhook署名検証のテスト"""

    def test_verify_valid_signature(self):
        """有効な署名の検証が成功する"""
        service = StripeService()
        service.webhook_secret = "whsec_test_secret"

        payload = b'{"id": "evt_test", "type": "test"}'
        timestamp = str(int(time.time()))

        # 正しい署名を生成
        signed_payload = f"{timestamp}.".encode() + payload
        expected_sig = hmac.new(
            service.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        signature = f"t={timestamp},v1={expected_sig}"

        # エラーなく検証完了
        service._verify_webhook_signature(payload, signature)

    def test_verify_invalid_signature(self):
        """無効な署名の検証が失敗する"""
        service = StripeService()
        service.webhook_secret = "whsec_test_secret"

        payload = b'{"id": "evt_test"}'
        signature = f"t={int(time.time())},v1=invalid_signature_hash"

        with pytest.raises(ValueError, match="署名の検証に失敗"):
            service._verify_webhook_signature(payload, signature)

    def test_verify_missing_signature(self):
        """署名なしの場合にエラー"""
        service = StripeService()
        service.webhook_secret = "whsec_test_secret"

        with pytest.raises(ValueError):
            service._verify_webhook_signature(b"payload", "")

    def test_verify_expired_timestamp(self):
        """古いタイムスタンプの署名が拒否される"""
        service = StripeService()
        service.webhook_secret = "whsec_test_secret"

        payload = b'{"id": "evt_test"}'
        old_timestamp = str(int(time.time()) - 600)  # 10分前

        signed_payload = f"{old_timestamp}.".encode() + payload
        expected_sig = hmac.new(
            service.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        signature = f"t={old_timestamp},v1={expected_sig}"

        with pytest.raises(ValueError, match="タイムスタンプが古すぎ"):
            service._verify_webhook_signature(payload, signature)

    def test_verify_invalid_format(self):
        """不正なフォーマットの署名が拒否される"""
        service = StripeService()
        service.webhook_secret = "whsec_test_secret"

        with pytest.raises(ValueError):
            service._verify_webhook_signature(b"payload", "invalid_format")


class TestCheckoutValidation:
    """チェックアウトセッション作成のバリデーションテスト"""

    @pytest.mark.asyncio
    async def test_invalid_plan_raises(self):
        """無効なプランIDでValueErrorが発生する"""
        service = StripeService()
        with pytest.raises(ValueError, match="無効なプラン"):
            await service.create_checkout_session(
                user_id=uuid4(),
                plan="nonexistent",
                success_url="http://localhost/success",
                cancel_url="http://localhost/cancel",
            )

    @pytest.mark.asyncio
    async def test_free_plan_raises(self):
        """freeプランでValueErrorが発生する"""
        service = StripeService()
        with pytest.raises(ValueError, match="無効なプラン"):
            await service.create_checkout_session(
                user_id=uuid4(),
                plan="free",
                success_url="http://localhost/success",
                cancel_url="http://localhost/cancel",
            )
