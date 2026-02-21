"""Azure Speech Services - 発音評価とテキスト読み上げ

Azure Cognitive Services Speech SDK REST APIを使用して
発音評価（Pronunciation Assessment）とテキスト読み上げ（TTS）を提供。
マルチアクセント音声・環境音シミュレーション対応。
"""

import base64
import json
import logging
from typing import Any

import httpx

from app.config import settings
from app.prompts.accent_profiles import (
    ACCENT_VOICES,
    AUDIO_ENVIRONMENTS,
    get_language_code,
    get_voice_for_accent,
)
from app.schemas.listening import PronunciationResult, PronunciationWordScore

logger = logging.getLogger(__name__)


class SpeechService:
    """Azure Speech Servicesとの通信を管理するサービス"""

    def __init__(self):
        self.speech_key = settings.azure_speech_key
        self.speech_region = settings.azure_speech_region
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    @property
    def _tts_endpoint(self) -> str:
        """TTS APIエンドポイントURL"""
        return f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"

    @property
    def _token_endpoint(self) -> str:
        """トークン取得エンドポイントURL"""
        return f"https://{self.speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"

    @property
    def _pronunciation_endpoint(self) -> str:
        """発音評価エンドポイントURL"""
        return (
            f"https://{self.speech_region}.stt.speech.microsoft.com/"
            f"speech/recognition/conversation/cognitiveservices/v1"
            f"?language=en-US"
        )

    async def _get_auth_token(self) -> str:
        """Azure Speech用の認証トークンを取得"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._token_endpoint,
                headers={
                    "Ocp-Apim-Subscription-Key": self.speech_key,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                content="",
            )
            response.raise_for_status()
            return response.text

    def _build_pronunciation_config(self, reference_text: str) -> str:
        """発音評価の設定JSONを構築"""
        config = {
            "ReferenceText": reference_text,
            "GradingSystem": "HundredMark",
            "Granularity": "Word",
            "Dimension": "Comprehensive",
            "EnableMiscue": True,
            "EnableProsodyAssessment": True,
        }
        config_json = json.dumps(config)
        return base64.b64encode(config_json.encode("utf-8")).decode("utf-8")

    async def assess_pronunciation(
        self,
        audio_data: bytes,
        reference_text: str,
        language: str = "en-US",
    ) -> PronunciationResult:
        """
        音声データの発音評価を実行

        Azure Speech SDKの発音評価APIを使用して、
        正確度・流暢さ・韻律・完全性のスコアを返す。

        Args:
            audio_data: WAV形式の音声バイトデータ
            reference_text: リファレンステキスト
            language: 評価対象の言語コード

        Returns:
            PronunciationResult: 発音評価結果
        """
        pronunciation_config = self._build_pronunciation_config(reference_text)

        headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "audio/wav",
            "Pronunciation-Assessment": pronunciation_config,
            "Accept": "application/json",
        }

        endpoint = (
            f"https://{self.speech_region}.stt.speech.microsoft.com/"
            f"speech/recognition/conversation/cognitiveservices/v1"
            f"?language={language}"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    endpoint,
                    headers=headers,
                    content=audio_data,
                )
                response.raise_for_status()
                result = response.json()

            return self._parse_pronunciation_result(result)

        except httpx.HTTPStatusError as e:
            logger.error(
                "発音評価APIエラー: status=%d body=%s",
                e.response.status_code,
                e.response.text,
            )
            raise
        except Exception as e:
            logger.error("発音評価で予期しないエラー: %s", e)
            raise

    def _parse_pronunciation_result(
        self, result: dict[str, Any]
    ) -> PronunciationResult:
        """Azure Speech APIのレスポンスをPronunciationResultに変換"""
        nbe = result.get("NBest", [])
        if not nbe:
            return PronunciationResult(
                accuracy_score=0.0,
                fluency_score=0.0,
                prosody_score=0.0,
                completeness_score=0.0,
                word_scores=[],
            )

        best = nbe[0]
        pron_assessment = best.get("PronunciationAssessment", {})

        # 単語レベルのスコアを取得
        word_scores = []
        words = best.get("Words", [])
        for word_data in words:
            word_assessment = word_data.get("PronunciationAssessment", {})
            error_type = word_assessment.get("ErrorType", "None")
            word_scores.append(
                PronunciationWordScore(
                    word=word_data.get("Word", ""),
                    accuracy_score=word_assessment.get("AccuracyScore", 0.0),
                    error_type=error_type if error_type != "None" else None,
                )
            )

        return PronunciationResult(
            accuracy_score=pron_assessment.get("AccuracyScore", 0.0),
            fluency_score=pron_assessment.get("FluencyScore", 0.0),
            prosody_score=pron_assessment.get("ProsodyScore", 0.0),
            completeness_score=pron_assessment.get("CompletenessScore", 0.0),
            word_scores=word_scores,
        )

    def get_pronunciation_detail(self, result: dict[str, Any]) -> list[dict]:
        """
        発音評価結果から単語レベルの詳細スコアを取得

        Args:
            result: Azure Speech APIのレスポンス辞書

        Returns:
            単語レベルのスコアリスト
        """
        nbe = result.get("NBest", [])
        if not nbe:
            return []

        best = nbe[0]
        words = best.get("Words", [])
        details = []

        for word_data in words:
            word_assessment = word_data.get("PronunciationAssessment", {})
            syllables = word_data.get("Syllables", [])
            phonemes = word_data.get("Phonemes", [])

            detail = {
                "word": word_data.get("Word", ""),
                "accuracy_score": word_assessment.get("AccuracyScore", 0.0),
                "error_type": word_assessment.get("ErrorType", "None"),
                "offset": word_data.get("Offset", 0),
                "duration": word_data.get("Duration", 0),
                "syllables": [
                    {
                        "syllable": s.get("Syllable", ""),
                        "accuracy_score": s.get("PronunciationAssessment", {}).get(
                            "AccuracyScore", 0.0
                        ),
                    }
                    for s in syllables
                ],
                "phonemes": [
                    {
                        "phoneme": p.get("Phoneme", ""),
                        "accuracy_score": p.get("PronunciationAssessment", {}).get(
                            "AccuracyScore", 0.0
                        ),
                    }
                    for p in phonemes
                ],
            }
            details.append(detail)

        return details

    async def text_to_speech(
        self,
        text: str,
        voice: str = "en-US-JennyMultilingualNeural",
        speed: float = 1.0,
        accent: str | None = None,
        gender: str = "female",
        environment: str = "clean",
    ) -> bytes:
        """
        テキストを音声に変換（Azure TTS）

        SSML形式でリクエストを送信し、WAV形式の音声バイトを返す。
        アクセント選択・環境音シミュレーションに対応。

        Args:
            text: 変換対象テキスト
            voice: 音声名（Azure Neural Voice）。accentが指定された場合は無視。
            speed: 再生速度（0.5〜2.0）
            accent: アクセント (us, uk, india, singapore, australia 等)
            gender: 性別 (female, male)
            environment: 環境設定 (clean, phone_call, video_call, office, cafe 等)

        Returns:
            WAV形式の音声バイトデータ
        """
        # アクセントが指定された場合、対応する音声を選択
        if accent and accent in ACCENT_VOICES:
            voice = get_voice_for_accent(accent, gender)
            lang_code = get_language_code(accent)
        else:
            lang_code = "en-US"

        # 速度を制限
        speed = max(0.5, min(2.0, speed))

        # SSMLを構築
        ssml = self._build_ssml(text, voice, speed, lang_code, environment)

        headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "FluentEdge-AI",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self._tts_endpoint,
                    headers=headers,
                    content=ssml.encode("utf-8"),
                )
                response.raise_for_status()
                return response.content

        except httpx.HTTPStatusError as e:
            logger.error(
                "TTS APIエラー: status=%d body=%s",
                e.response.status_code,
                e.response.text,
            )
            raise
        except Exception as e:
            logger.error("TTS変換で予期しないエラー: %s", e)
            raise

    def _build_ssml(
        self,
        text: str,
        voice: str,
        speed: float,
        lang_code: str,
        environment: str,
    ) -> str:
        """SSML XMLを構築（環境音エフェクト対応）"""
        rate_percent = int((speed - 1.0) * 100)
        rate_str = f"{rate_percent:+d}%" if rate_percent != 0 else "default"

        env_config = AUDIO_ENVIRONMENTS.get(environment, AUDIO_ENVIRONMENTS["clean"])
        ssml_effect = env_config.get("ssml_effect")

        # 環境音エフェクトの適用
        if ssml_effect == "telephone":
            # 電話回線シミュレーション: Azure mstts:express-as + audio effect
            inner_content = f"""<mstts:audioeconfig type="telephone"/>
            <prosody rate='{rate_str}'>
                {text}
            </prosody>"""
        else:
            inner_content = f"""<prosody rate='{rate_str}'>
                {text}
            </prosody>"""

        # ビデオ通話のピッチ調整
        adjustments = env_config.get("ssml_adjustments", {})
        if "pitch" in adjustments:
            pitch_val = adjustments["pitch"]
            inner_content = f"""<prosody rate='{rate_str}' pitch='{pitch_val}'>
                {text}
            </prosody>"""

        return f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
    xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='{lang_code}'>
    <voice name='{voice}'>
        {inner_content}
    </voice>
</speak>"""

    def get_available_accents(self) -> list[dict]:
        """利用可能なアクセント一覧を返す"""
        return [
            {
                "id": accent_id,
                "label": config["label"],
                "label_ja": config["label_ja"],
                "language_code": config["language_code"],
            }
            for accent_id, config in ACCENT_VOICES.items()
        ]

    def get_available_environments(self) -> list[dict]:
        """利用可能な環境設定一覧を返す"""
        return [
            {
                "id": env_id,
                "label": config["label"],
                "description": config["description"],
            }
            for env_id, config in AUDIO_ENVIRONMENTS.items()
        ]


# シングルトンインスタンス
speech_service = SpeechService()
