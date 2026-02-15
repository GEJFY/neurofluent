"""Pronunciation(発音トレーニング)ルーターのテスト"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.pronunciation import (
    JapaneseSpeakerPhoneme,
    PronunciationExercise,
    ProsodyExercise,
)


class TestPronunciationRouter:
    """発音トレーニングルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_phonemes(self, auth_client):
        """日本語話者の発音問題一覧を取得できる"""
        mock_phonemes = [
            JapaneseSpeakerPhoneme(
                phoneme_pair="/r/-/l/",
                description_ja="日本語にない区別",
                description_en="R/L distinction",
                examples=["right vs light", "read vs lead"],
                practice_words=["right", "light", "read", "lead"],
                common_mistake="日本語の「ラ行」で代用してしまう",
                tip="舌先を上顎につけずに発音する",
            )
        ]
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            # get_japanese_speaker_problems は同期メソッド（awaitなし）
            mock_service.get_japanese_speaker_problems = MagicMock(
                return_value=mock_phonemes
            )

            response = await auth_client.get("/api/speaking/pronunciation/phonemes")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]["phoneme_pair"] == "/r/-/l/"

    @pytest.mark.asyncio
    async def test_get_exercises(self, auth_client):
        """発音練習問題を取得できる"""
        mock_exercises = [
            PronunciationExercise(
                exercise_id="ex-1",
                target_phoneme="/r/-/l/",
                exercise_type="minimal_pair",
                word_a="right",
                word_b="light",
                sentence="Can you hear the difference between 'right' and 'light'?",
                ipa="/raɪt/ vs /laɪt/",
                difficulty="B2",
                tip="舌先の位置に注目",
            )
        ]
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            # generate_exercises は非同期メソッド（awaitあり）
            mock_service.generate_exercises = AsyncMock(return_value=mock_exercises)

            response = await auth_client.get("/api/speaking/pronunciation/exercises")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_prosody_exercises(self, auth_client):
        """韻律練習を取得できる"""
        mock_exercises = [
            ProsodyExercise(
                exercise_id="prosody-1",
                sentence="I'd like to SCHEDULE a meeting.",
                stress_pattern="word stress on SCHEDULE",
                intonation_type="falling",
                explanation="ビジネス会議の予定調整で使うフレーズ",
                context="Meeting scheduling",
            )
        ]
        with patch("app.routers.pronunciation.pronunciation_service") as mock_service:
            # generate_prosody_exercise は非同期メソッド（awaitあり）
            # レスポンスは list[ProsodyExercise]
            mock_service.generate_prosody_exercise = AsyncMock(
                return_value=mock_exercises
            )

            response = await auth_client.get(
                "/api/speaking/pronunciation/prosody/exercises"
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

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
