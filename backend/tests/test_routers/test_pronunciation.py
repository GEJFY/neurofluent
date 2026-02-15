"""Pronunciation(発音トレーニング)ルーターのテスト"""

from unittest.mock import AsyncMock, patch

import pytest


class TestPronunciationRouter:
    """発音トレーニングルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_phonemes(self, auth_client):
        """日本語話者の発音問題一覧を取得できる"""
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            mock_service.get_japanese_speaker_problems = AsyncMock(
                return_value=[
                    {
                        "phoneme_pair": "/r/-/l/",
                        "description": "日本語にない区別",
                        "difficulty": "high",
                        "examples": ["right/light", "read/lead"],
                    }
                ]
            )

            response = await auth_client.get("/api/speaking/pronunciation/phonemes")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_exercises(self, auth_client):
        """発音練習問題を取得できる"""
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            mock_service.generate_exercises = AsyncMock(
                return_value=[
                    {
                        "id": "ex-1",
                        "type": "minimal_pair",
                        "word1": "right",
                        "word2": "light",
                        "phoneme": "/r/-/l/",
                    }
                ]
            )

            response = await auth_client.get("/api/speaking/pronunciation/exercises")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_prosody_exercises(self, auth_client):
        """韻律練習を取得できる"""
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            mock_service.generate_prosody_exercise = AsyncMock(
                return_value={
                    "type": "stress",
                    "text": "I'd like to SCHEDULE a meeting",
                    "focus": "word stress",
                    "tips": ["Stress on the capitalized syllable"],
                }
            )

            response = await auth_client.get(
                "/api/speaking/pronunciation/prosody/exercises"
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーはエラーになる"""
        response = await client.get("/api/speaking/pronunciation/phonemes")

        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_progress(self, auth_client):
        """発音進捗を取得できる"""
        response = await auth_client.get("/api/speaking/pronunciation/progress")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
