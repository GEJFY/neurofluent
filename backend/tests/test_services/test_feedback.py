"""フィードバックサービスのテスト - AIフィードバック生成"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.feedback_service import FeedbackService


class TestFeedbackService:
    """FeedbackServiceのテスト"""

    @pytest.mark.asyncio
    async def test_generate_feedback(self):
        """正常系: claude_serviceをモックしてフィードバック生成"""
        service = FeedbackService()

        mock_response = {
            "grammar_errors": [
                {
                    "original": "I goes",
                    "corrected": "I go",
                    "explanation": "Subject-verb agreement",
                }
            ],
            "expression_upgrades": [
                {
                    "original": "I want to",
                    "upgraded": "I would like to",
                    "context": "more polite",
                }
            ],
            "pronunciation_notes": ["Watch the 'th' sound"],
            "positive_feedback": "Good use of vocabulary!",
            "vocabulary_level": "B2",
        }

        with patch("app.services.feedback_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            result = await service.generate_feedback(
                user_text="I goes to the meeting yesterday.",
                conversation_context=[
                    {"role": "assistant", "content": "How was your day?"},
                    {"role": "user", "content": "I goes to the meeting yesterday."},
                ],
                user_level="B2",
                mode="meeting",
            )

            assert len(result.grammar_errors) == 1
            assert result.grammar_errors[0]["original"] == "I goes"
            assert len(result.expression_upgrades) == 1
            assert result.positive_feedback == "Good use of vocabulary!"
            assert result.vocabulary_level == "B2"

            mock_claude.chat_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_feedback_parse_error_fallback(self):
        """JSONパースエラー時にデフォルトフィードバックが返される"""
        service = FeedbackService()

        with patch("app.services.feedback_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(
                side_effect=ValueError("JSON parse error")
            )

            result = await service.generate_feedback(
                user_text="Hello there",
                conversation_context=[],
                user_level="B1",
                mode="small_talk",
            )

            # パースエラー時のフォールバック
            assert result.grammar_errors == []
            assert result.positive_feedback == "Good effort! Keep practicing."
            assert result.vocabulary_level == "B1"

    @pytest.mark.asyncio
    async def test_feedback_unexpected_error_fallback(self):
        """予期しないエラー時にフォールバックフィードバックが返される"""
        service = FeedbackService()

        with patch("app.services.feedback_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(
                side_effect=RuntimeError("Connection lost")
            )

            result = await service.generate_feedback(
                user_text="Test input",
                conversation_context=[],
                user_level="C1",
                mode="presentation",
            )

            assert result.positive_feedback == "Analysis temporarily unavailable."
            assert result.vocabulary_level == "C1"
