"""瞬間英作文サービス - エクササイズ生成・回答チェック"""

import logging
import uuid

from app.schemas.speaking import FlashExercise, FlashCheckResponse
from app.services.claude_service import claude_service
from app.prompts.flash_translation import (
    build_flash_generation_prompt,
    build_flash_check_prompt,
)

logger = logging.getLogger(__name__)


class FlashService:
    """瞬間英作文の問題生成と回答評価"""

    async def generate_exercises(
        self,
        level: str = "B2",
        focus: str | None = None,
        weak_patterns: list[str] | None = None,
        count: int = 5,
    ) -> list[FlashExercise]:
        """
        レベルと弱点パターンに基づいてエクササイズを生成

        Args:
            level: 目標CEFRレベル
            focus: フォーカスする文法・表現カテゴリ
            weak_patterns: ユーザーの弱点パターンリスト
            count: 生成する問題数

        Returns:
            FlashExerciseのリスト
        """
        system_prompt = build_flash_generation_prompt(level)

        focus_text = f"Focus area: {focus}" if focus else "General business English"
        weak_text = ""
        if weak_patterns:
            weak_text = f"\nUser's weak patterns to reinforce: {', '.join(weak_patterns)}"

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} flash translation exercises.\n"
                    f"Target level: {level}\n"
                    f"{focus_text}{weak_text}\n\n"
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
                exercise = FlashExercise(
                    exercise_id=item.get("exercise_id", str(uuid.uuid4())),
                    japanese=item["japanese"],
                    english_target=item["english_target"],
                    acceptable_alternatives=item.get("acceptable_alternatives", []),
                    key_pattern=item.get("key_pattern", "general"),
                    difficulty=item.get("difficulty", level),
                    time_limit_seconds=item.get("time_limit_seconds", 15),
                    hints=item.get("hints", []),
                )
                exercises.append(exercise)

            return exercises

        except Exception as e:
            logger.error("エクササイズ生成エラー: %s", e)
            # フォールバック: ハードコードされた基本問題を返す
            return [
                FlashExercise(
                    exercise_id=str(uuid.uuid4()),
                    japanese="次回の会議の日程を調整させてください。",
                    english_target="Let me arrange the schedule for our next meeting.",
                    acceptable_alternatives=[
                        "Allow me to coordinate the timing of our next meeting.",
                        "I'd like to schedule our next meeting.",
                    ],
                    key_pattern="polite request + scheduling",
                    difficulty=level,
                    time_limit_seconds=15,
                    hints=["Let me...", "arrange / coordinate / schedule"],
                ),
            ]

    async def check_answer(
        self,
        user_answer: str,
        target: str,
        alternatives: list[str] | None = None,
    ) -> FlashCheckResponse:
        """
        ユーザーの回答を目標英文と照合・評価

        Args:
            user_answer: ユーザーの回答
            target: 目標英文
            alternatives: 許容される代替英文リスト

        Returns:
            FlashCheckResponse: 評価結果
        """
        system_prompt = build_flash_check_prompt()

        alt_text = ""
        if alternatives:
            alt_text = f"\nAcceptable alternatives:\n" + "\n".join(
                f"- {alt}" for alt in alternatives
            )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Target answer: {target}\n"
                    f"{alt_text}\n\n"
                    f"User's answer: {user_answer}\n\n"
                    f"Evaluate the user's answer and return JSON."
                ),
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="haiku",
                max_tokens=512,
                system=system_prompt,
            )

            return FlashCheckResponse(
                is_correct=result.get("is_correct", False),
                score=min(max(float(result.get("score", 0.0)), 0.0), 1.0),
                corrected=result.get("corrected", target),
                explanation=result.get("explanation", ""),
                review_item_created=False,
            )

        except Exception as e:
            logger.error("回答チェックエラー: %s", e)
            # エラー時はシンプルな文字列比較にフォールバック
            normalized_user = user_answer.strip().lower().rstrip(".")
            normalized_target = target.strip().lower().rstrip(".")
            is_match = normalized_user == normalized_target

            return FlashCheckResponse(
                is_correct=is_match,
                score=1.0 if is_match else 0.3,
                corrected=target,
                explanation="AI evaluation is temporarily unavailable. Simple match was used.",
                review_item_created=False,
            )


# シングルトンインスタンス
flash_service = FlashService()
