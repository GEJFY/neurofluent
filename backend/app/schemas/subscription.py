"""サブスクリプション（Subscription）スキーマ - プラン・決済管理"""

from datetime import datetime

from pydantic import BaseModel, Field


class PlanFeature(BaseModel):
    """プラン機能詳細"""

    name: str
    description: str
    included: bool = True


class PlanLimits(BaseModel):
    """プラン制限"""

    daily_sessions: int = Field(description="1日あたりのセッション上限")
    monthly_api_calls: int = Field(description="月間API呼び出し上限")
    flash_exercises_per_day: int = Field(description="1日あたりの瞬間英作文上限")
    conversation_minutes_per_day: int = Field(description="1日あたりの会話練習時間（分）")
    pronunciation_evaluations_per_day: int = Field(description="1日あたりの発音評価上限")
    advanced_analytics: bool = Field(default=False, description="詳細分析機能")
    ai_curriculum: bool = Field(default=False, description="AIカリキュラム最適化")
    priority_support: bool = Field(default=False, description="優先サポート")


class PlanInfo(BaseModel):
    """プラン情報"""

    id: str = Field(description="プランID: free, standard, premium, enterprise")
    name: str = Field(description="プラン名称")
    price_monthly: float = Field(description="月額料金（USD）")
    price_yearly: float = Field(description="年額料金（USD）")
    features: list[PlanFeature] = Field(default_factory=list, description="含まれる機能一覧")
    limits: PlanLimits = Field(description="プラン制限")
    is_current: bool = Field(default=False, description="現在のプランかどうか")

    model_config = {"from_attributes": True}


class SubscriptionInfo(BaseModel):
    """サブスクリプション情報"""

    plan: str = Field(description="現在のプラン: free, standard, premium, enterprise")
    status: str = Field(description="ステータス: active, canceled, past_due, trialing")
    current_period_start: datetime | None = Field(default=None, description="現在の課金期間開始日")
    current_period_end: datetime | None = Field(default=None, description="現在の課金期間終了日")
    cancel_at_period_end: bool = Field(default=False, description="期間終了時にキャンセルされるか")
    stripe_customer_id: str | None = Field(default=None, description="Stripe顧客ID")

    model_config = {"from_attributes": True}


class CheckoutSessionRequest(BaseModel):
    """チェックアウトセッション作成リクエスト"""

    plan: str = Field(description="選択プラン: standard, premium, enterprise")
    success_url: str = Field(description="決済成功後のリダイレクトURL")
    cancel_url: str = Field(description="決済キャンセル時のリダイレクトURL")
    billing_cycle: str = Field(default="monthly", description="課金サイクル: monthly, yearly")


class CheckoutSessionResponse(BaseModel):
    """チェックアウトセッションレスポンス"""

    checkout_url: str = Field(description="StripeチェックアウトページへのリダイレクトURL")
    session_id: str = Field(description="StripeセッションID")


class WebhookPayload(BaseModel):
    """Stripe Webhookペイロード"""

    event_type: str = Field(description="Webhookイベント種別")
    data: dict = Field(default_factory=dict, description="イベントデータ")


class CancelSubscriptionResponse(BaseModel):
    """サブスクリプションキャンセルレスポンス"""

    success: bool
    message: str
    cancel_at_period_end: bool = True
    current_period_end: datetime | None = None
