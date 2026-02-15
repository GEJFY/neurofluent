"""瞬間英作文(Speaking/Flash)ルーターのテスト"""

from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.speaking import FlashCheckResponse, FlashExercise


class TestSpeakingRouter:
    """Speakingルーターのテスト"""

    @pytest.mark.asyncio
    async def test_get_flash_questions(self, auth_client, mock_claude):
        """フラッシュ翻訳エクササイズの取得"""
        mock_exercises = [
            FlashExercise(
                exercise_id="ex-001",
                japanese="会議を始めましょう。",
                english_target="Let's start the meeting.",
                acceptable_alternatives=["Shall we begin the meeting?"],
                key_pattern="Let's + verb",
                difficulty="B2",
                time_limit_seconds=15,
                hints=["Let's..."],
            ),
        ]

        with patch("app.routers.speaking.flash_service") as mock_flash:
            mock_flash.generate_exercises = AsyncMock(return_value=mock_exercises)

            response = await auth_client.get(
                "/api/speaking/flash",
                params={"count": 1},
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["exercise_id"] == "ex-001"
            assert data[0]["japanese"] == "会議を始めましょう。"
            assert data[0]["english_target"] == "Let's start the meeting."

    @pytest.mark.asyncio
    async def test_get_flash_questions_with_focus(self, auth_client, mock_claude):
        """フォーカス指定でのエクササイズ取得"""
        with patch("app.routers.speaking.flash_service") as mock_flash:
            mock_flash.generate_exercises = AsyncMock(return_value=[])

            response = await auth_client.get(
                "/api/speaking/flash",
                params={"count": 5, "focus": "conditionals"},
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_check_answer(self, auth_client, mock_claude):
        """回答チェックエンドポイント"""
        mock_result = FlashCheckResponse(
            is_correct=True,
            score=0.9,
            corrected="Let's start the meeting.",
            explanation="Very natural expression.",
            review_item_created=False,
        )

        with patch("app.routers.speaking.flash_service") as mock_flash:
            mock_flash.check_answer = AsyncMock(return_value=mock_result)

            response = await auth_client.post(
                "/api/speaking/flash/check",
                json={
                    "exercise_id": "ex-001",
                    "user_answer": "Let's start the meeting.",
                    "target": "Let's start the meeting.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["is_correct"] is True
            assert data["score"] == 0.9

    @pytest.mark.asyncio
    async def test_check_answer_low_score_creates_review(
        self, auth_client, mock_claude
    ):
        """低スコアの場合に復習アイテムが作成される"""
        mock_result = FlashCheckResponse(
            is_correct=False,
            score=0.4,
            corrected="Let's start the meeting.",
            explanation="Try again.",
            review_item_created=False,
        )

        with patch("app.routers.speaking.flash_service") as mock_flash:
            mock_flash.check_answer = AsyncMock(return_value=mock_result)

            response = await auth_client.post(
                "/api/speaking/flash/check",
                json={
                    "exercise_id": "ex-002",
                    "user_answer": "Start meeting please.",
                    "target": "Let's start the meeting.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            # スコア0.7未満なので復習アイテムが作成される
            assert data["review_item_created"] is True

    @pytest.mark.asyncio
    async def test_unauthenticated(self, client):
        """未認証ユーザーは401エラー"""
        response = await client.get("/api/speaking/flash")
        assert response.status_code == 401
