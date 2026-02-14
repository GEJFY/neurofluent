"""発音トレーニングサービス - 日本語話者向け音素・韻律訓練

日本語話者に特有のL1干渉パターン（/r/-/l/, /θ/-/s/, /v/-/b/等）に
フォーカスした発音エクササイズの生成と、Azure Speech APIによる
音素レベルの発音評価を行う。
"""

import logging
import uuid

import httpx

from app.config import settings
from app.schemas.pronunciation import (
    PronunciationExercise,
    PhonemeResult,
    ProsodyExercise,
    JapaneseSpeakerPhoneme,
)
from app.services.claude_service import claude_service
from app.prompts.pronunciation import (
    build_pronunciation_exercise_prompt,
    build_prosody_exercise_prompt,
    JAPANESE_L1_INTERFERENCE,
)

logger = logging.getLogger(__name__)


class PronunciationService:
    """発音トレーニングサービス - 音素練習と発音評価"""

    def __init__(self):
        self.speech_key = settings.azure_speech_key
        self.speech_region = settings.azure_speech_region
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def generate_exercises(
        self,
        target_phonemes: list[str],
        user_level: str = "B2",
        count: int = 10,
        exercise_type: str | None = None,
    ) -> list[PronunciationExercise]:
        """
        指定音素の発音練習問題を生成

        Args:
            target_phonemes: 対象音素ペアリスト (例: ["/r/-/l/", "/θ/-/s/"])
            user_level: ユーザーのCEFRレベル
            count: 生成する問題数
            exercise_type: 問題種別フィルタ (minimal_pair, tongue_twister, sentence)

        Returns:
            PronunciationExerciseのリスト
        """
        # 有効な音素のみフィルタ
        valid_phonemes = [
            p for p in target_phonemes if p in JAPANESE_L1_INTERFERENCE
        ]
        if not valid_phonemes:
            valid_phonemes = ["/r/-/l/"]

        system_prompt = build_pronunciation_exercise_prompt(valid_phonemes, user_level)

        type_filter = ""
        if exercise_type:
            type_filter = f"\nGenerate only '{exercise_type}' type exercises."

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} pronunciation exercises.\n"
                    f"Target phonemes: {', '.join(valid_phonemes)}\n"
                    f"Target level: {user_level}"
                    f"{type_filter}\n\n"
                    f"Return a JSON array of exercises."
                ),
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=4096,
                system=system_prompt,
            )

            exercises_data = result if isinstance(result, list) else result.get("exercises", [])

            exercises = []
            for item in exercises_data:
                exercise = PronunciationExercise(
                    exercise_id=item.get("exercise_id", str(uuid.uuid4())),
                    target_phoneme=item.get("target_phoneme", valid_phonemes[0]),
                    exercise_type=item.get("exercise_type", "sentence"),
                    word_a=item.get("word_a", ""),
                    word_b=item.get("word_b"),
                    sentence=item.get("sentence", ""),
                    ipa=item.get("ipa", ""),
                    audio_url=item.get("audio_url"),
                    difficulty=item.get("difficulty", user_level),
                    tip=item.get("tip", ""),
                )
                exercises.append(exercise)

            return exercises

        except Exception as e:
            logger.error("発音エクササイズ生成エラー: %s", e)
            return self._build_fallback_exercises(valid_phonemes, user_level, count)

    async def evaluate_phoneme(
        self,
        audio_data: bytes,
        target_phoneme: str,
        reference_text: str,
    ) -> PhonemeResult:
        """
        Azure Speech APIで音素レベルの発音評価を実行

        Args:
            audio_data: WAV形式の音声データ
            target_phoneme: 評価対象の音素
            reference_text: 参照テキスト（ユーザーが発話すべきテキスト）

        Returns:
            PhonemeResult: 音素評価結果
        """
        if not self.speech_key or not self.speech_region:
            logger.warning("Azure Speech APIキーが未設定。フォールバック評価を使用。")
            return self._fallback_evaluation(target_phoneme, reference_text)

        # Azure Speech pronunciation assessment API
        url = (
            f"https://{self.speech_region}.stt.speech.microsoft.com/"
            f"speech/recognition/conversation/cognitiveservices/v1"
            f"?language=en-US"
        )

        # Pronunciation assessment設定
        pronunciation_config = {
            "referenceText": reference_text,
            "gradingSystem": "HundredMark",
            "granularity": "Phoneme",
            "dimension": "Comprehensive",
            "enableMiscue": True,
        }

        import base64
        import json
        config_json = json.dumps(pronunciation_config)
        config_base64 = base64.b64encode(config_json.encode()).decode()

        headers = {
            "Ocp-Apim-Subscription-Key": self.speech_key,
            "Content-Type": "audio/wav",
            "Pronunciation-Assessment": config_base64,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    content=audio_data,
                )

                if response.status_code != 200:
                    logger.error(
                        "Azure Speech API エラー: status=%d body=%s",
                        response.status_code,
                        response.text,
                    )
                    return self._fallback_evaluation(target_phoneme, reference_text)

                data = response.json()

            # 発音評価結果をパース
            return self._parse_pronunciation_result(data, target_phoneme)

        except Exception as e:
            logger.error("発音評価エラー: %s", e)
            return self._fallback_evaluation(target_phoneme, reference_text)

    def get_japanese_speaker_problems(self) -> list[JapaneseSpeakerPhoneme]:
        """
        日本語話者に共通するL1干渉パターンの一覧を返す

        Returns:
            JapaneseSpeakerPhonemeのリスト
        """
        problems = []
        for key, data in JAPANESE_L1_INTERFERENCE.items():
            # ミニマルペアから練習用単語を抽出
            practice_words = []
            for a, b in data["minimal_pairs"][:6]:
                practice_words.extend([a, b])

            problems.append(
                JapaneseSpeakerPhoneme(
                    phoneme_pair=data["phoneme_pair"],
                    description_ja=data["description_ja"],
                    description_en=data["description_en"],
                    examples=data["practice_sentences"][:3],
                    practice_words=practice_words,
                    common_mistake=data["common_mistake"],
                    tip=data["tip"],
                )
            )

        return problems

    async def generate_prosody_exercise(
        self,
        pattern: str = "stress",
        count: int = 5,
    ) -> list[ProsodyExercise]:
        """
        韻律（ストレス・リズム・イントネーション）エクササイズを生成

        Args:
            pattern: パターン種別 (stress, rhythm, intonation)
            count: 生成する問題数

        Returns:
            ProsodyExerciseのリスト
        """
        system_prompt = build_prosody_exercise_prompt(pattern)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} prosody exercises focusing on '{pattern}'.\n"
                    f"Use business English contexts.\n\n"
                    f"Return a JSON array of exercises."
                ),
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=2048,
                system=system_prompt,
            )

            exercises_data = result if isinstance(result, list) else result.get("exercises", [])

            exercises = []
            for item in exercises_data:
                exercises.append(ProsodyExercise(
                    exercise_id=item.get("exercise_id", str(uuid.uuid4())),
                    sentence=item.get("sentence", ""),
                    stress_pattern=item.get("stress_pattern", ""),
                    intonation_type=item.get("intonation_type", "falling"),
                    audio_url=item.get("audio_url"),
                    explanation=item.get("explanation", ""),
                    context=item.get("context", ""),
                ))

            return exercises

        except Exception as e:
            logger.error("韻律エクササイズ生成エラー: %s", e)
            return self._build_fallback_prosody(pattern, count)

    # --- プライベートヘルパーメソッド ---

    def _parse_pronunciation_result(
        self,
        data: dict,
        target_phoneme: str,
    ) -> PhonemeResult:
        """Azure Speech APIの結果をパース"""
        nbest = data.get("NBest", [{}])
        if not nbest:
            return self._fallback_evaluation(target_phoneme, "")

        best = nbest[0]
        pron_assessment = best.get("PronunciationAssessment", {})

        accuracy_score = pron_assessment.get("AccuracyScore", 0.0) / 100.0
        pron_score = pron_assessment.get("PronScore", 0.0) / 100.0

        # 音素レベルの結果を検索
        words = best.get("Words", [])
        phoneme_details = []
        for word in words:
            phonemes = word.get("Phonemes", [])
            for phoneme in phonemes:
                phoneme_assessment = phoneme.get("PronunciationAssessment", {})
                phoneme_details.append({
                    "phoneme": phoneme.get("Phoneme", ""),
                    "accuracy": phoneme_assessment.get("AccuracyScore", 0.0),
                })

        # フィードバック生成
        is_correct = accuracy_score >= 0.7

        if accuracy_score >= 0.9:
            feedback = "Excellent pronunciation! Your articulation is very clear."
        elif accuracy_score >= 0.7:
            feedback = "Good pronunciation! A few minor adjustments would make it even better."
        elif accuracy_score >= 0.5:
            feedback = "Getting there! Focus on the specific phoneme contrast in this exercise."
        else:
            feedback = "Keep practicing! Pay close attention to the tongue and lip position for this sound."

        # 共通エラーパターンの特定
        error_pattern = ""
        if target_phoneme in JAPANESE_L1_INTERFERENCE:
            error_pattern = JAPANESE_L1_INTERFERENCE[target_phoneme]["common_mistake"]

        return PhonemeResult(
            target_phoneme=target_phoneme,
            accuracy=round(accuracy_score, 3),
            is_correct=is_correct,
            feedback=feedback,
            common_error_pattern=error_pattern,
        )

    def _fallback_evaluation(
        self,
        target_phoneme: str,
        reference_text: str,
    ) -> PhonemeResult:
        """フォールバック: Azure Speech API不使用時の評価"""
        error_pattern = ""
        if target_phoneme in JAPANESE_L1_INTERFERENCE:
            error_pattern = JAPANESE_L1_INTERFERENCE[target_phoneme]["common_mistake"]

        return PhonemeResult(
            target_phoneme=target_phoneme,
            accuracy=0.0,
            is_correct=False,
            feedback=(
                "Pronunciation evaluation requires the Azure Speech API. "
                "Please ensure your Azure Speech key is configured. "
                "In the meantime, try recording yourself and comparing with native speakers."
            ),
            common_error_pattern=error_pattern,
        )

    def _build_fallback_exercises(
        self,
        phonemes: list[str],
        level: str,
        count: int,
    ) -> list[PronunciationExercise]:
        """フォールバック: L1干渉データベースからエクササイズを構築"""
        exercises = []
        exercise_count = 0

        for phoneme in phonemes:
            if phoneme not in JAPANESE_L1_INTERFERENCE:
                continue

            data = JAPANESE_L1_INTERFERENCE[phoneme]

            # ミニマルペア
            for a, b in data["minimal_pairs"]:
                if exercise_count >= count:
                    break
                exercises.append(PronunciationExercise(
                    exercise_id=str(uuid.uuid4()),
                    target_phoneme=phoneme,
                    exercise_type="minimal_pair",
                    word_a=a,
                    word_b=b,
                    sentence=f"Can you hear the difference between '{a}' and '{b}'?",
                    ipa=f"/{a}/ vs /{b}/",
                    difficulty=level,
                    tip=data["tip"],
                ))
                exercise_count += 1

            # 練習文
            for sentence in data["practice_sentences"]:
                if exercise_count >= count:
                    break
                exercises.append(PronunciationExercise(
                    exercise_id=str(uuid.uuid4()),
                    target_phoneme=phoneme,
                    exercise_type="sentence",
                    word_a=sentence.split()[0],
                    word_b=None,
                    sentence=sentence,
                    ipa="",
                    difficulty=level,
                    tip=data["tip"],
                ))
                exercise_count += 1

            # 早口言葉
            for tw in data["tongue_twisters"]:
                if exercise_count >= count:
                    break
                exercises.append(PronunciationExercise(
                    exercise_id=str(uuid.uuid4()),
                    target_phoneme=phoneme,
                    exercise_type="tongue_twister",
                    word_a=tw,
                    word_b=None,
                    sentence=tw,
                    ipa="",
                    difficulty=level,
                    tip=data["tip"],
                ))
                exercise_count += 1

            if exercise_count >= count:
                break

        return exercises

    def _build_fallback_prosody(
        self,
        pattern: str,
        count: int,
    ) -> list[ProsodyExercise]:
        """フォールバック: 静的な韻律エクササイズ"""
        fallback_exercises = {
            "stress": [
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="I didn't say he stole the money.",
                    stress_pattern="Shift stress to each word for different meanings",
                    intonation_type="falling",
                    explanation="In English, changing which word is stressed changes the meaning entirely. "
                               "Japanese relies more on particles and word order for emphasis.",
                    context="Clarifying a misunderstanding in a meeting",
                ),
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="We need to PRESENT the PRESENT to the president.",
                    stress_pattern="preSENT (verb) vs PREsent (noun)",
                    intonation_type="falling",
                    explanation="English stress can change word class: PREsent (noun) vs preSENT (verb). "
                               "This doesn't exist in Japanese.",
                    context="Discussing a gift for a company executive",
                ),
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="The project is ON schedule and UNDER budget.",
                    stress_pattern="oOo - content words stressed, function words weak",
                    intonation_type="falling",
                    explanation="English stresses content words (nouns, verbs, adjectives) and reduces function words. "
                               "Japanese gives more equal weight to all syllables.",
                    context="Status update in a project meeting",
                ),
            ],
            "rhythm": [
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="CATS CHASE MICE across the FLOOR.",
                    stress_pattern="Oo Oo Oo - stress-timed rhythm",
                    intonation_type="falling",
                    explanation="English is stress-timed: stressed syllables occur at regular intervals. "
                               "Unstressed syllables are compressed. Japanese is mora-timed with equal beats.",
                    context="Understanding English speech rhythm",
                ),
            ],
            "intonation": [
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="You're coming to the meeting tomorrow?",
                    stress_pattern="Rising at the end",
                    intonation_type="rising",
                    explanation="Rising intonation turns a statement into a question in English. "
                               "Japanese uses the particle 'ka' instead of intonation for questions.",
                    context="Confirming attendance at a meeting",
                ),
                ProsodyExercise(
                    exercise_id=str(uuid.uuid4()),
                    sentence="That's an interesting proposal, but...",
                    stress_pattern="Fall-rise on 'interesting', trailing off",
                    intonation_type="fall-rise",
                    explanation="Fall-rise intonation in English implies reservation or disagreement. "
                               "It's a polite way to signal 'I have concerns' without saying it directly.",
                    context="Diplomatically expressing doubt in a negotiation",
                ),
            ],
        }

        exercises = fallback_exercises.get(pattern, fallback_exercises["stress"])
        return exercises[:count]


# シングルトンインスタンス
pronunciation_service = PronunciationService()
