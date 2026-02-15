"""瞬間英作文(Speaking/Flash)ルーター - フラッシュ翻訳エクササイズ"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.review import ReviewItem
from app.models.user import User
from app.schemas.speaking import FlashCheckRequest, FlashCheckResponse, FlashExercise
from app.services.flash_service import flash_service

router = APIRouter()


@router.get("/flash", response_model=list[FlashExercise])
async def generate_flash_exercises(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    count: int = Query(default=5, ge=1, le=20),
    focus: str | None = Query(
        default=None, description="フォーカスする文法・表現カテゴリ"
    ),
):
    """
    ユーザーのレベルと弱点に基づいてフラッシュ翻訳エクササイズを生成

    弱点パターンはユーザーの日次統計から取得し、
    重点的に出題される問題を動的に生成する。
    """
    # ユーザーの弱点パターンを取得（直近の統計から）
    from sqlalchemy import select

    from app.models.stats import DailyStat

    stats_result = await db.execute(
        select(DailyStat)
        .where(DailyStat.user_id == current_user.id)
        .order_by(DailyStat.date.desc())
        .limit(7)
    )
    recent_stats = stats_result.scalars().all()

    # 弱点パターンを集約
    weak_patterns = []
    for stat in recent_stats:
        if stat.weak_patterns:
            patterns = stat.weak_patterns
            if isinstance(patterns, list):
                weak_patterns.extend(patterns)
            elif isinstance(patterns, dict):
                weak_patterns.extend(patterns.keys())

    # 重複を除去して上位5件に絞る
    unique_weak = list(dict.fromkeys(weak_patterns))[:5]

    exercises = await flash_service.generate_exercises(
        level=current_user.target_level,
        focus=focus,
        weak_patterns=unique_weak if unique_weak else None,
        count=count,
    )

    return exercises


@router.post("/flash/check", response_model=FlashCheckResponse)
async def check_flash_answer(
    data: FlashCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーの回答を評価し、必要に応じて復習アイテムを作成

    スコアが0.7未満の場合、自動的に復習アイテムを作成して
    FSRSアルゴリズムによるスケジュールに追加する。
    """
    result = await flash_service.check_answer(
        user_answer=data.user_answer,
        target=data.target,
    )

    # スコアが低い場合は復習アイテムを作成
    if result.score < 0.7:
        review_item = ReviewItem(
            user_id=current_user.id,
            item_type="flash_translation",
            content={
                "exercise_id": data.exercise_id,
                "target": data.target,
                "user_answer": data.user_answer,
                "corrected": result.corrected,
                "explanation": result.explanation,
            },
            next_review_at=datetime.now(UTC),
        )
        db.add(review_item)
        await db.commit()
        result.review_item_created = True

    return result
