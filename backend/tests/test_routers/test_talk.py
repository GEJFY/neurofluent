"""Talk(会話練習)ルーターのテスト - セッション開始・メッセージ送信"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio


class TestTalkRouter:
    """Talkルーターのテスト"""

    @pytest.mark.asyncio
    async def test_start_session(self, auth_client, mock_claude):
        """認証済みユーザーで会話セッションを開始できる"""
        response = await auth_client.post(
            "/api/talk/start",
            json={
                "mode": "meeting",
                "scenario_description": "Weekly team standup",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "meeting"
        assert data["scenario_description"] == "Weekly team standup"
        assert len(data["messages"]) == 1
        assert data["messages"][0]["role"] == "assistant"
        # mock_claudeのchat応答が使われる
        assert data["messages"][0]["content"] == "Mock AI response"

    @pytest.mark.asyncio
    async def test_send_message(self, auth_client, mock_claude, db_session, test_user):
        """メッセージ送信でAI応答とフィードバックが返される"""
        # まずセッションを開始
        start_response = await auth_client.post(
            "/api/talk/start",
            json={"mode": "small_talk"},
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["id"]

        # feedback_serviceもモック
        with patch("app.routers.talk.feedback_service") as mock_feedback:
            from app.schemas.talk import FeedbackData

            mock_feedback.generate_feedback = AsyncMock(
                return_value=FeedbackData(
                    grammar_errors=[],
                    expression_upgrades=[],
                    pronunciation_notes=[],
                    positive_feedback="Good job!",
                    vocabulary_level="B2",
                )
            )

            response = await auth_client.post(
                "/api/talk/message",
                json={
                    "session_id": session_id,
                    "content": "I want to discuss the new project timeline.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "assistant"
            assert data["content"] == "Mock AI response"
            assert data["feedback"]["positive_feedback"] == "Good job!"

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401エラーになる"""
        response = await client.post(
            "/api/talk/start",
            json={"mode": "meeting"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_sessions(self, auth_client, mock_claude):
        """セッション一覧の取得"""
        # セッション作成
        await auth_client.post(
            "/api/talk/start",
            json={"mode": "presentation"},
        )

        response = await auth_client.get("/api/talk/sessions")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["mode"] == "presentation"

    @pytest.mark.asyncio
    async def test_get_session_detail(self, auth_client, mock_claude):
        """セッション詳細の取得"""
        # セッション作成
        start_resp = await auth_client.post(
            "/api/talk/start",
            json={"mode": "negotiation"},
        )
        session_id = start_resp.json()["id"]

        response = await auth_client.get(f"/api/talk/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["mode"] == "negotiation"
        assert len(data["messages"]) >= 1

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, auth_client):
        """存在しないセッションIDで404エラー"""
        fake_id = str(uuid.uuid4())
        response = await auth_client.get(f"/api/talk/sessions/{fake_id}")

        assert response.status_code == 404
