"""モデルのテスト - User, DailyStat, ReviewItem作成"""

import uuid
from datetime import date, datetime, timezone

import pytest
import pytest_asyncio

from app.models.user import User
from app.models.stats import DailyStat
from app.models.review import ReviewItem
from app.models.conversation import ConversationSession, ConversationMessage


class TestUserModel:
    """Userモデルのテスト"""

    @pytest.mark.asyncio
    async def test_user_creation(self, db_session):
        """ユーザーモデルの作成と読み取り"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        user = User(
            id=uuid.uuid4(),
            email="newuser@example.com",
            name="New User",
            hashed_password=pwd_context.hash("password123"),
            native_language="ja",
            target_level="C1",
            subscription_plan="free",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.native_language == "ja"
        assert user.target_level == "C1"
        assert user.subscription_plan == "free"
        assert user.daily_goal_minutes == 15  # デフォルト値
        assert user.api_usage_monthly == 0
        assert repr(user) == "<User newuser@example.com>"

    @pytest.mark.asyncio
    async def test_user_default_values(self, db_session):
        """ユーザーのデフォルト値が正しい"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        user = User(
            id=uuid.uuid4(),
            email="default@example.com",
            name="Default User",
            hashed_password=pwd_context.hash("pass"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # デフォルト値の確認
        assert user.native_language == "ja"
        assert user.target_level == "C1"
        assert user.daily_goal_minutes == 15
        assert user.subscription_plan == "free"
        assert user.api_usage_monthly == 0


class TestDailyStatModel:
    """DailyStatモデルのテスト"""

    @pytest.mark.asyncio
    async def test_daily_stat_creation(self, db_session, test_user):
        """日次統計の作成"""
        stat = DailyStat(
            user_id=test_user.id,
            date=date.today(),
            practice_minutes=25,
            sessions_completed=3,
            reviews_completed=15,
            new_expressions_learned=8,
            grammar_accuracy=0.87,
            pronunciation_avg_score=0.75,
        )
        db_session.add(stat)
        await db_session.commit()
        await db_session.refresh(stat)

        assert stat.user_id == test_user.id
        assert stat.date == date.today()
        assert stat.practice_minutes == 25
        assert stat.sessions_completed == 3
        assert stat.reviews_completed == 15
        assert stat.new_expressions_learned == 8
        assert stat.grammar_accuracy == 0.87
        assert stat.pronunciation_avg_score == 0.75
        assert repr(stat).startswith("<DailyStat")

    @pytest.mark.asyncio
    async def test_daily_stat_default_values(self, db_session, test_user):
        """日次統計のデフォルト値"""
        stat = DailyStat(
            user_id=test_user.id,
            date=date.today(),
        )
        db_session.add(stat)
        await db_session.commit()
        await db_session.refresh(stat)

        assert stat.practice_minutes == 0
        assert stat.sessions_completed == 0
        assert stat.reviews_completed == 0
        assert stat.new_expressions_learned == 0
        assert stat.grammar_accuracy is None
        assert stat.pronunciation_avg_score is None
        assert stat.weak_patterns is None

    @pytest.mark.asyncio
    async def test_daily_stat_with_weak_patterns(self, db_session, test_user):
        """弱点パターンJSON付きの日次統計"""
        stat = DailyStat(
            user_id=test_user.id,
            date=date.today(),
            practice_minutes=10,
            weak_patterns={"conditionals": 0.5, "passive_voice": 0.6},
        )
        db_session.add(stat)
        await db_session.commit()
        await db_session.refresh(stat)

        assert stat.weak_patterns is not None
        assert stat.weak_patterns["conditionals"] == 0.5


class TestReviewItemModel:
    """ReviewItemモデルのテスト"""

    @pytest.mark.asyncio
    async def test_review_item_creation(self, db_session, test_user):
        """復習アイテムの作成"""
        item = ReviewItem(
            user_id=test_user.id,
            item_type="flash_translation",
            content={
                "target": "Let's discuss the agenda.",
                "user_answer": "Let's talk about agenda.",
            },
            next_review_at=datetime.now(timezone.utc),
        )
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)

        assert item.user_id == test_user.id
        assert item.item_type == "flash_translation"
        assert item.content["target"] == "Let's discuss the agenda."
        assert item.ease_factor == 2.5  # デフォルト
        assert item.interval_days == 0  # デフォルト
        assert item.repetitions == 0  # デフォルト
        assert item.stability == 1.0  # FSRSデフォルト
        assert item.difficulty == 0.3  # FSRSデフォルト
        assert repr(item).startswith("<ReviewItem")


class TestConversationModels:
    """ConversationSession/Messageモデルのテスト"""

    @pytest.mark.asyncio
    async def test_conversation_session_creation(self, db_session, test_user):
        """会話セッションの作成"""
        session = ConversationSession(
            user_id=test_user.id,
            mode="meeting",
            scenario_description="Weekly standup",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.user_id == test_user.id
        assert session.mode == "meeting"
        assert session.scenario_description == "Weekly standup"
        assert session.ended_at is None
        assert session.duration_seconds is None
        assert repr(session).startswith("<ConversationSession")

    @pytest.mark.asyncio
    async def test_conversation_message_creation(self, db_session, test_user):
        """会話メッセージの作成"""
        session = ConversationSession(
            user_id=test_user.id,
            mode="small_talk",
        )
        db_session.add(session)
        await db_session.flush()

        message = ConversationMessage(
            session_id=session.id,
            role="assistant",
            content="Hello! How can I help you today?",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        assert message.session_id == session.id
        assert message.role == "assistant"
        assert message.content == "Hello! How can I help you today?"
        assert message.feedback is None
        assert message.pronunciation_score is None
        assert repr(message).startswith("<ConversationMessage")
