"""Realtime(リアルタイム音声)ルーターのテスト"""

from unittest.mock import MagicMock, patch

import pytest


class TestRealtimeRouter:
    """リアルタイム音声ルーターのテスト"""

    @pytest.mark.asyncio
    async def test_create_session(self, auth_client):
        """認証済みユーザーでリアルタイムセッションを作成できる"""
        with patch("app.routers.realtime.realtime_service") as mock_service:
            # create_session は同期メソッド（awaitなし）
            mock_service.create_session = MagicMock(
                return_value={
                    "ws_url": "wss://test.openai.azure.com/realtime",
                    "session_token": "test-token-abc123",
                    "model": "gpt-4o-realtime",
                    "voice": "alloy",
                    "mode": "casual_chat",
                    "instructions_summary": "Casual Chat: 自由に英会話を楽しもう",
                    "instructions": "You are a conversation partner...",
                    "api_key": "test-key",
                }
            )

            response = await auth_client.post(
                "/api/talk/realtime/session",
                json={"mode": "casual_chat"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "ws_url" in data
            assert "session_token" in data
            assert data["voice"] == "alloy"
            assert data["mode"] == "casual_chat"

    @pytest.mark.asyncio
    async def test_get_modes(self, auth_client):
        """利用可能なモード一覧を取得できる"""
        with patch("app.routers.realtime.realtime_service") as mock_service:
            # get_available_modes は同期メソッド（awaitなし）
            mock_service.get_available_modes = MagicMock(
                return_value=[
                    {
                        "id": "casual_chat",
                        "name": "Casual Chat",
                        "description": "自由な英会話",
                        "available": True,
                        "phase": "phase1",
                    },
                    {
                        "id": "meeting",
                        "name": "Business Meeting",
                        "description": "ビジネス会議シミュレーション",
                        "available": True,
                        "phase": "phase2",
                    },
                ]
            )

            response = await auth_client.get("/api/talk/realtime/modes")

            assert response.status_code == 200
            data = response.json()
            # レスポンスは ConversationModeList: {"modes": [...], "current_phase": "..."}
            assert "modes" in data
            assert isinstance(data["modes"], list)
            assert len(data["modes"]) > 0
            assert data["modes"][0]["id"] == "casual_chat"

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーはエラーになる"""
        response = await client.post(
            "/api/talk/realtime/session",
            json={"mode": "casual_chat"},
        )

        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_invalid_mode(self, auth_client):
        """無効なモードで400エラーになる"""
        response = await auth_client.post(
            "/api/talk/realtime/session",
            json={"mode": "invalid_mode_xyz"},
        )

        # ルーターでバリデーション済み → 400
        assert response.status_code == 400
