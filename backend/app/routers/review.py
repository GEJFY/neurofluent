"""復習(Review)ルーター - 間隔反復学習のスケジュール管理"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.review import ReviewItem
from app.models.user import User
from app.schemas.review import (
    ReviewCompleteRequest,
    ReviewCompleteResponse,
    ReviewItemResponse,
)
from app.services.spaced_repetition import FSRSCard, fsrs

router = APIRouter()


@router.get("/due", response_model=list[ReviewItemResponse])
async def get_due_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    今日の復習対象アイテムを取得

    next_review_atが現在時刻以前のアイテムと、
    まだ一度も復習されていないアイテムを返す。
    """
    now = datetime.now(UTC)

    result = await db.execute(
        select(ReviewItem)
        .where(
            ReviewItem.user_id == current_user.id,
            (ReviewItem.next_review_at <= now) | (ReviewItem.next_review_at.is_(None)),
        )
        .order_by(ReviewItem.next_review_at.asc().nullsfirst())
        .limit(limit)
    )
    items = result.scalars().all()

    return [
        ReviewItemResponse(
            id=item.id,
            item_type=item.item_type,
            content=item.content,
            next_review_at=item.next_review_at,
            ease_factor=item.ease_factor,
            interval_days=item.interval_days,
            repetitions=item.repetitions,
        )
        for item in items
    ]


@router.post("/complete", response_model=ReviewCompleteResponse)
async def complete_review(
    data: ReviewCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    復習結果を記録し、FSRSアルゴリズムで次回復習日を計算

    レーティング:
        1 = Again（もう一度）: 完全に忘れていた
        2 = Hard（難しい）: 思い出せたが困難だった
        3 = Good（良い）: 適度な努力で思い出せた
        4 = Easy（簡単）: 即座に思い出せた
    """
    # 復習アイテムを取得
    result = await db.execute(
        select(ReviewItem).where(
            ReviewItem.id == data.item_id,
            ReviewItem.user_id == current_user.id,
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="復習アイテムが見つかりません",
        )

    # 経過日数を計算
    elapsed_days = 0.0
    if item.last_reviewed_at is not None:
        delta = datetime.now(UTC) - item.last_reviewed_at
        elapsed_days = max(0, delta.total_seconds() / 86400)

    # FSRSカードオブジェクトを構築
    card = FSRSCard(
        stability=item.stability,
        difficulty=item.difficulty,
        interval=float(item.interval_days),
        repetitions=item.repetitions,
        ease_factor=item.ease_factor,
        last_review=item.last_reviewed_at,
    )

    # FSRSアルゴリズムで更新
    updated_card = fsrs.review(card, rating=data.rating, elapsed_days=elapsed_days)

    # DBモデルを更新
    item.stability = updated_card.stability
    item.difficulty = updated_card.difficulty
    item.ease_factor = updated_card.ease_factor
    item.interval_days = max(1, int(updated_card.interval))
    item.repetitions = updated_card.repetitions
    item.next_review_at = updated_card.next_review
    item.last_reviewed_at = updated_card.last_review
    item.last_quality = data.rating

    await db.commit()
    await db.refresh(item)

    return ReviewCompleteResponse(
        next_review_at=item.next_review_at,
        new_interval_days=item.interval_days,
        new_ease_factor=item.ease_factor,
    )
