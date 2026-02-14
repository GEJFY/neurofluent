"""シャドーイングサービスのテスト - 教材生成・評価"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.shadowing_service import ShadowingService


class TestShadowingService:
    """ShadowingServiceのテスト"""

    @pytest.mark.asyncio
    async def test_get_material(self):
        """正常系: シャドーイング教材の生成"""
        service = ShadowingService()

        mock_response = {
            "text": "Let's review the quarterly results. Our revenue grew by 15% year over year.",
            "key_phrases": ["quarterly results", "revenue grew", "year over year"],
            "vocabulary_notes": [
                {"word": "quarterly", "meaning": "四半期の", "example": "We have quarterly meetings."}
            ],
        }

        with patch("app.services.shadowing_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(return_value=mock_response)

            material = await service.generate_material(
                topic="earnings_call",
                difficulty="intermediate",
                user_level="B2",
            )

            assert material.text == mock_response["text"]
            assert len(material.key_phrases) == 3
            assert material.difficulty == "intermediate"
            # intermediateの推奨速度
            assert 0.7 in material.suggested_speeds
            assert 1.0 in material.suggested_speeds

    @pytest.mark.asyncio
    async def test_get_material_fallback_on_error(self):
        """エラー時にフォールバック教材が返される"""
        service = ShadowingService()

        with patch("app.services.shadowing_service.claude_service") as mock_claude:
            mock_claude.chat_json = AsyncMock(side_effect=RuntimeError("API error"))

            material = await service.generate_material(
                difficulty="beginner",
            )

            # フォールバック教材が返される
            assert len(material.text) > 0
            assert material.difficulty == "beginner"
            assert material.suggested_speeds == [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    @pytest.mark.asyncio
    async def test_evaluate_shadowing(self):
        """正常系: シャドーイング評価"""
        service = ShadowingService()

        mock_pron_result = MagicMock()
        mock_pron_result.accuracy_score = 85.0
        mock_pron_result.fluency_score = 80.0
        mock_pron_result.prosody_score = 75.0
        mock_pron_result.completeness_score = 90.0
        mock_pron_result.word_scores = []

        with patch("app.services.shadowing_service.speech_service") as mock_speech:
            mock_speech.assess_pronunciation = AsyncMock(return_value=mock_pron_result)

            result = await service.evaluate_shadowing(
                user_audio=b"fake-audio-bytes",
                reference_text="Hello, this is a test.",
                target_speed=1.0,
            )

            # 重み付き平均: 85*0.35 + 80*0.30 + 75*0.20 + 90*0.15 = 82.25
            expected_score = round(
                85.0 * 0.35 + 80.0 * 0.30 + 75.0 * 0.20 + 90.0 * 0.15, 1
            )
            assert result.overall_score == expected_score
            assert result.accuracy == 85.0
            assert result.fluency == 80.0
            assert result.prosody == 75.0
            assert result.completeness == 90.0
            assert result.speed_achieved == 1.0

    @pytest.mark.asyncio
    async def test_evaluate_shadowing_error(self):
        """評価エラー時に例外がraiseされる"""
        service = ShadowingService()

        with patch("app.services.shadowing_service.speech_service") as mock_speech:
            mock_speech.assess_pronunciation = AsyncMock(
                side_effect=RuntimeError("Speech API unavailable")
            )

            with pytest.raises(RuntimeError, match="Speech API unavailable"):
                await service.evaluate_shadowing(
                    user_audio=b"audio",
                    reference_text="Test",
                )

    @pytest.mark.asyncio
    async def test_generate_audio(self):
        """TTS音声生成が正常に動作する"""
        service = ShadowingService()

        with patch("app.services.shadowing_service.speech_service") as mock_speech:
            mock_speech.text_to_speech = AsyncMock(return_value=b"fake-wav-data")

            audio = await service.generate_audio(
                text="Hello world",
                speed=1.2,
            )

            assert audio == b"fake-wav-data"
            mock_speech.text_to_speech.assert_called_once_with(
                text="Hello world",
                voice="en-US-JennyMultilingualNeural",
                speed=1.2,
            )

    def test_suggested_speeds_by_difficulty(self):
        """難易度別の推奨速度リストが正しい"""
        service = ShadowingService()

        beginner = service._get_suggested_speeds("beginner")
        assert beginner[0] == 0.5
        assert beginner[-1] == 1.0

        advanced = service._get_suggested_speeds("advanced")
        assert advanced[0] == 0.8
        assert advanced[-1] == 1.5
