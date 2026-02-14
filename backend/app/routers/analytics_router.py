"""拡張アナリティクス（Extended Analytics）ルーター - 詳細学習分析

週次・月次レポート、スキル分析、発音進捗追跡、AI推奨事項、
概日リズム最適化日次メニューを提供するエンドポイント群。
既存のanalytics.pyのダッシュボード機能を拡張する。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    WeeklyReport,
    MonthlyReport,
    SkillBreakdown,
    PronunciationProgress,
    Recommendation,
    DailyMenu,
    FocusArea,
)
from app.services.analytics_service import analytics_service
from app.services.curriculum_service import curriculum_service

router = APIRouter()


@router.get("/weekly-report", response_model=WeeklyReport)
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    週次学習レポートを取得

    今週（月曜日〜日曜日）の学習実績を集計し、
    前週との比較データとともに返す。
    - 合計学習時間、セッション数、復習数
    - 日別詳細データ
    - 前週比改善率
    """
    return await analytics_service.get_weekly_report(current_user.id, db)


@router.get("/monthly-report", response_model=MonthlyReport)
async def get_monthly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    月次学習レポートを取得

    今月の学習実績を集計し、トレンドチャートデータ、
    スキルレーダーデータ、アチーブメントとともに返す。
    - 週ごとのトレンド
    - 強み・弱みの分析
    - 推奨アクション
    """
    return await analytics_service.get_monthly_report(current_user.id, db)


@router.get("/skills", response_model=SkillBreakdown)
async def get_skill_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    スキル分類別の詳細分析を取得

    スピーキング、リスニング、語彙の3大スキルについて、
    直近30日間のデータに基づく詳細分析を返す。
    - スピーキング: 応答速度、フィラー語、文法精度、表現レベル
    - リスニング: 速度別理解度、弱点パターン、ディクテーション精度
    - 語彙: 語彙範囲、洗練度、週あたり新規語彙数
    """
    return await analytics_service.get_skill_breakdown(current_user.id, db)


@router.get("/pronunciation-progress", response_model=PronunciationProgress)
async def get_pronunciation_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    発音改善の進捗データを取得

    直近30日間の発音スコアのトレンドと、
    音素・パターン別のスコアを返す。
    - 全体トレンド（日次スコア推移）
    - 音素別スコア
    - 弱点音素リスト
    """
    return await analytics_service.get_pronunciation_progress(current_user.id, db)


@router.get("/recommendations", response_model=list[Recommendation])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI生成の学習推奨事項を取得

    ユーザーの直近7日間の学習データと弱点分野を分析し、
    3〜5件のパーソナライズされた推奨事項を返す。
    各推奨事項にはカテゴリ、優先度、推奨エクササイズ種別が含まれる。
    """
    return await analytics_service.get_learning_recommendations(current_user.id, db)


@router.get("/daily-menu", response_model=DailyMenu)
async def get_daily_menu(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    本日の推奨学習メニューを取得

    概日リズム（朝・午後・夕方・夜）に基づいて最適化された
    学習メニューを生成する。

    - 朝（5-12時）: 高認知負荷 → 瞬間英作文、文法パターン
    - 午後（12-17時）: 中負荷 → 会話練習、シャドーイング
    - 夕方（17-21時）: 統合 → 復習、理解力テスト
    - 夜（21-5時）: 受動 → リスニングのみ
    """
    return await curriculum_service.generate_daily_menu(current_user.id, db)


@router.get("/focus-areas", response_model=list[FocusArea])
async def get_focus_areas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    フォーカスエリア（ベイジアン知識モデル）を取得

    各スキルについてBeta分布 P(知識あり) を計算し、
    目標レベルとのギャップが大きい順に返す。
    """
    return await curriculum_service.get_focus_areas(current_user.id, db)
