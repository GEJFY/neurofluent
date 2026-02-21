"""フィードバック生成サービス - ユーザー発話に対するAIフィードバック"""

import logging

from app.prompts.feedback import build_feedback_prompt
from app.schemas.talk import FeedbackData
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)


class FeedbackService:
    """会話中のユーザー発話を分析し、構造化フィードバックを生成"""

    async def generate_feedback(
        self,
        user_text: str,
        conversation_context: list[dict],
        user_level: str = "B2",
        mode: str = "meeting",
        weakness_history: list[str] | None = None,
        industry: str | None = None,
    ) -> FeedbackData:
        """
        ユーザーの英語テキストを分析してフィードバックを生成

        Args:
            user_text: ユーザーが入力した英文
            conversation_context: 直近の会話履歴
            user_level: ユーザーのCEFRレベル
            mode: 会話モード
            weakness_history: 過去セッションで検出された頻出弱点パターン
            industry: ユーザーの業界

        Returns:
            FeedbackData: 構造化されたフィードバック
        """
        system_prompt = build_feedback_prompt(
            user_level=user_level,
            mode=mode,
            weakness_history=weakness_history,
            industry=industry,
        )

        # 会話コンテキストを整形
        context_text = ""
        for msg in conversation_context[-6:]:  # 直近6メッセージまで
            role_label = "User" if msg.get("role") == "user" else "Assistant"
            context_text += f"{role_label}: {msg.get('content', '')}\n"

        messages = [
            {
                "role": "user",
                "content": (
                    f"以下の会話コンテキストにおけるユーザーの最新発話を分析してください。\n\n"
                    f"## 会話コンテキスト\n{context_text}\n\n"
                    f"## 分析対象のユーザー発話\n{user_text}\n\n"
                    f"JSON形式で回答してください。"
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

            return FeedbackData(
                grammar_errors=result.get("grammar_errors", []),
                expression_upgrades=result.get("expression_upgrades", []),
                pronunciation_notes=result.get("pronunciation_notes", []),
                positive_feedback=result.get("positive_feedback", ""),
                vocabulary_level=result.get("vocabulary_level", user_level),
            )

        except (ValueError, KeyError) as e:
            logger.warning("フィードバック生成でパースエラー: %s", e)
            # パースエラー時はデフォルトフィードバックを返す
            return FeedbackData(
                grammar_errors=[],
                expression_upgrades=[],
                pronunciation_notes=[],
                positive_feedback="Good effort! Keep practicing.",
                vocabulary_level=user_level,
            )

        except Exception as e:
            logger.error("フィードバック生成で予期しないエラー: %s", e)
            return FeedbackData(
                grammar_errors=[],
                expression_upgrades=[],
                pronunciation_notes=[],
                positive_feedback="Analysis temporarily unavailable.",
                vocabulary_level=user_level,
            )


# シングルトンインスタンス
feedback_service = FeedbackService()
