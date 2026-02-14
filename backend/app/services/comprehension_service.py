"""リスニングコンプリヘンションサービス - ビジネス英語聴解力訓練

Claude Sonnetを使用してビジネス英語のリスニング素材を生成し、
理解度テスト（選択式・サマリー）の出題と評価を行う。
"""

import logging
import uuid

from app.schemas.comprehension import (
    ComprehensionMaterial,
    ComprehensionQuestion,
    ComprehensionResult,
    SummaryResult,
    VocabularyItem,
)
from app.services.claude_service import claude_service
from app.prompts.comprehension import (
    build_material_generation_prompt,
    build_question_generation_prompt,
    build_summary_evaluation_prompt,
    COMPREHENSION_TOPICS,
)

logger = logging.getLogger(__name__)


class ComprehensionService:
    """リスニングコンプリヘンションサービス"""

    async def generate_material(
        self,
        topic: str,
        difficulty: str = "intermediate",
        duration_minutes: int = 3,
    ) -> ComprehensionMaterial:
        """
        ビジネス英語リスニング素材を生成

        Claude Sonnetを使用して、指定トピック・難易度・長さの
        リスニング素材（スクリプト + 語彙 + 要点）を生成する。

        Args:
            topic: トピック
            difficulty: 難易度 (beginner, intermediate, advanced)
            duration_minutes: 素材の推定長さ（分）

        Returns:
            ComprehensionMaterial: 生成されたリスニング素材
        """
        system_prompt = build_material_generation_prompt(topic, difficulty, duration_minutes)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate a listening comprehension material.\n"
                    f"Topic: {topic}\n"
                    f"Difficulty: {difficulty}\n"
                    f"Duration: approximately {duration_minutes} minutes\n\n"
                    f"Return the material as JSON."
                ),
            }
        ]

        try:
            result = await claude_service.chat_json(
                messages=messages,
                model="sonnet",
                max_tokens=4096,
                system=system_prompt,
            )

            # 語彙データのパース
            vocabulary = []
            for vocab in result.get("vocabulary", []):
                vocabulary.append(VocabularyItem(
                    word=vocab.get("word", ""),
                    definition=vocab.get("definition", ""),
                    example=vocab.get("example", ""),
                    level=vocab.get("level", difficulty),
                ))

            return ComprehensionMaterial(
                material_id=result.get("material_id", str(uuid.uuid4())),
                topic=result.get("topic", topic),
                text=result.get("text", ""),
                difficulty=result.get("difficulty", difficulty),
                duration_seconds=int(result.get("duration_seconds", duration_minutes * 60)),
                vocabulary=vocabulary,
                key_points=result.get("key_points", []),
            )

        except Exception as e:
            logger.error("リスニング素材生成エラー: %s", e)
            return self._build_fallback_material(topic, difficulty, duration_minutes)

    async def generate_questions(
        self,
        text: str,
        count: int = 5,
    ) -> list[ComprehensionQuestion]:
        """
        リスニング素材に対する理解度テスト問題を生成

        Args:
            text: リスニング素材テキスト
            count: 生成する問題数

        Returns:
            ComprehensionQuestionのリスト
        """
        system_prompt = build_question_generation_prompt(text, count)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} comprehension questions for the given text.\n"
                    f"Return a JSON array of questions."
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

            questions_data = result if isinstance(result, list) else result.get("questions", [])

            questions = []
            for item in questions_data:
                questions.append(ComprehensionQuestion(
                    question_id=item.get("question_id", str(uuid.uuid4())),
                    question_text=item.get("question_text", ""),
                    question_type=item.get("question_type", "multiple_choice"),
                    options=item.get("options"),
                    correct_answer=item.get("correct_answer", ""),
                ))

            return questions

        except Exception as e:
            logger.error("問題生成エラー: %s", e)
            return self._build_fallback_questions(text)

    async def check_answer(
        self,
        question_id: str,
        user_answer: str,
        correct_answer: str,
    ) -> ComprehensionResult:
        """
        選択式問題の回答をチェック

        Args:
            question_id: 問題ID
            user_answer: ユーザーの回答
            correct_answer: 正解

        Returns:
            ComprehensionResult: 回答結果
        """
        # 回答の正規化（先頭の "A) ", "B) " 等を除去して比較）
        normalized_user = self._normalize_answer(user_answer)
        normalized_correct = self._normalize_answer(correct_answer)

        is_correct = normalized_user == normalized_correct

        if is_correct:
            explanation = "Correct! Well done."
            score = 1.0
        else:
            explanation = f"The correct answer is: {correct_answer}"
            # 部分一致のスコア計算
            user_words = set(normalized_user.lower().split())
            correct_words = set(normalized_correct.lower().split())
            if correct_words:
                overlap = len(user_words & correct_words) / len(correct_words)
                score = round(overlap * 0.5, 2)  # 部分一致は最大0.5
            else:
                score = 0.0

        return ComprehensionResult(
            is_correct=is_correct,
            score=score,
            explanation=explanation,
            correct_answer=correct_answer,
        )

    async def check_summary(
        self,
        material_id: str,
        user_summary: str,
        original_text: str,
    ) -> SummaryResult:
        """
        サマリーの質を評価

        Claude Haikuを使用して、ユーザーのサマリーが元のテキストの
        要点をどの程度カバーしているかを評価する。

        Args:
            material_id: 素材ID
            user_summary: ユーザーが書いたサマリー
            original_text: 元のリスニング素材テキスト

        Returns:
            SummaryResult: サマリー評価結果
        """
        system_prompt = build_summary_evaluation_prompt(original_text)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Evaluate this summary:\n\n"
                    f"{user_summary}\n\n"
                    f"Return the evaluation as JSON."
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

            return SummaryResult(
                score=min(max(float(result.get("score", 0.0)), 0.0), 1.0),
                feedback=result.get("feedback", ""),
                key_points_covered=result.get("key_points_covered", []),
                key_points_missed=result.get("key_points_missed", []),
            )

        except Exception as e:
            logger.error("サマリー評価エラー: %s", e)
            return self._fallback_summary_check(user_summary, original_text)

    def get_available_topics(self) -> list[dict]:
        """
        利用可能なビジネストピック一覧を返す

        Returns:
            カテゴリ・トピックのリスト
        """
        return COMPREHENSION_TOPICS

    # --- プライベートヘルパーメソッド ---

    def _normalize_answer(self, answer: str) -> str:
        """回答テキストを正規化"""
        text = answer.strip()
        # "A) ", "B) " 等の選択肢プレフィックスを除去
        if len(text) >= 3 and text[0].isalpha() and text[1] == ")" and text[2] == " ":
            text = text[3:]
        return text.strip()

    def _build_fallback_material(
        self,
        topic: str,
        difficulty: str,
        duration_minutes: int,
    ) -> ComprehensionMaterial:
        """フォールバック: 静的なリスニング素材"""
        return ComprehensionMaterial(
            material_id=str(uuid.uuid4()),
            topic=topic,
            text=(
                "Good morning, everyone. Thank you for joining today's meeting. "
                "I'd like to discuss our quarterly results and the outlook for next quarter. "
                "Overall, we've seen a 12% increase in revenue compared to last year, "
                "which is above our target of 10%. "
                "Our customer satisfaction scores have also improved, reaching 4.3 out of 5. "
                "However, we've identified some areas where we need to improve. "
                "First, our response time to customer inquiries has increased by about 15%. "
                "Second, we've seen higher than expected employee turnover in the engineering team. "
                "For next quarter, I propose we focus on three key areas: "
                "improving our customer support infrastructure, "
                "implementing a retention program for technical staff, "
                "and launching our new product line in the Asian market. "
                "I'd like to hear your thoughts on these priorities. "
                "Shall we start with the customer support discussion?"
            ),
            difficulty=difficulty,
            duration_seconds=duration_minutes * 60,
            vocabulary=[
                VocabularyItem(
                    word="quarterly results",
                    definition="Financial performance data reported every three months",
                    example="Let's discuss our quarterly results in the meeting.",
                    level="B2",
                ),
                VocabularyItem(
                    word="outlook",
                    definition="Expected future situation or forecast",
                    example="The outlook for next quarter is positive.",
                    level="B2",
                ),
                VocabularyItem(
                    word="customer satisfaction scores",
                    definition="Numerical ratings of how happy customers are with a service",
                    example="Our customer satisfaction scores reached 4.3 out of 5.",
                    level="B1",
                ),
                VocabularyItem(
                    word="employee turnover",
                    definition="Rate at which employees leave and are replaced",
                    example="High employee turnover can be costly for the company.",
                    level="B2",
                ),
                VocabularyItem(
                    word="retention program",
                    definition="Initiatives designed to keep employees from leaving",
                    example="We're implementing a retention program for our technical staff.",
                    level="C1",
                ),
            ],
            key_points=[
                "Revenue increased 12%, above the 10% target",
                "Customer satisfaction improved to 4.3/5",
                "Customer inquiry response time increased 15%",
                "Higher than expected engineering team turnover",
                "Three focus areas for next quarter: support, retention, Asian market launch",
            ],
        )

    def _build_fallback_questions(self, text: str) -> list[ComprehensionQuestion]:
        """フォールバック: 基本的な理解度問題"""
        return [
            ComprehensionQuestion(
                question_id=str(uuid.uuid4()),
                question_text="What was the main topic of this passage?",
                question_type="multiple_choice",
                options=[
                    "A) A new product announcement",
                    "B) Quarterly business results and future priorities",
                    "C) An employee training program",
                    "D) A customer complaint resolution",
                ],
                correct_answer="B) Quarterly business results and future priorities",
            ),
            ComprehensionQuestion(
                question_id=str(uuid.uuid4()),
                question_text="What area of concern was mentioned?",
                question_type="multiple_choice",
                options=[
                    "A) Declining revenue",
                    "B) Product quality issues",
                    "C) Increased customer inquiry response time",
                    "D) Office relocation problems",
                ],
                correct_answer="C) Increased customer inquiry response time",
            ),
            ComprehensionQuestion(
                question_id=str(uuid.uuid4()),
                question_text="Write a brief summary of the main points discussed in this passage.",
                question_type="summary",
                options=None,
                correct_answer="The passage discusses positive quarterly results with revenue growth above target and improved customer satisfaction, along with areas for improvement including response times and employee turnover, and outlines three priorities for the next quarter.",
            ),
        ]

    def _fallback_summary_check(
        self,
        user_summary: str,
        original_text: str,
    ) -> SummaryResult:
        """フォールバック: キーワードベースのサマリー評価"""
        # キーワードの存在チェック
        key_terms = [
            "revenue", "increase", "customer", "satisfaction",
            "response time", "turnover", "next quarter", "priorities",
        ]

        user_lower = user_summary.lower()
        covered = [term for term in key_terms if term in user_lower]
        missed = [term for term in key_terms if term not in user_lower]

        coverage = len(covered) / len(key_terms) if key_terms else 0.0

        # 長さチェック
        word_count = len(user_summary.split())
        length_score = 1.0
        if word_count < 20:
            length_score = 0.5
        elif word_count > 200:
            length_score = 0.7

        score = round(coverage * 0.7 + length_score * 0.3, 2)

        if score >= 0.7:
            feedback = "Good summary! You captured the main points well."
        elif score >= 0.4:
            feedback = "Decent effort, but some key points were missed. Try to include more specific details."
        else:
            feedback = "Your summary needs more detail. Listen again and focus on the main discussion points."

        return SummaryResult(
            score=score,
            feedback=feedback,
            key_points_covered=[f"Mentioned: {term}" for term in covered],
            key_points_missed=[f"Missing: {term}" for term in missed],
        )


# シングルトンインスタンス
comprehension_service = ComprehensionService()
