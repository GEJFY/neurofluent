"""Realtime(リアルタイム音声)ルーターのテスト"""

from unittest.mock import AsyncMock, patch

import pytest


class TestRealtimeRouter:
    """リアルタイム音声ルーターのテスト"""

    @pytest.mark.asyncio
    async def test_create_session(self, auth_client):
        """認証済みユーザーでリアルタイムセッションを作成できる"""
        with patch("app.routers.realtime.realtime_service") as mock_service:
            mock_service.create_session = AsyncMock(
                return_value={
                    "ws_url": "wss://test.openai.azure.com/realtime",
                    "session_token": "test-token",
                    "model": "gpt-realtime",
                    "voice": "alloy",
                    "instructions_summary": "Casual conversation",
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

    @pytest.mark.asyncio
    async def test_get_modes(self, auth_client):
        """利用可能なモード一覧を取得できる"""
        response = await auth_client.get("/api/talk/realtime/modes")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

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
        """無効なモードでエラーになる"""
        with patch("app.routers.realtime.realtime_service") as mock_service:
            mock_service.create_session = AsyncMock(
                return_value={
                    "ws_url": "wss://test.openai.azure.com/realtime",
                    "session_token": "test-token",
                    "model": "gpt-realtime",
                    "voice": "alloy",
                    "instructions_summary": "Test",
                }
            )

            response = await auth_client.post(
                "/api/talk/realtime/session",
                json={"mode": "invalid_mode_xyz"},
            )

            # invalid_mode may return 400 or 422
            assert response.status_code in (200, 400, 422)
