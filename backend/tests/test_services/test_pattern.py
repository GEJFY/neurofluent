"""パターンプラクティスサービスのテスト - エクササイズ取得・回答チェック"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.pattern_service import PatternService


class TestPatternService:
    """PatternServiceのテスト"""

    @pytest.mark.asyncio
    async def test_get_exercises(self):
        """パターンエクササイズの取得（組み込み + AI生成）"""
        service = PatternService()

        # 組み込みパターンが少なく、AI生成が必要な場合をテスト
        mock_ai_response = {
            "exercises": [
                {
                    "pattern_id": "ai-001",
                    "pattern_template": "I would like to ___ this topic.",
                    "example_sentence": "I would like to discuss this topic.",
                    "japanese_hint": "このトピックについて___したいのですが。",
                    "category": "meeting",
                    "difficulty": "B2",
                    "fill_in_blank": True,
                },
            ]
        }

        with patch("app.services.pattern_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_ai_response)

            # 少数のリクエストは組み込みから取得（AIは不要かもしれない）
            exercises = await service.get_patterns(
                category="meeting",
                user_level="B2",
                count=3,
            )

            # 結果が返されること（組み込み or AI生成）
            assert len(exercises) >= 1

    @pytest.mark.asyncio
    async def test_get_exercises_ai_error_fallback(self):
        """AI生成エラー時に組み込みパターンのみが返される"""
        service = PatternService()

        with patch("app.services.pattern_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            exercises = await service.get_patterns(
                user_level="B2",
                count=5,
            )

            # エラーでも組み込みパターンから結果が返される
            # （組み込みパターンが0件の場合は空リスト）
            assert isinstance(exercises, list)

    @pytest.mark.asyncio
    async def test_check_answer(self):
        """正常系: パターン回答のチェック"""
        service = PatternService()

        mock_response = {
            "is_correct": True,
            "score": 0.9,
            "corrected": "I would like to discuss this topic.",
            "explanation": "Good use of the pattern!",
            "usage_tip": "Use this in formal meetings.",
        }

        with patch("app.services.pattern_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            result = await service.check_pattern(
                pattern_id="mtg-001",
                user_answer="I would like to discuss this topic.",
                expected="I would like to discuss this topic.",
            )

            assert result.is_correct is True
            assert result.score == 0.9
            assert result.explanation == "Good use of the pattern!"
            assert result.usage_tip == "Use this in formal meetings."

    @pytest.mark.asyncio
    async def test_check_answer_error_fallback(self):
        """チェックエラー時にフォールバック評価が返される"""
        service = PatternService()

        with patch("app.services.pattern_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            # 完全一致の場合
            result = await service.check_pattern(
                pattern_id="mtg-001",
                user_answer="I would like to discuss this.",
                expected="I would like to discuss this.",
            )
            assert result.is_correct is True
            assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_check_answer_partial_match_fallback(self):
        """フォールバック時の部分一致チェック"""
        service = PatternService()

        with patch("app.services.pattern_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=ValueError("parse error"))

            result = await service.check_pattern(
                pattern_id="mtg-001",
                user_answer="I want to talk about this.",
                expected="I would like to discuss this topic in detail.",
            )

            # 部分一致なのでスコアは0-1の間
            assert 0.0 <= result.score <= 1.0
            assert result.corrected == "I would like to discuss this topic in detail."

    def test_get_categories(self):
        """カテゴリ一覧の取得"""
        service = PatternService()
        categories = service.get_categories()

        assert len(categories) > 0
        category_ids = [c.category for c in categories]
        assert "meeting" in category_ids
        assert "negotiation" in category_ids
        assert "presentation" in category_ids
