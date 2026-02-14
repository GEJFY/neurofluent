"""アナリティクス(Analytics)ルーター - 学習統計ダッシュボード"""

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import ConversationSession
from app.models.review import ReviewItem
from app.models.stats import DailyStat

router = APIRouter()


class DashboardResponse(BaseModel):
    """ダッシュボード統計レスポンス"""

    streak_days: int
    total_practice_minutes: int
    total_sessions: int
    total_reviews_completed: int
    total_expressions_learned: int
    avg_grammar_accuracy: float | None
    avg_pronunciation_score: float | None
    recent_daily_stats: list[dict]
    pending_reviews: int


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    ユーザーの学習ダッシュボードデータを取得

    連続学習日数（ストリーク）、累計時間、セッション数、
    復習完了数、直近7日間の日次統計を返す。
    """
    today = date.today()

    # 直近30日間の日次統計を取得
    stats_result = await db.execute(
        select(DailyStat)
        .where(
            DailyStat.user_id == current_user.id,
            DailyStat.date >= today - timedelta(days=30),
        )
        .order_by(DailyStat.date.desc())
    )
    all_stats = stats_result.scalars().all()

    # ストリーク計算: 今日から遡って連続で学習した日数を数える
    streak_days = 0
    stats_dates = {s.date for s in all_stats if s.practice_minutes > 0}

    check_date = today
    while check_date in stats_dates:
        streak_days += 1
        check_date -= timedelta(days=1)

    # 今日がまだ統計に含まれていない場合、昨日からチェック
    if streak_days == 0:
        check_date = today - timedelta(days=1)
        while check_date in stats_dates:
            streak_days += 1
            check_date -= timedelta(days=1)

    # 累計統計の集計
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(DailyStat.practice_minutes), 0),
            func.coalesce(func.sum(DailyStat.sessions_completed), 0),
            func.coalesce(func.sum(DailyStat.reviews_completed), 0),
            func.coalesce(func.sum(DailyStat.new_expressions_learned), 0),
            func.avg(DailyStat.grammar_accuracy),
            func.avg(DailyStat.pronunciation_avg_score),
        ).where(DailyStat.user_id == current_user.id)
    )
    total_row = total_result.one()

    total_practice_minutes = int(total_row[0])
    total_sessions = int(total_row[1])
    total_reviews = int(total_row[2])
    total_expressions = int(total_row[3])
    avg_grammar = float(total_row[4]) if total_row[4] is not None else None
    avg_pronunciation = float(total_row[5]) if total_row[5] is not None else None

    # セッション数がゼロの場合、conversation_sessionsテーブルから直接カウント
    if total_sessions == 0:
        session_count_result = await db.execute(
            select(func.count(ConversationSession.id)).where(
                ConversationSession.user_id == current_user.id
            )
        )
        total_sessions = session_count_result.scalar() or 0

    # 未復習アイテム数
    now = datetime.now(timezone.utc)
    pending_result = await db.execute(
        select(func.count(ReviewItem.id)).where(
            ReviewItem.user_id == current_user.id,
            (ReviewItem.next_review_at <= now) | (ReviewItem.next_review_at.is_(None)),
        )
    )
    pending_reviews = pending_result.scalar() or 0

    # 直近7日間の日次統計を整形
    recent_stats = []
    for stat in all_stats[:7]:
        recent_stats.append({
            "date": stat.date.isoformat(),
            "practice_minutes": stat.practice_minutes,
            "sessions_completed": stat.sessions_completed,
            "reviews_completed": stat.reviews_completed,
            "new_expressions_learned": stat.new_expressions_learned,
            "grammar_accuracy": stat.grammar_accuracy,
            "pronunciation_avg_score": stat.pronunciation_avg_score,
        })

    return DashboardResponse(
        streak_days=streak_days,
        total_practice_minutes=total_practice_minutes,
        total_sessions=total_sessions,
        total_reviews_completed=total_reviews,
        total_expressions_learned=total_expressions,
        avg_grammar_accuracy=avg_grammar,
        avg_pronunciation_score=avg_pronunciation,
        recent_daily_stats=recent_stats,
        pending_reviews=pending_reviews,
    )
