"""アナリティクスサービス - 包括的な学習分析

週次・月次レポート、スキル分析、発音進捗追跡、AI推奨事項の生成を行う。
ユーザーの学習データを多角的に分析し、パーソナライズされたフィードバックを提供。
"""

import logging
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stats import DailyStat
from app.models.review import ReviewItem
from app.models.conversation import ConversationSession
from app.models.sound_pattern import SoundPatternMastery
from app.schemas.analytics import (
    WeeklyReport,
    MonthlyReport,
    SkillBreakdown,
    PronunciationProgress,
    Recommendation,
    DailyBreakdown,
    Achievement,
    PhonemeTrend,
    SpeakingSkill,
    SpeakingResponseTime,
    SpeakingFillerWords,
    SpeakingGrammar,
    SpeakingExpressionLevel,
    ListeningSkill,
    ListeningComprehensionBySpeed,
    ListeningWeakPatterns,
    ListeningDictationAccuracy,
    VocabularySkill,
    VocabularyRange,
    VocabularySophistication,
    VocabularyNewPerWeek,
)
from app.services.claude_service import claude_service
from app.prompts.analytics import build_recommendation_prompt

logger = logging.getLogger(__name__)


class AnalyticsService:
    """包括的な学習分析サービス"""

    async def get_weekly_report(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> WeeklyReport:
        """
        週次学習レポートを生成

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            WeeklyReport: 週次レポート
        """
        today = date.today()
        # 今週の月曜日を起点
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # 今週の日次統計を取得
        current_stats = await self._get_daily_stats(user_id, week_start, week_end, db)

        # 前週の統計を取得（比較用）
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(days=1)
        prev_stats = await self._get_daily_stats(user_id, prev_week_start, prev_week_end, db)

        # 今週の集計
        total_minutes = sum(s.practice_minutes for s in current_stats)
        total_sessions = sum(s.sessions_completed for s in current_stats)
        total_reviews = sum(s.reviews_completed for s in current_stats)
        new_expressions = sum(s.new_expressions_learned for s in current_stats)

        grammar_scores = [s.grammar_accuracy for s in current_stats if s.grammar_accuracy is not None]
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else None

        pron_scores = [s.pronunciation_avg_score for s in current_stats if s.pronunciation_avg_score is not None]
        avg_pronunciation = sum(pron_scores) / len(pron_scores) if pron_scores else None

        # ストリーク計算
        streak_days = await self._calculate_streak(user_id, db)

        # 日別詳細
        daily_breakdown = [
            DailyBreakdown(
                date=s.date,
                practice_minutes=s.practice_minutes,
                sessions_completed=s.sessions_completed,
                reviews_completed=s.reviews_completed,
                new_expressions_learned=s.new_expressions_learned,
                grammar_accuracy=s.grammar_accuracy,
                pronunciation_avg_score=s.pronunciation_avg_score,
            )
            for s in current_stats
        ]

        # 前週比較
        prev_minutes = sum(s.practice_minutes for s in prev_stats)
        prev_grammar = [s.grammar_accuracy for s in prev_stats if s.grammar_accuracy is not None]
        prev_avg_grammar = sum(prev_grammar) / len(prev_grammar) if prev_grammar else None

        improvement = {}
        if prev_minutes > 0:
            improvement["minutes"] = round(
                ((total_minutes - prev_minutes) / prev_minutes) * 100, 1
            )
        if prev_avg_grammar is not None and avg_grammar is not None and prev_avg_grammar > 0:
            improvement["grammar_accuracy"] = round(
                ((avg_grammar - prev_avg_grammar) / prev_avg_grammar) * 100, 1
            )

        return WeeklyReport(
            period_start=week_start,
            period_end=week_end,
            total_minutes=total_minutes,
            total_sessions=total_sessions,
            total_reviews=total_reviews,
            new_expressions=new_expressions,
            avg_grammar_accuracy=round(avg_grammar, 3) if avg_grammar is not None else None,
            avg_pronunciation=round(avg_pronunciation, 3) if avg_pronunciation is not None else None,
            streak_days=streak_days,
            daily_breakdown=daily_breakdown,
            improvement_vs_last_week=improvement,
        )

    async def get_monthly_report(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> MonthlyReport:
        """
        月次学習レポートを生成

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            MonthlyReport: 月次レポート
        """
        today = date.today()
        month_start = today.replace(day=1)
        # 翌月初日の前日を月末とする
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

        stats = await self._get_daily_stats(user_id, month_start, month_end, db)

        total_minutes = sum(s.practice_minutes for s in stats)
        total_sessions = sum(s.sessions_completed for s in stats)
        total_reviews = sum(s.reviews_completed for s in stats)
        new_expressions = sum(s.new_expressions_learned for s in stats)

        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else None

        pron_scores = [s.pronunciation_avg_score for s in stats if s.pronunciation_avg_score is not None]
        avg_pronunciation = sum(pron_scores) / len(pron_scores) if pron_scores else None

        # 月内最長ストリーク
        streak_best = self._calculate_best_streak_in_range(stats)

        # 週ごとのトレンドデータ
        weekly_trend = self._build_weekly_trend(stats, month_start)

        # スキルレーダーデータ
        skill_radar = await self._build_skill_radar(user_id, db)

        # アチーブメント判定
        achievements = self._evaluate_achievements(stats, total_minutes, total_sessions)

        # 強み・弱みの分析
        strengths, weaknesses = self._analyze_strengths_weaknesses(stats)

        # 推奨事項
        recommendations_text = []
        if weaknesses:
            recommendations_text.append(f"Focus on improving: {', '.join(weaknesses[:2])}")
        if total_minutes < 300:
            recommendations_text.append("Try to increase daily practice time to reach 10 minutes/day")
        if avg_grammar is not None and avg_grammar < 0.7:
            recommendations_text.append("Consider more grammar-focused exercises")

        return MonthlyReport(
            period_start=month_start,
            period_end=month_end,
            total_minutes=total_minutes,
            total_sessions=total_sessions,
            total_reviews=total_reviews,
            new_expressions=new_expressions,
            avg_grammar_accuracy=round(avg_grammar, 3) if avg_grammar is not None else None,
            avg_pronunciation=round(avg_pronunciation, 3) if avg_pronunciation is not None else None,
            streak_best=streak_best,
            monthly_trend_chart_data=weekly_trend,
            skill_radar_data=skill_radar,
            top_achievements=achievements,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations_text,
        )

    async def get_skill_breakdown(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> SkillBreakdown:
        """
        スキル分類別の詳細分析を取得

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            SkillBreakdown: スキル分析結果
        """
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        stats = await self._get_daily_stats(user_id, thirty_days_ago, today, db)

        # --- スピーキング ---
        response_times = [s.avg_response_time_ms for s in stats if s.avg_response_time_ms is not None]
        avg_response = int(sum(response_times) / len(response_times)) if response_times else 0

        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0.0

        # 応答速度のトレンド判定
        response_trend = "stable"
        if len(response_times) >= 7:
            recent = sum(response_times[-3:]) / 3
            older = sum(response_times[:3]) / 3
            if recent < older * 0.9:
                response_trend = "improving"
            elif recent > older * 1.1:
                response_trend = "declining"

        # 文法の弱点パターンを集約
        weak_grammar_patterns = []
        for s in stats:
            if s.weak_patterns and isinstance(s.weak_patterns, dict):
                for pattern, score in s.weak_patterns.items():
                    if isinstance(score, (int, float)) and score < 0.7:
                        if pattern not in weak_grammar_patterns:
                            weak_grammar_patterns.append(pattern)

        speaking = SpeakingSkill(
            response_time=SpeakingResponseTime(
                avg_ms=avg_response,
                trend=response_trend,
                target_ms=3000,
            ),
            filler_words=SpeakingFillerWords(
                avg_per_minute=0.0,
                common_fillers=[],
                trend="stable",
            ),
            grammar=SpeakingGrammar(
                accuracy=round(avg_grammar, 3),
                weak_patterns=weak_grammar_patterns[:5],
                trend="stable",
            ),
            expression_level=SpeakingExpressionLevel(
                current_level="B2",
                sophistication_score=0.0,
                recently_mastered=[],
            ),
        )

        # --- リスニング ---
        # 音声パターン習熟度を取得
        pattern_result = await db.execute(
            select(SoundPatternMastery)
            .where(SoundPatternMastery.user_id == user_id)
        )
        pattern_masteries = pattern_result.scalars().all()

        listening_weak_patterns = [
            ListeningWeakPatterns(
                pattern_type=pm.pattern_type,
                pattern_name=pm.pattern_type.replace("_", " ").title(),
                accuracy=pm.accuracy,
                practice_count=pm.practice_count,
            )
            for pm in pattern_masteries
            if pm.accuracy < 0.7
        ]

        listening_speed_scores = [s.listening_speed_max for s in stats if s.listening_speed_max is not None]
        max_speed = max(listening_speed_scores) if listening_speed_scores else 1.0

        listening = ListeningSkill(
            comprehension_by_speed=ListeningComprehensionBySpeed(
                slow=min(1.0, max_speed / 0.75) if max_speed else 0.0,
                normal=min(1.0, max_speed / 1.0) if max_speed else 0.0,
                fast=min(1.0, max_speed / 1.25) if max_speed else 0.0,
                native=min(1.0, max_speed / 1.5) if max_speed else 0.0,
            ),
            weak_patterns=listening_weak_patterns,
            dictation_accuracy=ListeningDictationAccuracy(
                overall_accuracy=0.0,
                by_pattern={},
            ),
        )

        # --- 語彙 ---
        # 復習アイテムから語彙統計を計算
        vocab_result = await db.execute(
            select(func.count(ReviewItem.id))
            .where(
                ReviewItem.user_id == user_id,
                ReviewItem.item_type.in_(["vocabulary", "expression", "flash_translation"]),
            )
        )
        total_vocab = vocab_result.scalar() or 0

        recent_vocab_result = await db.execute(
            select(func.count(ReviewItem.id))
            .where(
                ReviewItem.user_id == user_id,
                ReviewItem.item_type.in_(["vocabulary", "expression", "flash_translation"]),
                ReviewItem.created_at >= datetime.now(timezone.utc) - timedelta(days=7),
            )
        )
        new_this_week = recent_vocab_result.scalar() or 0

        vocabulary = VocabularySkill(
            range=VocabularyRange(
                total_words=total_vocab,
                active_words=int(total_vocab * 0.6),
                passive_words=int(total_vocab * 0.4),
            ),
            sophistication=VocabularySophistication(
                level="intermediate",
                score=0.5,
                advanced_word_ratio=0.0,
            ),
            new_per_week=VocabularyNewPerWeek(
                current_week=new_this_week,
                avg_last_4_weeks=new_this_week / 4.0,
                target=20,
            ),
        )

        return SkillBreakdown(
            speaking=speaking,
            listening=listening,
            vocabulary=vocabulary,
        )

    async def get_pronunciation_progress(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> PronunciationProgress:
        """
        発音進捗データを取得

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            PronunciationProgress: 発音進捗
        """
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        # 日次統計から発音スコアのトレンドを構築
        stats = await self._get_daily_stats(user_id, thirty_days_ago, today, db)

        overall_trend = [
            PhonemeTrend(date=s.date, score=s.pronunciation_avg_score)
            for s in stats
            if s.pronunciation_avg_score is not None
        ]

        # 音声パターン習熟度から音素別スコアを取得
        pattern_result = await db.execute(
            select(SoundPatternMastery)
            .where(SoundPatternMastery.user_id == user_id)
        )
        pattern_masteries = pattern_result.scalars().all()

        phoneme_scores = {}
        weak_phonemes = []
        for pm in pattern_masteries:
            phoneme_scores[pm.pattern_type] = round(pm.accuracy, 3)
            if pm.accuracy < 0.6:
                weak_phonemes.append(pm.pattern_type)

        return PronunciationProgress(
            overall_trend=overall_trend,
            phoneme_scores=phoneme_scores,
            weak_phonemes=weak_phonemes,
        )

    async def get_learning_recommendations(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[Recommendation]:
        """
        AI生成の学習推奨事項を取得

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            Recommendationのリスト
        """
        today = date.today()
        seven_days_ago = today - timedelta(days=7)

        stats = await self._get_daily_stats(user_id, seven_days_ago, today, db)

        # ユーザー統計のサマリーを構築
        total_minutes = sum(s.practice_minutes for s in stats)
        total_sessions = sum(s.sessions_completed for s in stats)
        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0.0
        pron_scores = [s.pronunciation_avg_score for s in stats if s.pronunciation_avg_score is not None]
        avg_pron = sum(pron_scores) / len(pron_scores) if pron_scores else 0.0

        user_stats = {
            "total_practice_minutes_last_7_days": total_minutes,
            "total_sessions_last_7_days": total_sessions,
            "avg_grammar_accuracy": round(avg_grammar, 2),
            "avg_pronunciation_score": round(avg_pron, 2),
            "days_with_practice": len([s for s in stats if s.practice_minutes > 0]),
        }

        # 弱点分野の特定
        weak_areas = []
        if avg_grammar < 0.7:
            weak_areas.append("grammar accuracy (below 70%)")
        if avg_pron < 0.6:
            weak_areas.append("pronunciation (below 60%)")
        if total_minutes < 70:
            weak_areas.append("practice consistency (less than 10 min/day)")
        if total_sessions < 5:
            weak_areas.append("session frequency (fewer than 5 sessions/week)")

        # 音声パターンの弱点
        pattern_result = await db.execute(
            select(SoundPatternMastery)
            .where(
                SoundPatternMastery.user_id == user_id,
                SoundPatternMastery.accuracy < 0.6,
            )
        )
        weak_patterns = pattern_result.scalars().all()
        for wp in weak_patterns:
            weak_areas.append(f"sound pattern: {wp.pattern_type} ({wp.accuracy:.0%} accuracy)")

        system_prompt = build_recommendation_prompt(user_stats, weak_areas)

        messages = [
            {
                "role": "user",
                "content": "Generate personalized learning recommendations based on my stats.",
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=2048,
                system=system_prompt,
            )

            recommendations_data = result if isinstance(result, list) else result.get("recommendations", [])

            recommendations = []
            for item in recommendations_data:
                recommendations.append(
                    Recommendation(
                        category=item.get("category", "speaking"),
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        priority=min(max(int(item.get("priority", 3)), 1), 5),
                        suggested_exercise_type=item.get("suggested_exercise_type", "conversation"),
                    )
                )

            return sorted(recommendations, key=lambda r: r.priority)

        except Exception as e:
            logger.error("推奨事項生成エラー: %s", e)
            # フォールバック推奨事項
            return self._build_fallback_recommendations(user_stats, weak_areas)

    # --- プライベートヘルパーメソッド ---

    async def _get_daily_stats(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        db: AsyncSession,
    ) -> list[DailyStat]:
        """指定期間の日次統計を取得"""
        result = await db.execute(
            select(DailyStat)
            .where(
                DailyStat.user_id == user_id,
                DailyStat.date >= start_date,
                DailyStat.date <= end_date,
            )
            .order_by(DailyStat.date.asc())
        )
        return list(result.scalars().all())

    async def _calculate_streak(self, user_id: UUID, db: AsyncSession) -> int:
        """連続学習日数を計算"""
        today = date.today()
        result = await db.execute(
            select(DailyStat)
            .where(
                DailyStat.user_id == user_id,
                DailyStat.date >= today - timedelta(days=90),
                DailyStat.practice_minutes > 0,
            )
            .order_by(DailyStat.date.desc())
        )
        stats = result.scalars().all()
        stats_dates = {s.date for s in stats}

        streak = 0
        check = today
        while check in stats_dates:
            streak += 1
            check -= timedelta(days=1)

        if streak == 0:
            check = today - timedelta(days=1)
            while check in stats_dates:
                streak += 1
                check -= timedelta(days=1)

        return streak

    def _calculate_best_streak_in_range(self, stats: list[DailyStat]) -> int:
        """期間内の最長ストリークを計算"""
        active_dates = sorted(s.date for s in stats if s.practice_minutes > 0)
        if not active_dates:
            return 0

        best = 1
        current = 1
        for i in range(1, len(active_dates)):
            if active_dates[i] - active_dates[i - 1] == timedelta(days=1):
                current += 1
                best = max(best, current)
            else:
                current = 1

        return best

    def _build_weekly_trend(
        self,
        stats: list[DailyStat],
        month_start: date,
    ) -> list[dict]:
        """月内の週ごとトレンドデータを構築"""
        weeks: list[dict] = []
        current = month_start
        week_num = 1

        while current.month == month_start.month:
            week_end = current + timedelta(days=6)
            week_stats = [s for s in stats if current <= s.date <= week_end]

            weeks.append({
                "week": week_num,
                "minutes": sum(s.practice_minutes for s in week_stats),
                "sessions": sum(s.sessions_completed for s in week_stats),
                "reviews": sum(s.reviews_completed for s in week_stats),
            })

            current = week_end + timedelta(days=1)
            week_num += 1

        return weeks

    async def _build_skill_radar(self, user_id: UUID, db: AsyncSession) -> dict:
        """スキルレーダーチャートデータを構築"""
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)

        stats = await self._get_daily_stats(user_id, thirty_days_ago, today, db)

        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        pron_scores = [s.pronunciation_avg_score for s in stats if s.pronunciation_avg_score is not None]

        return {
            "speaking": round(sum(grammar_scores) / len(grammar_scores), 2) if grammar_scores else 0.0,
            "listening": 0.5,
            "vocabulary": 0.5,
            "grammar": round(sum(grammar_scores) / len(grammar_scores), 2) if grammar_scores else 0.0,
            "pronunciation": round(sum(pron_scores) / len(pron_scores), 2) if pron_scores else 0.0,
        }

    def _evaluate_achievements(
        self,
        stats: list[DailyStat],
        total_minutes: int,
        total_sessions: int,
    ) -> list[Achievement]:
        """月間アチーブメントを評価"""
        achievements = []

        if total_minutes >= 600:
            achievements.append(Achievement(
                title="Marathon Learner",
                description="10 hours of practice this month!",
                icon="fire",
            ))
        elif total_minutes >= 300:
            achievements.append(Achievement(
                title="Dedicated Student",
                description="5 hours of practice this month!",
                icon="star",
            ))

        if total_sessions >= 30:
            achievements.append(Achievement(
                title="Daily Practitioner",
                description="30 sessions completed this month!",
                icon="calendar",
            ))

        streak = self._calculate_best_streak_in_range(stats)
        if streak >= 14:
            achievements.append(Achievement(
                title="Two-Week Streak",
                description="14 consecutive days of practice!",
                icon="trophy",
            ))
        elif streak >= 7:
            achievements.append(Achievement(
                title="Week Warrior",
                description="7 consecutive days of practice!",
                icon="medal",
            ))

        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        if grammar_scores and max(grammar_scores) >= 0.95:
            achievements.append(Achievement(
                title="Grammar Master",
                description="Achieved 95%+ grammar accuracy!",
                icon="brain",
            ))

        return achievements

    def _analyze_strengths_weaknesses(
        self,
        stats: list[DailyStat],
    ) -> tuple[list[str], list[str]]:
        """強み・弱みを分析"""
        strengths = []
        weaknesses = []

        grammar_scores = [s.grammar_accuracy for s in stats if s.grammar_accuracy is not None]
        pron_scores = [s.pronunciation_avg_score for s in stats if s.pronunciation_avg_score is not None]

        if grammar_scores:
            avg_grammar = sum(grammar_scores) / len(grammar_scores)
            if avg_grammar >= 0.8:
                strengths.append("Grammar accuracy")
            elif avg_grammar < 0.6:
                weaknesses.append("Grammar accuracy")

        if pron_scores:
            avg_pron = sum(pron_scores) / len(pron_scores)
            if avg_pron >= 0.8:
                strengths.append("Pronunciation")
            elif avg_pron < 0.6:
                weaknesses.append("Pronunciation")

        active_days = len([s for s in stats if s.practice_minutes > 0])
        total_days = max(len(stats), 1)
        if active_days / total_days >= 0.7:
            strengths.append("Practice consistency")
        elif active_days / total_days < 0.3:
            weaknesses.append("Practice consistency")

        return strengths, weaknesses

    def _build_fallback_recommendations(
        self,
        user_stats: dict,
        weak_areas: list[str],
    ) -> list[Recommendation]:
        """フォールバック推奨事項"""
        recommendations = []

        if user_stats.get("avg_grammar_accuracy", 1.0) < 0.7:
            recommendations.append(Recommendation(
                category="grammar",
                title="Strengthen Grammar Patterns",
                description="Your grammar accuracy is below target. Try focused flash translation exercises with grammar patterns you find challenging.",
                priority=1,
                suggested_exercise_type="flash_translation",
            ))

        if user_stats.get("avg_pronunciation_score", 1.0) < 0.6:
            recommendations.append(Recommendation(
                category="pronunciation",
                title="Improve Pronunciation Accuracy",
                description="Work on pronunciation exercises focusing on phonemes that are challenging for Japanese speakers.",
                priority=2,
                suggested_exercise_type="pronunciation",
            ))

        if user_stats.get("total_practice_minutes_last_7_days", 0) < 70:
            recommendations.append(Recommendation(
                category="speaking",
                title="Increase Daily Practice",
                description="Try to maintain at least 10 minutes of practice per day for optimal progress.",
                priority=2,
                suggested_exercise_type="conversation",
            ))

        recommendations.append(Recommendation(
            category="listening",
            title="Connected Speech Practice",
            description="Practice recognizing natural sound changes in English to improve listening comprehension.",
            priority=3,
            suggested_exercise_type="mogomogo",
        ))

        return recommendations


# シングルトンインスタンス
analytics_service = AnalyticsService()
