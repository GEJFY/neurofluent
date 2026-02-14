"""パターンプラクティスルーター - ビジネス英語パターン練習API

パターンカテゴリの取得、エクササイズ生成、回答チェック、
ユーザーの習熟度進捗トラッキングを提供。
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.pattern import PatternMastery
from app.schemas.pattern import (
    PatternExercise,
    PatternCheckRequest,
    PatternCheckResult,
    PatternCategory,
    PatternProgress,
)
from app.services.pattern_service import pattern_service

router = APIRouter()


@router.get("/categories", response_model=list[PatternCategory])
async def get_pattern_categories(
    current_user: User = Depends(get_current_user),
):
    """
    パターンカテゴリ一覧を取得

    各カテゴリの名前、説明、パターン数を返す。
    """
    return pattern_service.get_categories()


@router.get("/exercises", response_model=list[PatternExercise])
async def get_pattern_exercises(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    category: str | None = Query(
        default=None,
        description="カテゴリ: meeting, negotiation, presentation, email, discussion, general",
    ),
    count: int = Query(
        default=10,
        ge=1,
        le=20,
        description="取得するエクササイズ数",
    ),
):
    """
    パターン練習エクササイズを取得

    ユーザーのレベルと弱点に基づいて、
    組み込みパターンまたはAI生成パターンを返す。
    """
    # カテゴリのバリデーション
    valid_categories = ["meeting", "negotiation", "presentation", "email", "discussion", "general"]
    if category and category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効なカテゴリです。有効な値: {', '.join(valid_categories)}",
        )

    # ユーザーの弱点パターンを取得
    mastery_result = await db.execute(
        select(PatternMastery)
        .where(
            PatternMastery.user_id == current_user.id,
            PatternMastery.accuracy_rate < 0.7,
        )
        .order_by(PatternMastery.accuracy_rate.asc())
        .limit(5)
    )
    weak_masteries = mastery_result.scalars().all()
    weak_patterns = [m.pattern_id for m in weak_masteries] if weak_masteries else None

    exercises = await pattern_service.get_patterns(
        category=category,
        user_level=current_user.target_level,
        count=count,
        weak_patterns=weak_patterns,
    )

    return exercises


@router.post("/check", response_model=PatternCheckResult)
async def check_pattern_answer(
    data: PatternCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    パターン練習の回答を評価

    ユーザーの回答をAIで評価し、スコア・解説・使用アドバイスを返す。
    結果に基づいてパターン習熟度を更新する。
    """
    result = await pattern_service.check_pattern(
        pattern_id=data.pattern_id,
        user_answer=data.user_answer,
        expected=data.expected,
    )

    # パターン習熟度を更新
    await _update_pattern_mastery(
        db=db,
        user_id=current_user.id,
        pattern_id=data.pattern_id,
        is_correct=result.is_correct,
        score=result.score,
    )

    return result


@router.get("/progress", response_model=list[PatternProgress])
async def get_pattern_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーのパターン習熟度進捗を取得

    各カテゴリごとの習熟度サマリーを返す。
    """
    # カテゴリごとの集計クエリ
    result = await db.execute(
        select(
            PatternMastery.pattern_category,
            func.count(PatternMastery.id).label("total_patterns"),
            func.sum(
                case(
                    (PatternMastery.skill_stage == "understood", 1),
                    else_=0,
                )
            ).label("understood"),
            func.sum(
                case(
                    (PatternMastery.skill_stage == "drilling", 1),
                    else_=0,
                )
            ).label("drilling"),
            func.sum(
                case(
                    (PatternMastery.skill_stage == "acquired", 1),
                    else_=0,
                )
            ).label("acquired"),
            func.avg(PatternMastery.accuracy_rate).label("average_accuracy"),
            func.sum(PatternMastery.practice_count).label("total_practice_count"),
        )
        .where(PatternMastery.user_id == current_user.id)
        .group_by(PatternMastery.pattern_category)
    )
    rows = result.all()

    progress_list = []
    for row in rows:
        progress_list.append(
            PatternProgress(
                category=row.pattern_category,
                total_patterns=row.total_patterns or 0,
                understood=row.understood or 0,
                drilling=row.drilling or 0,
                acquired=row.acquired or 0,
                average_accuracy=round(float(row.average_accuracy or 0), 3),
                total_practice_count=row.total_practice_count or 0,
            )
        )

    # 練習していないカテゴリも空エントリとして追加
    existing_categories = {p.category for p in progress_list}
    all_categories = ["meeting", "negotiation", "presentation", "email", "discussion", "general"]
    for cat in all_categories:
        if cat not in existing_categories:
            progress_list.append(
                PatternProgress(
                    category=cat,
                    total_patterns=0,
                    understood=0,
                    drilling=0,
                    acquired=0,
                    average_accuracy=0.0,
                    total_practice_count=0,
                )
            )

    return progress_list


async def _update_pattern_mastery(
    db: AsyncSession,
    user_id: uuid.UUID,
    pattern_id: str,
    is_correct: bool,
    score: float,
) -> None:
    """
    パターン習熟度を更新または新規作成

    練習回数・正答率を更新し、スキルステージを
    適切に進行させる。

    ステージ遷移ルール:
    - understood -> drilling: 練習回数 >= 3
    - drilling -> acquired: 正答率 >= 0.8 かつ 練習回数 >= 10
    """
    # パターンIDからカテゴリを推定
    prefix_map = {
        "mtg": "meeting",
        "neg": "negotiation",
        "prs": "presentation",
        "eml": "email",
        "dsc": "discussion",
        "gen": "general",
        "ai": "general",
    }
    prefix = pattern_id.split("-")[0] if "-" in pattern_id else "gen"
    category = prefix_map.get(prefix, "general")

    # 既存の習熟度レコードを検索
    result = await db.execute(
        select(PatternMastery).where(
            PatternMastery.user_id == user_id,
            PatternMastery.pattern_id == pattern_id,
        )
    )
    mastery = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if mastery is None:
        # 新規レコードを作成
        mastery = PatternMastery(
            user_id=user_id,
            pattern_id=pattern_id,
            pattern_category=category,
            skill_stage="understood",
            practice_count=1,
            accuracy_rate=score,
            last_practiced_at=now,
        )
        db.add(mastery)
    else:
        # 既存レコードを更新
        mastery.practice_count += 1
        # 指数移動平均で正答率を更新
        alpha = 0.3  # 新しいスコアの重み
        mastery.accuracy_rate = (
            alpha * score + (1 - alpha) * mastery.accuracy_rate
        )
        mastery.last_practiced_at = now

        # スキルステージの遷移チェック
        if mastery.skill_stage == "understood" and mastery.practice_count >= 3:
            mastery.skill_stage = "drilling"
        elif (
            mastery.skill_stage == "drilling"
            and mastery.accuracy_rate >= 0.8
            and mastery.practice_count >= 10
        ):
            mastery.skill_stage = "acquired"

    await db.flush()
