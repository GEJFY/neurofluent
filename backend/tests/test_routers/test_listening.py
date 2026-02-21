"""リスニング・シャドーイングルーターのテスト"""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.listening import ShadowingMaterial


class TestListeningRouter:
    """Listeningルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_shadowing_material(self, auth_client, mock_claude):
        """シャドーイング教材の取得"""
        mock_material = ShadowingMaterial(
            text="Let's review the quarterly results.",
            suggested_speeds=[0.7, 0.8, 0.9, 1.0],
            key_phrases=["quarterly results"],
            vocabulary_notes=[],
            difficulty="intermediate",
        )

        with patch("app.routers.listening.shadowing_service") as mock_svc:
            mock_svc.generate_material = AsyncMock(return_value=mock_material)

            response = await auth_client.get(
                "/api/listening/shadowing/material",
                params={"topic": "business_meeting", "difficulty": "intermediate"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["text"] == "Let's review the quarterly results."
            assert data["difficulty"] == "intermediate"
            assert len(data["suggested_speeds"]) == 4

    @pytest.mark.asyncio
    async def test_get_shadowing_material_invalid_topic(self, auth_client):
        """無効なトピックで400エラー"""
        response = await auth_client.get(
            "/api/listening/shadowing/material",
            params={"topic": "invalid_topic"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_shadowing_material_invalid_difficulty(self, auth_client):
        """無効な難易度で400エラー"""
        response = await auth_client.get(
            "/api/listening/shadowing/material",
            params={"difficulty": "super_hard"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_tts(self, auth_client, mock_speech):
        """TTS変換エンドポイント"""
        with patch("app.routers.listening.shadowing_service") as mock_svc:
            mock_svc.generate_audio = AsyncMock(return_value=b"fake-wav-bytes")

            response = await auth_client.post(
                "/api/listening/tts",
                json={
                    "text": "Hello, this is a test.",
                    "speed": 1.0,
                    "voice": "en-US-JennyMultilingualNeural",
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"
            assert response.content == b"fake-wav-bytes"

    @pytest.mark.asyncio
    async def test_tts_error(self, auth_client):
        """TTS変換エラー時に500エラー"""
        with patch("app.routers.listening.shadowing_service") as mock_svc:
            mock_svc.generate_audio = AsyncMock(
                side_effect=RuntimeError("Speech API unavailable")
            )

            response = await auth_client.post(
                "/api/listening/tts",
                json={"text": "Test"},
            )

            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_shadowing_history(self, auth_client):
        """シャドーイング練習履歴の取得（空）"""
        response = await auth_client.get("/api/listening/shadowing/history")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_accents(self, auth_client):
        """アクセント・環境一覧の取得"""
        with patch("app.services.speech_service.speech_service") as mock_svc:
            mock_svc.get_available_accents = lambda: [
                {"id": "us", "label": "American English"},
                {"id": "uk", "label": "British English"},
            ]
            mock_svc.get_available_environments = lambda: [
                {"id": "clean", "label": "Clean"},
                {"id": "phone_call", "label": "Phone Call"},
            ]

            response = await auth_client.get("/api/listening/accents")

            assert response.status_code == 200
            data = response.json()
            assert "accents" in data
            assert "environments" in data
            assert len(data["accents"]) >= 1
            assert len(data["environments"]) >= 1

    @pytest.mark.asyncio
    async def test_get_shadowing_material_with_accent(self, auth_client, mock_claude):
        """アクセント・環境指定でシャドーイング教材を取得"""
        mock_material = ShadowingMaterial(
            text="Shall we crack on with the agenda?",
            suggested_speeds=[0.8, 1.0],
            key_phrases=["crack on"],
            vocabulary_notes=[],
            difficulty="intermediate",
        )

        with patch("app.routers.listening.shadowing_service") as mock_svc:
            mock_svc.generate_material = AsyncMock(return_value=mock_material)

            response = await auth_client.get(
                "/api/listening/shadowing/material",
                params={
                    "topic": "business_meeting",
                    "difficulty": "intermediate",
                    "accent": "uk",
                    "environment": "phone_call",
                },
            )

            assert response.status_code == 200
            # サービスにaccent/environmentが渡されたことを検証
            mock_svc.generate_material.assert_called_once()
            call_kwargs = mock_svc.generate_material.call_args
            assert call_kwargs.kwargs.get("accent") == "uk" or (
                len(call_kwargs.args) > 3 and call_kwargs.args[3] == "uk"
            )

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401/403エラー（HTTPBearer）"""
        response = await client.get("/api/listening/shadowing/material")
        assert response.status_code in (401, 403)
