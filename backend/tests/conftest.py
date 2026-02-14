"""
FluentEdge テスト共通設定

テスト用DB、認証済みクライアント、LLMモックなどの共通フィクスチャを提供。
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base, get_db
from app.main import app

# テスト用DBのURL（テスト実行時はsqliteを使用）
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """セッション全体で共有するイベントループ"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """各テストの前にDBを初期化"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


# テスト用にDBセッションを差し替え
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """テスト用HTTPクライアント"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """テスト用DBセッション（直接利用）"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(setup_database, db_session):
    """テスト用ユーザーを作成（パスワードハッシュ付き）"""
    from passlib.context import CryptContext

    from app.models.user import User

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        hashed_password=pwd_context.hash("testpass123"),
        native_language="ja",
        target_level="B2",
        subscription_plan="free",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_client(client, test_user):
    """認証済みHTTPクライアント（JWTトークン付き）"""
    from app.routers.auth import create_access_token

    token = create_access_token(str(test_user.id))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def mock_claude():
    """ClaudeServiceのモック - chat/chat_json/get_usage_info をモック化"""
    with patch("app.services.claude_service.claude_service") as mock:
        mock.chat = AsyncMock(return_value="Mock AI response")
        mock.chat_json = AsyncMock(
            return_value={
                "grammar_errors": [],
                "expression_upgrades": [],
                "pronunciation_notes": [],
                "positive_feedback": "Great job!",
                "vocabulary_level": "B2",
            }
        )
        mock.get_usage_info = AsyncMock(
            return_value={
                "text": "Mock response",
                "input_tokens": 100,
                "output_tokens": 50,
                "model": "mock-model",
            }
        )
        yield mock


@pytest.fixture
def mock_stripe():
    """StripeServiceのモック"""
    with patch("app.services.stripe_service.stripe_service") as mock:
        mock.get_plans = MagicMock(return_value=[])
        mock.get_subscription = AsyncMock(
            return_value=MagicMock(
                plan="free",
                status="active",
                current_period_start=None,
                current_period_end=None,
                cancel_at_period_end=False,
                stripe_customer_id=None,
            )
        )
        mock.create_checkout_session = AsyncMock(
            return_value=MagicMock(
                checkout_url="https://checkout.stripe.com/test",
                session_id="cs_test_123",
            )
        )
        mock.handle_webhook = AsyncMock(
            return_value={"event_type": "checkout.session.completed", "status": "processed"}
        )
        yield mock


@pytest.fixture
def mock_speech():
    """SpeechServiceのモック"""
    with patch("app.services.shadowing_service.speech_service") as mock:
        mock.text_to_speech = AsyncMock(return_value=b"fake-audio-bytes")
        mock.assess_pronunciation = AsyncMock(
            return_value=MagicMock(
                accuracy_score=85.0,
                fluency_score=80.0,
                prosody_score=75.0,
                completeness_score=90.0,
                word_scores=[],
            )
        )
        yield mock
