"""AIカリキュラム最適化サービス - 概日リズムベースの学習計画

ユーザーの時間帯、弱点分野、学習ストリーク、未復習アイテム数に基づいて
最適化された日次学習メニューを生成する。ベイジアン知識モデルを用いて
各スキルの習熟度を追跡し、フォーカスエリアを特定する。
"""

import logging
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import ReviewItem
from app.models.sound_pattern import SoundPatternMastery
from app.models.stats import DailyStat
from app.prompts.analytics import build_daily_menu_prompt
from app.schemas.analytics import (
    ActivityItem,
    DailyMenu,
    FocusArea,
)
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)


# スキル定義: 各スキルのBeta分布初期パラメータ
SKILL_DEFINITIONS = {
    "grammar_accuracy": {
        "name": "Grammar Accuracy",
        "name_ja": "文法精度",
        "alpha_init": 2.0,
        "beta_init": 2.0,
        "target": 0.85,
        "exercise_types": ["flash_translation", "conversation"],
    },
    "pronunciation": {
        "name": "Pronunciation",
        "name_ja": "発音",
        "alpha_init": 2.0,
        "beta_init": 3.0,
        "target": 0.80,
        "exercise_types": ["pronunciation", "shadowing"],
    },
    "listening_comprehension": {
        "name": "Listening Comprehension",
        "name_ja": "リスニング理解力",
        "alpha_init": 2.0,
        "beta_init": 2.0,
        "target": 0.80,
        "exercise_types": ["comprehension", "dictation", "mogomogo"],
    },
    "connected_speech": {
        "name": "Connected Speech",
        "name_ja": "音声変化認識",
        "alpha_init": 1.0,
        "beta_init": 3.0,
        "target": 0.75,
        "exercise_types": ["mogomogo", "dictation"],
    },
    "vocabulary_range": {
        "name": "Vocabulary Range",
        "name_ja": "語彙力",
        "alpha_init": 2.0,
        "beta_init": 2.0,
        "target": 0.80,
        "exercise_types": ["vocabulary", "flash_translation", "comprehension"],
    },
    "fluency": {
        "name": "Fluency",
        "name_ja": "流暢さ",
        "alpha_init": 2.0,
        "beta_init": 3.0,
        "target": 0.80,
        "exercise_types": ["conversation", "shadowing"],
    },
}


class CurriculumService:
    """AIカリキュラム最適化サービス"""

    async def generate_daily_menu(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> DailyMenu:
        """
        概日リズムに基づく日次学習メニューを生成

        時間帯ごとの認知負荷最適化:
        - 朝: 高負荷（瞬間英作文、パターン練習、精度モード）
        - 午後: 中負荷（シャドーイング、リスニング、流暢さモード）
        - 夕方: 統合（復習、理解力テスト、まとめ）
        - 夜: 受動（リスニングのみ、テストなし）

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            DailyMenu: 日次学習メニュー
        """
        now = datetime.now(UTC)
        # JSTに変換（UTC+9）
        jst_hour = (now.hour + 9) % 24

        if 5 <= jst_hour < 12:
            time_of_day = "morning"
        elif 12 <= jst_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= jst_hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        # ユーザー統計を取得
        user_stats = await self._get_user_summary(user_id, db)

        # 未復習アイテム数
        pending_result = await db.execute(
            select(func.count(ReviewItem.id)).where(
                ReviewItem.user_id == user_id,
                (ReviewItem.next_review_at <= now)
                | (ReviewItem.next_review_at.is_(None)),
            )
        )
        pending_reviews = pending_result.scalar() or 0

        system_prompt = build_daily_menu_prompt(
            time_of_day, user_stats, pending_reviews
        )

        messages = [
            {
                "role": "user",
                "content": "Generate my personalized learning menu for right now.",
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=2048,
                system=system_prompt,
            )

            activities = []
            for act in result.get("recommended_activities", []):
                activities.append(
                    ActivityItem(
                        activity_type=act.get("activity_type", "review"),
                        title=act.get("title", ""),
                        description=act.get("description", ""),
                        estimated_minutes=max(1, int(act.get("estimated_minutes", 5))),
                        priority=min(max(int(act.get("priority", 3)), 1), 5),
                        params=act.get("params", {}),
                    )
                )

            return DailyMenu(
                time_of_day=result.get("time_of_day", time_of_day),
                recommended_activities=activities,
                focus_message=result.get(
                    "focus_message", "Let's continue improving your English!"
                ),
                estimated_minutes=int(result.get("estimated_minutes", 15)),
            )

        except Exception as e:
            logger.error("日次メニュー生成エラー: %s", e)
            return self._build_fallback_menu(time_of_day, pending_reviews)

    async def get_focus_areas(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[FocusArea]:
        """
        ベイジアン知識モデルに基づくフォーカスエリアを取得

        各スキルについてBeta分布 P(知識あり) を計算し、
        目標レベルとのギャップが大きいものを優先的に返す。

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            FocusAreaのリスト（優先度順）
        """
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        stats_result = await db.execute(
            select(DailyStat)
            .where(
                DailyStat.user_id == user_id,
                DailyStat.date >= thirty_days_ago,
            )
            .order_by(DailyStat.date.asc())
        )
        stats = list(stats_result.scalars().all())

        # 音声パターン習熟度を取得
        pattern_result = await db.execute(
            select(SoundPatternMastery).where(SoundPatternMastery.user_id == user_id)
        )
        pattern_masteries = pattern_result.scalars().all()

        focus_areas = []

        for skill_key, skill_def in SKILL_DEFINITIONS.items():
            alpha = skill_def["alpha_init"]
            beta_param = skill_def["beta_init"]

            # データに基づいてBeta分布のパラメータを更新
            if skill_key == "grammar_accuracy":
                for s in stats:
                    if s.grammar_accuracy is not None:
                        alpha += s.grammar_accuracy * s.sessions_completed
                        beta_param += (1 - s.grammar_accuracy) * s.sessions_completed

            elif skill_key == "pronunciation":
                for s in stats:
                    if s.pronunciation_avg_score is not None:
                        alpha += s.pronunciation_avg_score * max(
                            1, s.sessions_completed
                        )
                        beta_param += (1 - s.pronunciation_avg_score) * max(
                            1, s.sessions_completed
                        )

            elif skill_key == "connected_speech":
                for pm in pattern_masteries:
                    alpha += pm.accuracy * pm.practice_count
                    beta_param += (1 - pm.accuracy) * pm.practice_count

            elif skill_key == "listening_comprehension":
                for s in stats:
                    if s.listening_speed_max is not None:
                        # 速度正規化: 1.5倍速を満点とする
                        normalized = min(s.listening_speed_max / 1.5, 1.0)
                        alpha += normalized * max(1, s.sessions_completed)
                        beta_param += (1 - normalized) * max(1, s.sessions_completed)

            elif skill_key == "vocabulary_range":
                for s in stats:
                    if s.new_expressions_learned > 0:
                        # 1日5語を目標とした相対スコア
                        score = min(s.new_expressions_learned / 5.0, 1.0)
                        alpha += score
                        beta_param += 1 - score

            elif skill_key == "fluency":
                for s in stats:
                    if s.avg_response_time_ms is not None:
                        # 3000ms以下を目標とした正規化
                        normalized = max(0, 1 - (s.avg_response_time_ms / 6000.0))
                        alpha += normalized * max(1, s.sessions_completed)
                        beta_param += (1 - normalized) * max(1, s.sessions_completed)

            # Beta分布のExpected value: E[X] = alpha / (alpha + beta)
            current_level = (
                alpha / (alpha + beta_param) if (alpha + beta_param) > 0 else 0.5
            )
            target = skill_def["target"]

            # ギャップに基づく優先度計算（ギャップが大きいほど優先度が高い）
            gap = max(0, target - current_level)
            if gap >= 0.3:
                priority = 1
            elif gap >= 0.2:
                priority = 2
            elif gap >= 0.1:
                priority = 3
            elif gap >= 0.05:
                priority = 4
            else:
                priority = 5

            focus_areas.append(
                FocusArea(
                    skill=skill_def["name"],
                    current_level=round(current_level, 3),
                    target_level=target,
                    priority=priority,
                    suggested_exercises=skill_def["exercise_types"],
                )
            )

        # 優先度順にソート（低い数値 = 高い優先度）
        focus_areas.sort(key=lambda fa: fa.priority)

        return focus_areas

    async def update_curriculum(
        self,
        user_id: UUID,
        session_result: dict,
        db: AsyncSession,
    ) -> None:
        """
        セッション結果に基づいてユーザーの学習モデルを更新

        日次統計テーブルの該当フィールドを更新する。
        新しいDailyStatレコードが存在しない場合は作成する。

        Args:
            user_id: ユーザーID
            session_result: セッション結果
                - session_type: str (flash_translation, conversation, etc.)
                - duration_minutes: int
                - grammar_accuracy: float | None
                - pronunciation_score: float | None
                - new_expressions: int
                - response_time_ms: int | None
                - weak_patterns: dict | None
            db: データベースセッション
        """
        today = date.today()

        # 今日のDailyStatを取得または作成
        result = await db.execute(
            select(DailyStat).where(
                DailyStat.user_id == user_id,
                DailyStat.date == today,
            )
        )
        daily_stat = result.scalar_one_or_none()

        if daily_stat is None:
            daily_stat = DailyStat(
                user_id=user_id,
                date=today,
                practice_minutes=0,
                sessions_completed=0,
                reviews_completed=0,
                new_expressions_learned=0,
            )
            db.add(daily_stat)

        # セッション結果を統計に反映
        duration = session_result.get("duration_minutes", 0)
        daily_stat.practice_minutes += duration
        daily_stat.sessions_completed += 1

        new_expr = session_result.get("new_expressions", 0)
        daily_stat.new_expressions_learned += new_expr

        # 文法精度: 加重平均で更新
        grammar = session_result.get("grammar_accuracy")
        if grammar is not None:
            if daily_stat.grammar_accuracy is not None:
                # 既存スコアとの加重平均
                total_sessions = daily_stat.sessions_completed
                daily_stat.grammar_accuracy = (
                    daily_stat.grammar_accuracy * (total_sessions - 1) + grammar
                ) / total_sessions
            else:
                daily_stat.grammar_accuracy = grammar

        # 発音スコア: 加重平均で更新
        pron_score = session_result.get("pronunciation_score")
        if pron_score is not None:
            if daily_stat.pronunciation_avg_score is not None:
                total_sessions = daily_stat.sessions_completed
                daily_stat.pronunciation_avg_score = (
                    daily_stat.pronunciation_avg_score * (total_sessions - 1)
                    + pron_score
                ) / total_sessions
            else:
                daily_stat.pronunciation_avg_score = pron_score

        # 応答速度: 最新値で更新
        response_time = session_result.get("response_time_ms")
        if response_time is not None:
            daily_stat.avg_response_time_ms = response_time

        # 弱点パターン: マージ
        weak_patterns = session_result.get("weak_patterns")
        if weak_patterns:
            existing = daily_stat.weak_patterns or {}
            existing.update(weak_patterns)
            daily_stat.weak_patterns = existing

        await db.commit()

    # --- プライベートヘルパーメソッド ---

    async def _get_user_summary(self, user_id: UUID, db: AsyncSession) -> dict:
        """ユーザーの学習統計サマリーを取得"""
        today = date.today()
        seven_days_ago = today - timedelta(days=7)

        result = await db.execute(
            select(
                func.coalesce(func.sum(DailyStat.practice_minutes), 0),
                func.coalesce(func.sum(DailyStat.sessions_completed), 0),
                func.avg(DailyStat.grammar_accuracy),
                func.avg(DailyStat.pronunciation_avg_score),
            ).where(
                DailyStat.user_id == user_id,
                DailyStat.date >= seven_days_ago,
            )
        )
        row = result.one()

        return {
            "total_minutes_last_7_days": int(row[0]),
            "total_sessions_last_7_days": int(row[1]),
            "avg_grammar_accuracy": round(float(row[2]), 2)
            if row[2] is not None
            else 0.0,
            "avg_pronunciation_score": round(float(row[3]), 2)
            if row[3] is not None
            else 0.0,
        }

    def _build_fallback_menu(
        self,
        time_of_day: str,
        pending_reviews: int,
    ) -> DailyMenu:
        """フォールバック: 時間帯ベースの静的メニュー"""
        menus = {
            "morning": {
                "activities": [
                    ActivityItem(
                        activity_type="flash_translation",
                        title="Morning Flash Translation",
                        description="Start your day with quick Japanese-to-English translation drills.",
                        estimated_minutes=10,
                        priority=1,
                        params={"count": 10, "focus": "accuracy"},
                    ),
                    ActivityItem(
                        activity_type="pronunciation",
                        title="Pronunciation Practice",
                        description="Work on challenging phonemes while your focus is sharp.",
                        estimated_minutes=5,
                        priority=2,
                        params={"phonemes": ["/r/-/l/", "/θ/-/s/"]},
                    ),
                ],
                "focus_message": "Good morning! Your brain is at peak performance. Let's tackle the challenging exercises first!",
                "estimated_minutes": 15,
            },
            "afternoon": {
                "activities": [
                    ActivityItem(
                        activity_type="conversation",
                        title="Conversation Practice",
                        description="Practice natural business conversation with AI.",
                        estimated_minutes=10,
                        priority=1,
                        params={"mode": "fluency"},
                    ),
                    ActivityItem(
                        activity_type="mogomogo",
                        title="Connected Speech Listening",
                        description="Train your ears to catch natural sound changes.",
                        estimated_minutes=5,
                        priority=2,
                        params={"pattern_types": ["linking", "reduction"]},
                    ),
                ],
                "focus_message": "Afternoon is perfect for communication-focused practice. Let's build fluency!",
                "estimated_minutes": 15,
            },
            "evening": {
                "activities": [
                    ActivityItem(
                        activity_type="comprehension",
                        title="Listening Comprehension",
                        description="Listen to a short business English passage and answer questions.",
                        estimated_minutes=10,
                        priority=2,
                        params={"difficulty": "intermediate"},
                    ),
                ],
                "focus_message": "Evening is great for consolidation. Let's review and integrate what you've learned!",
                "estimated_minutes": 15,
            },
            "night": {
                "activities": [
                    ActivityItem(
                        activity_type="comprehension",
                        title="Relaxed Listening",
                        description="Listen to English audio at a comfortable pace. No pressure!",
                        estimated_minutes=10,
                        priority=2,
                        params={"difficulty": "easy", "mode": "passive"},
                    ),
                ],
                "focus_message": "Wind down with some relaxed listening. Great for subconscious learning!",
                "estimated_minutes": 10,
            },
        }

        menu_data = menus.get(time_of_day, menus["morning"])
        activities = list(menu_data["activities"])

        # 未復習アイテムが多い場合は復習を追加
        if pending_reviews > 5:
            activities.insert(
                0,
                ActivityItem(
                    activity_type="review",
                    title="Spaced Repetition Review",
                    description=f"You have {pending_reviews} items waiting for review.",
                    estimated_minutes=5,
                    priority=1,
                    params={"pending_count": pending_reviews},
                ),
            )

        return DailyMenu(
            time_of_day=time_of_day,
            recommended_activities=activities,
            focus_message=menu_data["focus_message"],
            estimated_minutes=menu_data["estimated_minutes"],
        )


# シングルトンインスタンス
curriculum_service = CurriculumService()
