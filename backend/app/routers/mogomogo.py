"""もごもごイングリッシュ（Mogomogo English）ルーター - 音声変化パターン訓練

リンキング・リダクション・フラッピング・削除・弱形の5種類の
音声変化パターンを聞き取る力を養成するエンドポイント群。
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.sound_pattern import SoundPatternMastery
from app.schemas.mogomogo import (
    MogomogoExercise,
    DictationRequest,
    DictationResult,
    SoundPatternInfo,
    MogomogoProgress,
    MogomogoProgressItem,
)
from app.services.mogomogo_service import mogomogo_service

router = APIRouter()


@router.get("/patterns", response_model=list[SoundPatternInfo])
async def get_sound_patterns(
    current_user: User = Depends(get_current_user),
):
    """
    利用可能な音声変化パターン種別を取得

    各パターンの名称、説明、例文、IPA表記を返す。
    対応パターン: linking, reduction, flapping, deletion, weak_form
    """
    return mogomogo_service.get_pattern_types()


@router.get("/exercises", response_model=list[MogomogoExercise])
async def generate_exercises(
    current_user: User = Depends(get_current_user),
    pattern_types: str = Query(
        default="linking,reduction",
        description="カンマ区切りのパターン種別 (linking,reduction,flapping,deletion,weak_form)",
    ),
    count: int = Query(default=10, ge=1, le=30, description="生成する問題数"),
    difficulty: str = Query(default=None, description="難易度レベル (A2, B1, B2, C1, C2)"),
):
    """
    指定された音声変化パターンの練習問題を生成

    パターン種別と問題数を指定して、AI生成のエクササイズを取得する。
    難易度はユーザーのtarget_levelがデフォルトで使用される。
    """
    types_list = [t.strip() for t in pattern_types.split(",") if t.strip()]
    level = difficulty or current_user.target_level

    exercises = await mogomogo_service.generate_exercises(
        pattern_types=types_list,
        user_level=level,
        count=count,
    )
    return exercises


@router.post("/dictation/check", response_model=DictationResult)
async def check_dictation(
    data: DictationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ディクテーション回答をチェック

    ユーザーが聞き取って書いたテキストと元のテキストを比較し、
    正確度・見落とし単語・認識パターンを返す。
    結果は音声パターン習熟度テーブルにも反映される。
    """
    result = await mogomogo_service.check_dictation(
        exercise_id=data.exercise_id,
        user_text=data.user_text,
        original_text=data.original_text,
    )

    # 習熟度の更新: SoundPatternMasteryテーブルに反映
    # exercise_idからパターン種別を推定（IDにパターン名が含まれている場合）
    # または、identified_patternsから推定
    for pattern in result.identified_patterns:
        # パターン名のキーワードマッチ
        pattern_type = _detect_pattern_type(pattern)
        if pattern_type:
            await _update_pattern_mastery(
                user_id=current_user.id,
                pattern_type=pattern_type,
                pattern_text=data.original_text,
                accuracy=result.accuracy,
                db=db,
            )

    # パターンが特定できなかった場合、全体精度で汎用更新
    if not result.identified_patterns:
        await _update_pattern_mastery(
            user_id=current_user.id,
            pattern_type="general",
            pattern_text=data.original_text,
            accuracy=result.accuracy,
            db=db,
        )

    return result


@router.get("/progress", response_model=MogomogoProgress)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーの音声パターン習熟度進捗を取得

    パターン種別ごとの正確度、練習回数、習熟レベルを返す。
    """
    # 全パターンの習熟度を取得
    result = await db.execute(
        select(SoundPatternMastery)
        .where(SoundPatternMastery.user_id == current_user.id)
        .order_by(SoundPatternMastery.pattern_type)
    )
    masteries = result.scalars().all()

    if not masteries:
        return MogomogoProgress(
            overall_accuracy=0.0,
            total_practice_count=0,
            patterns=[],
        )

    # パターン種別ごとに集約
    pattern_map: dict[str, list] = {}
    for m in masteries:
        if m.pattern_type not in pattern_map:
            pattern_map[m.pattern_type] = []
        pattern_map[m.pattern_type].append(m)

    patterns = []
    total_accuracy = 0.0
    total_count = 0

    # パターン名のマッピング
    pattern_names = {
        "linking": "Linking",
        "reduction": "Reduction",
        "flapping": "Flapping",
        "deletion": "Deletion",
        "weak_form": "Weak Forms",
        "general": "General",
    }

    for pt, entries in pattern_map.items():
        avg_accuracy = sum(e.accuracy for e in entries) / len(entries) if entries else 0.0
        total_practice = sum(e.practice_count for e in entries)

        # 習熟レベル判定
        if avg_accuracy >= 0.9 and total_practice >= 20:
            mastery_level = "mastered"
        elif avg_accuracy >= 0.7 and total_practice >= 10:
            mastery_level = "proficient"
        elif avg_accuracy >= 0.5 or total_practice >= 5:
            mastery_level = "developing"
        else:
            mastery_level = "beginner"

        patterns.append(MogomogoProgressItem(
            pattern_type=pt,
            pattern_name=pattern_names.get(pt, pt.replace("_", " ").title()),
            accuracy=round(avg_accuracy, 3),
            practice_count=total_practice,
            mastery_level=mastery_level,
        ))

        total_accuracy += avg_accuracy
        total_count += total_practice

    overall = total_accuracy / len(pattern_map) if pattern_map else 0.0

    return MogomogoProgress(
        overall_accuracy=round(overall, 3),
        total_practice_count=total_count,
        patterns=patterns,
    )


# --- ヘルパー関数 ---

def _detect_pattern_type(pattern_description: str) -> str | None:
    """パターン説明文からパターン種別を推定"""
    desc_lower = pattern_description.lower()

    if "link" in desc_lower or "connect" in desc_lower:
        return "linking"
    elif "reduc" in desc_lower or "gonna" in desc_lower or "wanna" in desc_lower:
        return "reduction"
    elif "flap" in desc_lower or "tap" in desc_lower:
        return "flapping"
    elif "delet" in desc_lower or "elision" in desc_lower or "drop" in desc_lower:
        return "deletion"
    elif "weak" in desc_lower or "unstress" in desc_lower or "schwa" in desc_lower:
        return "weak_form"
    return None


async def _update_pattern_mastery(
    user_id,
    pattern_type: str,
    pattern_text: str,
    accuracy: float,
    db: AsyncSession,
) -> None:
    """音声パターン習熟度を更新"""
    result = await db.execute(
        select(SoundPatternMastery).where(
            SoundPatternMastery.user_id == user_id,
            SoundPatternMastery.pattern_type == pattern_type,
            SoundPatternMastery.pattern_text == pattern_text,
        )
    )
    mastery = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if mastery is None:
        mastery = SoundPatternMastery(
            user_id=user_id,
            pattern_type=pattern_type,
            pattern_text=pattern_text,
            accuracy=accuracy,
            practice_count=1,
            last_practiced_at=now,
        )
        db.add(mastery)
    else:
        # 指数移動平均で精度を更新（直近の結果を重視）
        alpha = 0.3
        mastery.accuracy = alpha * accuracy + (1 - alpha) * mastery.accuracy
        mastery.practice_count += 1
        mastery.last_practiced_at = now

    await db.commit()
