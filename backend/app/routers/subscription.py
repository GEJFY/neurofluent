"""サブスクリプション（Subscription）ルーター - プラン・決済管理

Stripe連携によるサブスクリプション決済のエンドポイント群。
プラン一覧、チェックアウト、Webhook処理、キャンセルを提供する。
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.subscription import (
    CancelSubscriptionResponse,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    PlanInfo,
    SubscriptionInfo,
)
from app.services.stripe_service import stripe_service

router = APIRouter()


@router.get("/plans", response_model=list[PlanInfo])
async def get_plans(
    current_user: User = Depends(get_current_user),
):
    """
    利用可能なプラン一覧を取得

    Free, Standard ($9.99/月), Premium ($19.99/月), Enterprise の
    各プランの機能・制限情報を返す。
    ユーザーの現在のプランにis_current=Trueが設定される。
    """
    return stripe_service.get_plans(current_plan=current_user.subscription_plan)


@router.get("/current", response_model=SubscriptionInfo)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    現在のサブスクリプション情報を取得

    プラン名、ステータス、課金期間、キャンセル予定の有無を返す。
    サブスクリプション未登録の場合はfreeプランとして返す。
    """
    return await stripe_service.get_subscription(current_user.id, db)


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    data: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Stripeチェックアウトセッションを作成

    指定プランの決済ページURLを生成し返す。
    ユーザーはこのURLにリダイレクトされて決済を完了する。
    """
    if data.plan not in ("standard", "premium", "enterprise"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なプランです。standard, premium, enterpriseから選択してください。",
        )

    try:
        session = await stripe_service.create_checkout_session(
            user_id=current_user.id,
            plan=data.plan,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
            billing_cycle=data.billing_cycle,
        )
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="決済サービスとの通信に失敗しました。しばらく後にお試しください。",
        )


@router.post("/webhook")
async def handle_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe Webhookイベントを処理（認証不要）

    Stripe署名ヘッダーで検証を行う。
    対応イベント:
    - checkout.session.completed: 初回決済完了
    - customer.subscription.updated: サブスクリプション更新
    - customer.subscription.deleted: サブスクリプション削除
    """
    payload = await request.body()
    signature = request.headers.get("Stripe-Signature", "")

    try:
        result = await stripe_service.handle_webhook(payload, signature, db)
        return {"status": "ok", "event_type": result.get("event_type")}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook検証エラー: {str(e)}",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhookの処理中にエラーが発生しました。",
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    サブスクリプションをキャンセル

    現在の課金期間終了時にサブスクリプションが解約される。
    即時解約ではなく、期間終了まで機能は引き続き利用可能。
    """
    if current_user.subscription_plan == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のプランはフリープランのため、キャンセルできません。",
        )

    success = await stripe_service.cancel_subscription(current_user.id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="アクティブなサブスクリプションが見つかりません。",
        )

    # 更新後のサブスクリプション情報を取得
    sub_info = await stripe_service.get_subscription(current_user.id, db)

    return CancelSubscriptionResponse(
        success=True,
        message="サブスクリプションは現在の課金期間終了時にキャンセルされます。",
        cancel_at_period_end=True,
        current_period_end=sub_info.current_period_end,
    )
