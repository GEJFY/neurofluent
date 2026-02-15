"""もごもごイングリッシュサービス - リンキング・リダクション音声変化訓練

ネイティブスピーカーの自然な音声変化パターン（リンキング、リダクション、
フラッピング、削除、弱形）を聞き取る力を養成するサービス。
"""

import logging
import uuid
from difflib import SequenceMatcher

from app.prompts.mogomogo import (
    SOUND_PATTERN_DATABASE,
    build_dictation_check_prompt,
    build_mogomogo_generation_prompt,
)
from app.schemas.mogomogo import (
    DictationResult,
    IpaExample,
    MogomogoExercise,
    SoundPatternInfo,
)
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)


class MogomogoService:
    """もごもごイングリッシュ - 音声変化パターンの訓練サービス"""

    async def generate_exercises(
        self,
        pattern_types: list[str],
        user_level: str = "B2",
        count: int = 10,
    ) -> list[MogomogoExercise]:
        """
        指定された音声変化パターンの練習問題を生成

        Args:
            pattern_types: 対象パターン種別リスト
            user_level: ユーザーのCEFRレベル
            count: 生成する問題数

        Returns:
            MogomogoExerciseのリスト
        """
        # 有効なパターンのみフィルタリング
        valid_patterns = [pt for pt in pattern_types if pt in SOUND_PATTERN_DATABASE]
        if not valid_patterns:
            valid_patterns = ["linking", "reduction"]

        system_prompt = build_mogomogo_generation_prompt(valid_patterns, user_level)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} connected speech exercises.\n"
                    f"Pattern types to include: {', '.join(valid_patterns)}\n"
                    f"Target level: {user_level}\n\n"
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

            exercises_data = (
                result if isinstance(result, list) else result.get("exercises", [])
            )

            exercises = []
            for item in exercises_data:
                exercise = MogomogoExercise(
                    exercise_id=item.get("exercise_id", str(uuid.uuid4())),
                    pattern_type=item.get("pattern_type", valid_patterns[0]),
                    audio_text=item.get("audio_text", ""),
                    ipa_original=item.get("ipa_original", ""),
                    ipa_modified=item.get("ipa_modified", ""),
                    explanation=item.get("explanation", ""),
                    practice_sentence=item.get("practice_sentence", ""),
                    difficulty=item.get("difficulty", user_level),
                )
                exercises.append(exercise)

            return exercises

        except Exception as e:
            logger.error("もごもごエクササイズ生成エラー: %s", e)
            # フォールバック: データベースから直接エクササイズを構築
            return self._build_fallback_exercises(valid_patterns, user_level, count)

    async def check_dictation(
        self,
        exercise_id: str,
        user_text: str,
        original_text: str,
    ) -> DictationResult:
        """
        ディクテーションの正確性をチェック

        Args:
            exercise_id: エクササイズID
            user_text: ユーザーが聞き取ったテキスト
            original_text: 元のテキスト

        Returns:
            DictationResult: 評価結果
        """
        system_prompt = build_dictation_check_prompt()

        messages = [
            {
                "role": "user",
                "content": (
                    f"Original text: {original_text}\n"
                    f"User's dictation: {user_text}\n\n"
                    f"Evaluate the dictation accuracy and return JSON."
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

            return DictationResult(
                accuracy=min(max(float(result.get("accuracy", 0.0)), 0.0), 1.0),
                missed_words=result.get("missed_words", []),
                identified_patterns=result.get("identified_patterns", []),
                score=min(max(float(result.get("score", 0.0)), 0.0), 1.0),
                feedback=result.get("feedback", ""),
            )

        except Exception as e:
            logger.error("ディクテーションチェックエラー: %s", e)
            # フォールバック: シンプルな文字列比較
            return self._fallback_dictation_check(user_text, original_text)

    def get_pattern_types(self) -> list[SoundPatternInfo]:
        """
        利用可能な全音声変化パターン種別と説明・例を返す

        Returns:
            SoundPatternInfoのリスト
        """
        patterns = []
        for pattern_key, data in SOUND_PATTERN_DATABASE.items():
            examples = [
                ex["text"] + " -> " + ex["modified"] for ex in data["examples"][:5]
            ]
            ipa_examples = [
                IpaExample(
                    original=ex["ipa_original"],
                    modified=ex["ipa_modified"],
                    word=ex["text"],
                )
                for ex in data["examples"][:5]
            ]

            patterns.append(
                SoundPatternInfo(
                    type=pattern_key,
                    name_en=data["name_en"],
                    name_ja=data["name_ja"],
                    description=data["description"],
                    examples=examples,
                    ipa_examples=ipa_examples,
                )
            )

        return patterns

    def _build_fallback_exercises(
        self,
        pattern_types: list[str],
        level: str,
        count: int,
    ) -> list[MogomogoExercise]:
        """フォールバック: データベースからエクササイズを直接構築"""
        exercises = []
        exercise_count = 0

        for pt in pattern_types:
            if pt not in SOUND_PATTERN_DATABASE:
                continue
            db_entry = SOUND_PATTERN_DATABASE[pt]
            for ex in db_entry["examples"]:
                if exercise_count >= count:
                    break
                exercises.append(
                    MogomogoExercise(
                        exercise_id=str(uuid.uuid4()),
                        pattern_type=pt,
                        audio_text=ex["text"],
                        ipa_original=ex["ipa_original"],
                        ipa_modified=ex["ipa_modified"],
                        explanation=f"{db_entry['name_en']}: {db_entry['description']}",
                        practice_sentence=f'Listen carefully: "{ex["text"]}" naturally sounds like "{ex["modified"]}".',
                        difficulty=level,
                    )
                )
                exercise_count += 1
            if exercise_count >= count:
                break

        return exercises

    def _fallback_dictation_check(
        self,
        user_text: str,
        original_text: str,
    ) -> DictationResult:
        """フォールバック: シンプルな文字列比較によるディクテーション評価"""
        user_words = user_text.strip().lower().split()
        original_words = original_text.strip().lower().split()

        # SequenceMatcherで単語レベルの一致度を計算
        matcher = SequenceMatcher(None, user_words, original_words)
        accuracy = matcher.ratio()

        # 見落とした単語を特定
        missed_words = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ("replace", "delete"):
                missed_words.extend(original_words[j1:j2])

        score = accuracy

        if accuracy >= 0.9:
            feedback = "Excellent! You caught almost all the words correctly."
        elif accuracy >= 0.7:
            feedback = "Good effort! You caught most of the words. Pay attention to the connected speech patterns."
        elif accuracy >= 0.5:
            feedback = (
                "Keep practicing! Try to focus on how words connect in natural speech."
            )
        else:
            feedback = "This is challenging! Listen again and focus on the individual words within the connected speech."

        return DictationResult(
            accuracy=round(accuracy, 2),
            missed_words=missed_words,
            identified_patterns=[],
            score=round(score, 2),
            feedback=feedback,
        )


# シングルトンインスタンス
mogomogo_service = MogomogoService()
