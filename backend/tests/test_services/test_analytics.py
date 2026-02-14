"""アナリティクスサービスのテスト - 学習統計分析"""

import uuid
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """AnalyticsServiceのテスト"""

    @pytest.mark.asyncio
    async def test_get_weekly_report(self, db_session, test_user):
        """週次レポートの生成（データなし時のゼロ値レポート）"""
        service = AnalyticsService()

        report = await service.get_weekly_report(
            user_id=test_user.id,
            db=db_session,
        )

        # データがないので全てゼロ
        assert report.total_minutes == 0
        assert report.total_sessions == 0
        assert report.total_reviews == 0
        assert report.new_expressions == 0
        assert report.streak_days == 0
        assert report.daily_breakdown == []

    @pytest.mark.asyncio
    async def test_get_weekly_report_with_data(self, db_session, test_user):
        """統計データがある場合の週次レポート"""
        from app.models.stats import DailyStat

        service = AnalyticsService()
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # テスト用の日次統計を作成
        stat = DailyStat(
            user_id=test_user.id,
            date=week_start,
            practice_minutes=30,
            sessions_completed=3,
            reviews_completed=10,
            new_expressions_learned=5,
            grammar_accuracy=0.85,
            pronunciation_avg_score=0.78,
        )
        db_session.add(stat)
        await db_session.commit()

        report = await service.get_weekly_report(
            user_id=test_user.id,
            db=db_session,
        )

        assert report.total_minutes == 30
        assert report.total_sessions == 3
        assert report.total_reviews == 10
        assert report.new_expressions == 5
        assert len(report.daily_breakdown) == 1

    @pytest.mark.asyncio
    async def test_get_monthly_report(self, db_session, test_user):
        """月次レポートの生成"""
        service = AnalyticsService()

        report = await service.get_monthly_report(
            user_id=test_user.id,
            db=db_session,
        )

        assert report.total_minutes == 0
        assert report.total_sessions == 0
        assert report.period_start.day == 1  # 月初

    @pytest.mark.asyncio
    async def test_get_skill_breakdown(self, db_session, test_user):
        """スキル分析の取得"""
        service = AnalyticsService()

        breakdown = await service.get_skill_breakdown(
            user_id=test_user.id,
            db=db_session,
        )

        # 各スキルカテゴリが存在する
        assert breakdown.speaking is not None
        assert breakdown.listening is not None
        assert breakdown.vocabulary is not None

    @pytest.mark.asyncio
    async def test_get_pronunciation_progress(self, db_session, test_user):
        """発音進捗データの取得"""
        service = AnalyticsService()

        progress = await service.get_pronunciation_progress(
            user_id=test_user.id,
            db=db_session,
        )

        assert progress.overall_trend == []  # データなし
        assert progress.phoneme_scores == {}
        assert progress.weak_phonemes == []

    @pytest.mark.asyncio
    async def test_get_learning_recommendations(self, db_session, test_user):
        """学習推奨事項の取得（モック使用）"""
        service = AnalyticsService()

        mock_response = {
            "recommendations": [
                {
                    "category": "speaking",
                    "title": "Practice Daily Conversations",
                    "description": "Engage in 10-minute conversation sessions daily.",
                    "priority": 1,
                    "suggested_exercise_type": "conversation",
                },
                {
                    "category": "grammar",
                    "title": "Review Conditional Sentences",
                    "description": "Focus on if-clauses for business scenarios.",
                    "priority": 2,
                    "suggested_exercise_type": "flash_translation",
                },
            ]
        }

        with patch("app.services.analytics_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            recommendations = await service.get_learning_recommendations(
                user_id=test_user.id,
                db=db_session,
            )

            assert len(recommendations) == 2
            # priority順にソートされている
            assert recommendations[0].priority <= recommendations[1].priority
            assert recommendations[0].category == "speaking"

    @pytest.mark.asyncio
    async def test_get_learning_recommendations_fallback(self, db_session, test_user):
        """推奨事項取得のエラー時にフォールバックが返される"""
        service = AnalyticsService()

        with patch("app.services.analytics_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            recommendations = await service.get_learning_recommendations(
                user_id=test_user.id,
                db=db_session,
            )

            # フォールバック推奨事項が返される
            assert len(recommendations) >= 1
            assert all(hasattr(r, "category") for r in recommendations)

    def test_calculate_best_streak_in_range(self):
        """最長ストリーク計算"""
        service = AnalyticsService()

        # 空リスト
        assert service._calculate_best_streak_in_range([]) == 0

        # 3日間のストリーク
        today = date.today()
        stats = []
        for i in range(3):
            stat = MagicMock()
            stat.date = today - timedelta(days=i)
            stat.practice_minutes = 10
            stats.append(stat)

        result = service._calculate_best_streak_in_range(stats)
        assert result == 3
