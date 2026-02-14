"""瞬間英作文サービスのテスト - エクササイズ生成・回答チェック"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.flash_service import FlashService


class TestFlashService:
    """FlashServiceのテスト"""

    @pytest.mark.asyncio
    async def test_generate_exercises(self):
        """正常系: エクササイズの動的生成"""
        service = FlashService()

        mock_response = {
            "exercises": [
                {
                    "exercise_id": "ex-001",
                    "japanese": "次回の会議の日程を確認させてください。",
                    "english_target": "Let me confirm the schedule for our next meeting.",
                    "acceptable_alternatives": [
                        "Allow me to verify the schedule for our next meeting."
                    ],
                    "key_pattern": "Let me + verb",
                    "difficulty": "B2",
                    "time_limit_seconds": 15,
                    "hints": ["Let me..."],
                },
                {
                    "exercise_id": "ex-002",
                    "japanese": "この件について検討させてください。",
                    "english_target": "Let me consider this matter.",
                    "acceptable_alternatives": [],
                    "key_pattern": "Let me + verb",
                    "difficulty": "B2",
                    "time_limit_seconds": 15,
                    "hints": [],
                },
            ]
        }

        with patch("app.services.flash_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            exercises = await service.generate_exercises(
                level="B2",
                focus="polite requests",
                count=2,
            )

            assert len(exercises) == 2
            assert exercises[0].exercise_id == "ex-001"
            assert exercises[0].japanese == "次回の会議の日程を確認させてください。"
            assert exercises[0].english_target == "Let me confirm the schedule for our next meeting."
            assert exercises[0].key_pattern == "Let me + verb"

    @pytest.mark.asyncio
    async def test_generate_exercises_with_list_response(self):
        """Claude応答がリスト形式の場合にも対応する"""
        service = FlashService()

        mock_response = [
            {
                "japanese": "承知しました。",
                "english_target": "Understood.",
                "key_pattern": "acknowledgment",
                "difficulty": "B1",
            },
        ]

        with patch("app.services.flash_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            exercises = await service.generate_exercises(count=1)

            assert len(exercises) == 1
            assert exercises[0].english_target == "Understood."

    @pytest.mark.asyncio
    async def test_generate_exercises_error_fallback(self):
        """エラー時にフォールバックエクササイズが返される"""
        service = FlashService()

        with patch("app.services.flash_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            exercises = await service.generate_exercises()

            # フォールバックで最低1問は返される
            assert len(exercises) >= 1
            assert exercises[0].japanese == "次回の会議の日程を調整させてください。"

    @pytest.mark.asyncio
    async def test_check_answer(self):
        """正常系: 回答チェック"""
        service = FlashService()

        mock_response = {
            "is_correct": True,
            "score": 0.95,
            "corrected": "Let me schedule our next meeting.",
            "explanation": "Very close to the target. Natural phrasing.",
        }

        with patch("app.services.flash_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            result = await service.check_answer(
                user_answer="Let me schedule our next meeting.",
                target="Let me arrange the schedule for our next meeting.",
            )

            assert result.is_correct is True
            assert result.score == 0.95
            assert result.corrected == "Let me schedule our next meeting."
            assert result.review_item_created is False

    @pytest.mark.asyncio
    async def test_check_answer_error_fallback(self):
        """エラー時に簡易文字列比較にフォールバックする"""
        service = FlashService()

        with patch("app.services.flash_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            # 完全一致の場合
            result = await service.check_answer(
                user_answer="Hello world.",
                target="Hello world.",
            )
            assert result.is_correct is True
            assert result.score == 1.0

            # 不一致の場合
            result = await service.check_answer(
                user_answer="Hi there",
                target="Hello world.",
            )
            assert result.is_correct is False
            assert result.score == 0.3
