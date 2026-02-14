"""発音トレーニング（Pronunciation）ルーター - 音素・韻律の練習・評価

日本語話者に特有の発音問題（/r/-/l/, /θ/-/s/, /v/-/b/等）を
ターゲットにしたミニマルペア、舌を鍛える練習、文練習の
エクササイズ生成と、Azure Speech APIを用いた発音評価。
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.sound_pattern import SoundPatternMastery
from app.schemas.pronunciation import (
    PronunciationExercise,
    PhonemeResult,
    PronunciationEvaluateRequest,
    ProsodyExercise,
    JapaneseSpeakerPhoneme,
    PronunciationOverallProgress,
    PronunciationProgressItem,
)
from app.services.pronunciation_service import pronunciation_service

router = APIRouter()


@router.get("/phonemes", response_model=list[JapaneseSpeakerPhoneme])
async def get_japanese_speaker_phonemes(
    current_user: User = Depends(get_current_user),
):
    """
    日本語話者に共通する発音問題の一覧を取得

    L1干渉パターン（/r/-/l/, /θ/-/s/, /v/-/b/, /f/-/h/, /ae/-/uh/等）の
    説明、ミニマルペア、練習用単語、発音のコツを返す。
    """
    return pronunciation_service.get_japanese_speaker_problems()


@router.get("/exercises", response_model=list[PronunciationExercise])
async def generate_pronunciation_exercises(
    current_user: User = Depends(get_current_user),
    phonemes: str = Query(
        default="/r/-/l/",
        description="カンマ区切りの音素ペア (例: /r/-/l/,/θ/-/s/)",
    ),
    type: str | None = Query(
        default=None,
        description="問題種別フィルタ: minimal_pair, tongue_twister, sentence",
    ),
    count: int = Query(default=10, ge=1, le=30, description="生成する問題数"),
):
    """
    発音練習問題を生成

    指定した音素ペアに基づき、ミニマルペア、早口言葉、文練習の
    エクササイズをAI生成する。
    """
    phonemes_list = [p.strip() for p in phonemes.split(",") if p.strip()]
    level = current_user.target_level

    exercises = await pronunciation_service.generate_exercises(
        target_phonemes=phonemes_list,
        user_level=level,
        count=count,
        exercise_type=type,
    )
    return exercises


@router.post("/evaluate", response_model=PhonemeResult)
async def evaluate_pronunciation(
    audio: UploadFile = File(description="WAV形式の音声ファイル"),
    target_phoneme: str = Form(description="評価対象の音素 (例: /r/-/l/)"),
    reference_text: str = Form(description="参照テキスト（発話すべきテキスト）"),
    exercise_id: str | None = Form(default=None, description="エクササイズID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    発音を評価（マルチパート: 音声 + メタデータ）

    Azure Speech APIの発音評価機能を使用して音素レベルの評価を行う。
    結果は音声パターン習熟度テーブルにも反映される。
    """
    audio_data = await audio.read()

    result = await pronunciation_service.evaluate_phoneme(
        audio_data=audio_data,
        target_phoneme=target_phoneme,
        reference_text=reference_text,
    )

    # 習熟度の更新
    if result.accuracy > 0:
        await _update_pronunciation_mastery(
            user_id=current_user.id,
            pattern_type=f"phoneme_{target_phoneme}",
            pattern_text=reference_text,
            accuracy=result.accuracy,
            db=db,
        )

    return result


@router.get("/prosody/exercises", response_model=list[ProsodyExercise])
async def get_prosody_exercises(
    current_user: User = Depends(get_current_user),
    pattern: str = Query(
        default="stress",
        description="パターン種別: stress, rhythm, intonation",
    ),
    count: int = Query(default=5, ge=1, le=15, description="生成する問題数"),
):
    """
    韻律エクササイズを取得

    ストレス（強勢）、リズム、イントネーションの練習問題を生成する。
    日本語のモーラタイミングと英語のストレスタイミングの違いに
    フォーカスした練習を提供。
    """
    exercises = await pronunciation_service.generate_prosody_exercise(
        pattern=pattern,
        count=count,
    )
    return exercises


@router.get("/progress", response_model=PronunciationOverallProgress)
async def get_pronunciation_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    音素レベルの発音進捗を取得

    音素別の精度、練習回数、トレンド、強み・弱みを返す。
    """
    result = await db.execute(
        select(SoundPatternMastery)
        .where(
            SoundPatternMastery.user_id == current_user.id,
            SoundPatternMastery.pattern_type.like("phoneme_%"),
        )
        .order_by(SoundPatternMastery.pattern_type)
    )
    masteries = result.scalars().all()

    if not masteries:
        return PronunciationOverallProgress(
            overall_accuracy=0.0,
            total_evaluations=0,
            phoneme_progress=[],
            strongest_phonemes=[],
            weakest_phonemes=[],
        )

    # 音素ごとに集約
    phoneme_map: dict[str, list] = {}
    for m in masteries:
        # "phoneme_/r/-/l/" -> "/r/-/l/"
        phoneme = m.pattern_type.replace("phoneme_", "", 1)
        if phoneme not in phoneme_map:
            phoneme_map[phoneme] = []
        phoneme_map[phoneme].append(m)

    phoneme_progress = []
    total_accuracy_sum = 0.0
    total_evaluations = 0

    for phoneme, entries in phoneme_map.items():
        avg_accuracy = sum(e.accuracy for e in entries) / len(entries)
        total_practice = sum(e.practice_count for e in entries)
        total_accuracy_sum += avg_accuracy
        total_evaluations += total_practice

        # トレンド判定
        trend = "stable"
        if len(entries) >= 2:
            sorted_entries = sorted(entries, key=lambda e: e.last_practiced_at or e.created_at)
            recent = sorted_entries[-1].accuracy
            older = sorted_entries[0].accuracy
            if recent > older + 0.1:
                trend = "improving"
            elif recent < older - 0.1:
                trend = "declining"

        phoneme_progress.append(PronunciationProgressItem(
            phoneme=phoneme,
            accuracy=round(avg_accuracy, 3),
            practice_count=total_practice,
            trend=trend,
        ))

    overall = total_accuracy_sum / len(phoneme_map) if phoneme_map else 0.0

    # 強み・弱みの特定
    sorted_phonemes = sorted(phoneme_progress, key=lambda p: p.accuracy, reverse=True)
    strongest = [p.phoneme for p in sorted_phonemes if p.accuracy >= 0.7][:3]
    weakest = [p.phoneme for p in sorted_phonemes if p.accuracy < 0.6][:3]

    return PronunciationOverallProgress(
        overall_accuracy=round(overall, 3),
        total_evaluations=total_evaluations,
        phoneme_progress=phoneme_progress,
        strongest_phonemes=strongest,
        weakest_phonemes=weakest,
    )


# --- ヘルパー関数 ---

async def _update_pronunciation_mastery(
    user_id,
    pattern_type: str,
    pattern_text: str,
    accuracy: float,
    db: AsyncSession,
) -> None:
    """発音習熟度を更新"""
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
        # 指数移動平均で精度を更新
        alpha = 0.3
        mastery.accuracy = alpha * accuracy + (1 - alpha) * mastery.accuracy
        mastery.practice_count += 1
        mastery.last_practiced_at = now

    await db.commit()
