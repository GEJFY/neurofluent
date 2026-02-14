"""シャドーイングサービス - 教材生成・音声合成・評価

Claude Haikuによるシャドーイング教材の動的生成、
Azure TTSによる音声合成、Azure Speech SDKによる評価を統合。
"""

import logging

from app.schemas.listening import (
    ShadowingMaterial,
    ShadowingResult,
    PronunciationWordScore,
)
from app.services.claude_service import claude_service
from app.services.speech_service import speech_service
from app.prompts.shadowing import build_shadowing_material_prompt

logger = logging.getLogger(__name__)


class ShadowingService:
    """シャドーイング練習の教材生成・評価を管理するサービス"""

    async def generate_material(
        self,
        topic: str = "business_meeting",
        difficulty: str = "intermediate",
        user_level: str = "B2",
    ) -> ShadowingMaterial:
        """
        シャドーイング教材を動的に生成

        Claude Haikuを使用して、トピックと難易度に基づいた
        2-4文のビジネス英語テキストを生成。

        Args:
            topic: トピック（business_meeting, earnings_call等）
            difficulty: 難易度（beginner, intermediate, advanced）
            user_level: ユーザーのCEFRレベル

        Returns:
            ShadowingMaterial: 教材テキスト・重要フレーズ・語彙注釈
        """
        system_prompt = build_shadowing_material_prompt(
            topic=topic,
            difficulty=difficulty,
            user_level=user_level,
        )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate a shadowing material passage about '{topic}' "
                    f"at {difficulty} difficulty level. "
                    f"The user's CEFR level is {user_level}."
                ),
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=1024,
                system=system_prompt,
            )

            # 推奨速度を難易度に応じて調整
            suggested_speeds = self._get_suggested_speeds(difficulty)

            return ShadowingMaterial(
                text=result.get("text", ""),
                suggested_speeds=suggested_speeds,
                key_phrases=result.get("key_phrases", []),
                vocabulary_notes=result.get("vocabulary_notes", []),
                difficulty=difficulty,
            )

        except (ValueError, KeyError) as e:
            logger.warning("シャドーイング教材生成でパースエラー: %s", e)
            # フォールバック教材を返す
            return self._get_fallback_material(difficulty)

        except Exception as e:
            logger.error("シャドーイング教材生成で予期しないエラー: %s", e)
            return self._get_fallback_material(difficulty)

    def _get_suggested_speeds(self, difficulty: str) -> list[float]:
        """難易度に応じた推奨速度リストを取得"""
        speed_configs = {
            "beginner": [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "intermediate": [0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
            "advanced": [0.8, 0.9, 1.0, 1.1, 1.2, 1.5],
        }
        return speed_configs.get(difficulty, [0.7, 0.8, 0.9, 1.0, 1.1, 1.2])

    def _get_fallback_material(self, difficulty: str) -> ShadowingMaterial:
        """API障害時のフォールバック教材"""
        fallback_texts = {
            "beginner": (
                "Good morning, everyone. Let's start the meeting. "
                "Today, we will discuss our project timeline."
            ),
            "intermediate": (
                "Thank you for joining today's meeting. I'd like to start by reviewing "
                "our quarterly performance. As you can see from the report, "
                "we've made significant progress in customer acquisition."
            ),
            "advanced": (
                "I'd like to draw your attention to the trend we've been observing "
                "over the past quarter. Despite the challenging market conditions, "
                "our team has managed to not only meet but exceed our targets. "
                "This is largely attributable to the strategic initiatives we implemented last year."
            ),
        }

        return ShadowingMaterial(
            text=fallback_texts.get(difficulty, fallback_texts["intermediate"]),
            suggested_speeds=self._get_suggested_speeds(difficulty),
            key_phrases=["start the meeting", "quarterly performance", "significant progress"],
            vocabulary_notes=[
                {
                    "word": "quarterly",
                    "meaning": "四半期の",
                    "example": "We publish a quarterly report.",
                }
            ],
            difficulty=difficulty,
        )

    async def generate_audio(
        self,
        text: str,
        speed: float = 1.0,
        voice: str = "en-US-JennyMultilingualNeural",
    ) -> bytes:
        """
        テキストを音声に変換

        Azure TTSを使用して、指定された速度で
        WAV形式の音声バイトを生成。

        Args:
            text: 変換対象テキスト
            speed: 再生速度（0.5〜2.0）
            voice: 音声名

        Returns:
            WAV形式の音声バイトデータ
        """
        return await speech_service.text_to_speech(
            text=text,
            voice=voice,
            speed=speed,
        )

    async def evaluate_shadowing(
        self,
        user_audio: bytes,
        reference_text: str,
        target_speed: float = 1.0,
    ) -> ShadowingResult:
        """
        シャドーイングの発音評価を実行

        Azure Speech SDKの発音評価APIを使用して、
        ユーザーのシャドーイング音声を評価。

        Args:
            user_audio: ユーザーのWAV形式音声データ
            reference_text: リファレンステキスト
            target_speed: 目標とした再生速度

        Returns:
            ShadowingResult: 総合スコア・各項目スコア・改善ポイント
        """
        try:
            # 発音評価を実行
            pron_result = await speech_service.assess_pronunciation(
                audio_data=user_audio,
                reference_text=reference_text,
            )

            # 総合スコアを算出（重み付き平均）
            overall_score = (
                pron_result.accuracy_score * 0.35
                + pron_result.fluency_score * 0.30
                + pron_result.prosody_score * 0.20
                + pron_result.completeness_score * 0.15
            )

            # 改善ポイントを抽出
            areas_to_improve = self._identify_improvement_areas(pron_result)

            return ShadowingResult(
                overall_score=round(overall_score, 1),
                accuracy=pron_result.accuracy_score,
                fluency=pron_result.fluency_score,
                prosody=pron_result.prosody_score,
                completeness=pron_result.completeness_score,
                speed_achieved=target_speed,
                word_scores=pron_result.word_scores,
                areas_to_improve=areas_to_improve,
            )

        except Exception as e:
            logger.error("シャドーイング評価でエラー: %s", e)
            raise

    def _identify_improvement_areas(
        self,
        pron_result,
    ) -> list[str]:
        """発音評価結果から改善ポイントを特定"""
        areas = []

        # 全体スコアに基づく改善提案
        if pron_result.accuracy_score < 60:
            areas.append(
                "発音の正確度が低めです。個々の単語の発音を確認し、ゆっくりした速度から練習しましょう。"
            )
        elif pron_result.accuracy_score < 80:
            areas.append(
                "発音はおおむね良好ですが、一部の単語でより正確な発音を目指しましょう。"
            )

        if pron_result.fluency_score < 60:
            areas.append(
                "流暢さを改善しましょう。文の区切りとリズムを意識して、より滑らかに話す練習が効果的です。"
            )
        elif pron_result.fluency_score < 80:
            areas.append(
                "流暢さは良好です。さらにスムーズな話し方を目指して、速度を少し上げてみましょう。"
            )

        if pron_result.prosody_score < 60:
            areas.append(
                "イントネーションとストレスパターンに注意しましょう。文の抑揚をモデル音声に近づける練習が効果的です。"
            )
        elif pron_result.prosody_score < 80:
            areas.append(
                "韻律はおおむね良好です。感情やニュアンスを込めた自然なイントネーションを意識しましょう。"
            )

        if pron_result.completeness_score < 80:
            areas.append(
                "テキストの一部が欠落しています。全文をしっかり聞き取り、漏れなく発話しましょう。"
            )

        # 単語レベルのエラーを特定
        error_words = [
            ws for ws in pron_result.word_scores
            if ws.error_type is not None
        ]
        if error_words:
            mispronounced = [
                ws.word for ws in error_words
                if ws.error_type == "Mispronunciation"
            ]
            if mispronounced:
                words_str = ", ".join(mispronounced[:5])
                areas.append(
                    f"以下の単語の発音を重点的に練習しましょう: {words_str}"
                )

            omitted = [
                ws.word for ws in error_words
                if ws.error_type == "Omission"
            ]
            if omitted:
                words_str = ", ".join(omitted[:5])
                areas.append(
                    f"以下の単語が抜けています。テキスト全体を意識して発話しましょう: {words_str}"
                )

        # 改善ポイントがない場合
        if not areas:
            areas.append(
                "素晴らしいシャドーイングです！速度を上げるか、より難しい教材に挑戦してみましょう。"
            )

        return areas


# シングルトンインスタンス
shadowing_service = ShadowingService()
