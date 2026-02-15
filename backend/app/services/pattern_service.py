"""パターンプラクティスサービス - ビジネス英語パターンの生成・評価

Claude Haikuを使用してユーザーのレベルと弱点に基づいた
パターン練習エクササイズを動的に生成し、回答を評価する。
"""

import logging
import random

from app.prompts.pattern_practice import (
    BUSINESS_PATTERNS,
    build_pattern_check_prompt,
    build_pattern_generation_prompt,
)
from app.schemas.pattern import (
    PatternCategory,
    PatternCheckResult,
    PatternExercise,
)
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)

# カテゴリ定義
PATTERN_CATEGORIES = [
    PatternCategory(
        category="meeting",
        name="Meeting Facilitation",
        description="会議の進行・参加に必要な英語パターン。議題管理、意見表明、合意形成など。",
        pattern_count=len(BUSINESS_PATTERNS.get("meeting", [])),
    ),
    PatternCategory(
        category="negotiation",
        name="Business Negotiation",
        description="ビジネス交渉に使うパターン。提案、条件提示、譲歩、合意形成など。",
        pattern_count=len(BUSINESS_PATTERNS.get("negotiation", [])),
    ),
    PatternCategory(
        category="presentation",
        name="Presentation Skills",
        description="プレゼンテーションの構成パターン。導入、データ説明、Q&A、結論など。",
        pattern_count=len(BUSINESS_PATTERNS.get("presentation", [])),
    ),
    PatternCategory(
        category="email",
        name="Email Communication",
        description="ビジネスメールの定型表現。依頼、フォローアップ、お詫び、スケジュール調整など。",
        pattern_count=len(BUSINESS_PATTERNS.get("email", [])),
    ),
    PatternCategory(
        category="discussion",
        name="Discussion & Opinion",
        description="議論・意見表明のパターン。賛成・反対、根拠提示、要約など。",
        pattern_count=len(BUSINESS_PATTERNS.get("discussion", [])),
    ),
    PatternCategory(
        category="general",
        name="General Business",
        description="汎用ビジネス英語パターン。報告、質問、提案、コミュニケーション全般。",
        pattern_count=len(BUSINESS_PATTERNS.get("general", [])),
    ),
]


class PatternService:
    """ビジネス英語パターンの生成・評価を管理するサービス"""

    def get_categories(self) -> list[PatternCategory]:
        """
        パターンカテゴリ一覧を取得

        Returns:
            PatternCategoryのリスト
        """
        return PATTERN_CATEGORIES

    async def get_patterns(
        self,
        category: str | None = None,
        user_level: str = "B2",
        count: int = 10,
        weak_patterns: list[str] | None = None,
    ) -> list[PatternExercise]:
        """
        パターン練習エクササイズを取得

        まず組み込みパターンから適切なものを選択し、
        足りない場合はClaude Haikuで動的に生成する。

        Args:
            category: パターンカテゴリ（Noneの場合はランダムに混合）
            user_level: ユーザーのCEFRレベル
            count: 取得するエクササイズ数（1-20）
            weak_patterns: ユーザーの弱点パターンリスト

        Returns:
            PatternExerciseのリスト
        """
        count = max(1, min(20, count))

        # 組み込みパターンからの選択を試行
        builtin_exercises = self._select_from_builtin(
            category=category,
            user_level=user_level,
            count=count,
        )

        if len(builtin_exercises) >= count:
            return builtin_exercises[:count]

        # 不足分をClaude Haikuで動的生成
        remaining = count - len(builtin_exercises)
        target_category = category or "general"

        try:
            generated = await self._generate_with_ai(
                category=target_category,
                user_level=user_level,
                count=remaining,
                weak_patterns=weak_patterns,
            )
            return builtin_exercises + generated

        except Exception as e:
            logger.error("パターン動的生成でエラー: %s", e)
            # エラー時は組み込みパターンのみ返す
            return builtin_exercises

    def _select_from_builtin(
        self,
        category: str | None,
        user_level: str,
        count: int,
    ) -> list[PatternExercise]:
        """
        組み込みパターンから適切なエクササイズを選択

        ユーザーのCEFRレベルに近いパターンを優先的に選択。
        """
        # CEFRレベルの順序マップ
        cefr_order = {"A2": 0, "B1": 1, "B2": 2, "C1": 3, "C2": 4}
        user_cefr_idx = cefr_order.get(user_level, 2)

        if category and category in BUSINESS_PATTERNS:
            pool = BUSINESS_PATTERNS[category]
        else:
            # 全カテゴリから混合
            pool = []
            for cat_patterns in BUSINESS_PATTERNS.values():
                pool.extend(cat_patterns)

        # ユーザーレベルに合ったパターンをフィルタリング
        # レベル±1の範囲を許容
        suitable = []
        for pattern in pool:
            pattern_cefr_idx = cefr_order.get(pattern.get("cefr", "B2"), 2)
            if abs(pattern_cefr_idx - user_cefr_idx) <= 1:
                suitable.append(pattern)

        # 適切なパターンがない場合は全パターンから選択
        if not suitable:
            suitable = pool

        # ランダムに選択
        selected = random.sample(suitable, min(count, len(suitable)))

        # PatternExerciseに変換
        exercises = []
        for pattern in selected:
            # テンプレートに___が含まれていれば穴埋め形式
            is_fill_in_blank = "___" in pattern.get("template", "")

            exercises.append(
                PatternExercise(
                    pattern_id=pattern["id"],
                    pattern_template=pattern["template"],
                    example_sentence=pattern["example"],
                    japanese_hint=pattern["japanese"],
                    category=self._get_category_from_id(pattern["id"]),
                    difficulty=pattern.get("cefr", user_level),
                    fill_in_blank=is_fill_in_blank,
                )
            )

        return exercises

    def _get_category_from_id(self, pattern_id: str) -> str:
        """パターンIDからカテゴリを推定"""
        prefix_map = {
            "mtg": "meeting",
            "neg": "negotiation",
            "prs": "presentation",
            "eml": "email",
            "dsc": "discussion",
            "gen": "general",
        }
        prefix = pattern_id.split("-")[0] if "-" in pattern_id else ""
        return prefix_map.get(prefix, "general")

    async def _generate_with_ai(
        self,
        category: str,
        user_level: str,
        count: int,
        weak_patterns: list[str] | None = None,
    ) -> list[PatternExercise]:
        """Claude Haikuでパターンエクササイズを動的生成"""
        system_prompt = build_pattern_generation_prompt(
            category=category,
            level=user_level,
            weak_patterns=weak_patterns,
        )

        messages = [
            {
                "role": "user",
                "content": (
                    f"Generate {count} business English pattern exercises "
                    f"for the '{category}' category at CEFR {user_level} level."
                ),
            }
        ]

        result = await claude_service.chat_json(
            messages=messages,
            model="haiku",
            max_tokens=2048,
            system=system_prompt,
        )

        # リスト形式のレスポンスを処理
        exercises_data = (
            result if isinstance(result, list) else result.get("exercises", [])
        )

        exercises = []
        for item in exercises_data:
            try:
                exercises.append(
                    PatternExercise(
                        pattern_id=item.get("pattern_id", f"ai-{len(exercises):03d}"),
                        pattern_template=item.get("pattern_template", ""),
                        example_sentence=item.get("example_sentence", ""),
                        japanese_hint=item.get("japanese_hint", ""),
                        category=item.get("category", category),
                        difficulty=item.get("difficulty", user_level),
                        fill_in_blank=item.get("fill_in_blank", False),
                    )
                )
            except (ValueError, KeyError) as e:
                logger.warning("パターンエクササイズのパースに失敗: %s", e)
                continue

        return exercises

    async def check_pattern(
        self,
        pattern_id: str,
        user_answer: str,
        expected: str,
    ) -> PatternCheckResult:
        """
        パターン練習の回答を評価

        Claude Haikuを使用して、ユーザーの回答を
        期待される回答と比較・評価する。

        Args:
            pattern_id: パターンID
            user_answer: ユーザーの回答
            expected: 期待される回答

        Returns:
            PatternCheckResult: 評価結果
        """
        system_prompt = build_pattern_check_prompt()

        messages = [
            {
                "role": "user",
                "content": (
                    f"Evaluate this pattern exercise answer:\n\n"
                    f"Pattern ID: {pattern_id}\n"
                    f"Expected answer: {expected}\n"
                    f"User's answer: {user_answer}\n\n"
                    f"Evaluate and provide feedback in JSON format."
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

            return PatternCheckResult(
                is_correct=result.get("is_correct", False),
                score=result.get("score", 0.0),
                corrected=result.get("corrected", expected),
                explanation=result.get("explanation", ""),
                usage_tip=result.get("usage_tip", ""),
            )

        except (ValueError, KeyError) as e:
            logger.warning("パターンチェックでパースエラー: %s", e)
            # 簡易的な文字列比較によるフォールバック
            return self._fallback_check(user_answer, expected)

        except Exception as e:
            logger.error("パターンチェックで予期しないエラー: %s", e)
            return self._fallback_check(user_answer, expected)

    def _fallback_check(
        self,
        user_answer: str,
        expected: str,
    ) -> PatternCheckResult:
        """AI障害時のフォールバック評価（簡易文字列比較）"""
        user_clean = user_answer.strip().lower()
        expected_clean = expected.strip().lower()

        if user_clean == expected_clean:
            return PatternCheckResult(
                is_correct=True,
                score=1.0,
                corrected=expected,
                explanation="Perfect match!",
                usage_tip="Well done! Keep practicing this pattern in real conversations.",
            )

        # 部分一致チェック
        user_words = set(user_clean.split())
        expected_words = set(expected_clean.split())
        overlap = len(user_words & expected_words)
        total = max(len(expected_words), 1)
        score = overlap / total

        return PatternCheckResult(
            is_correct=score >= 0.7,
            score=round(score, 2),
            corrected=expected,
            explanation=(
                "Your answer partially matches the expected pattern. "
                "Please review the correct version above."
            ),
            usage_tip="Try to memorize the full pattern for use in business conversations.",
        )

    def get_business_patterns(self) -> dict[str, list[dict]]:
        """
        全カテゴリのビジネス英語パターンを取得

        Returns:
            カテゴリをキー、パターンリストを値とする辞書
        """
        return BUSINESS_PATTERNS


# シングルトンインスタンス
pattern_service = PatternService()
