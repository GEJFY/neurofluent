"""リスニングコンプリヘンション（Comprehension）スキーマ - 聴解力訓練

ビジネス英語のリスニング素材の生成、理解度テスト（選択式・サマリー）、
回答評価のためのスキーマ。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class VocabularyItem(BaseModel):
    """素材内の語彙アイテム"""

    word: str = Field(description="単語・フレーズ")
    definition: str = Field(description="定義・意味")
    example: str = Field(default="", description="使用例")
    level: str = Field(default="B2", description="語彙レベル")


class ComprehensionMaterial(BaseModel):
    """リスニング素材"""

    material_id: str = Field(description="素材の一意識別子")
    topic: str = Field(description="トピック")
    text: str = Field(description="リスニングテキスト（スクリプト）")
    difficulty: str = Field(description="難易度: beginner, intermediate, advanced")
    duration_seconds: int = Field(description="推定音声長（秒）")
    vocabulary: list[VocabularyItem] = Field(
        default_factory=list, description="重要語彙リスト"
    )
    key_points: list[str] = Field(default_factory=list, description="要点リスト")


class ComprehensionQuestion(BaseModel):
    """理解度テスト問題"""

    question_id: str = Field(description="問題の一意識別子")
    question_text: str = Field(description="問題文")
    question_type: str = Field(description="問題種別: multiple_choice, summary")
    options: list[str] | None = Field(
        default=None, description="選択肢リスト（multiple_choiceの場合）"
    )
    correct_answer: str = Field(description="正解")


class ComprehensionAnswerRequest(BaseModel):
    """回答リクエスト"""

    question_id: str = Field(description="問題ID")
    user_answer: str = Field(min_length=1, description="ユーザーの回答")
    correct_answer: str = Field(description="正解テキスト")


class ComprehensionResult(BaseModel):
    """回答結果"""

    is_correct: bool = Field(description="正解かどうか")
    score: float = Field(ge=0.0, le=1.0, description="スコア")
    explanation: str = Field(description="解説")
    correct_answer: str = Field(description="正解テキスト")


class SummaryCheckRequest(BaseModel):
    """サマリーチェックリクエスト"""

    material_id: str = Field(description="素材ID")
    user_summary: str = Field(min_length=10, description="ユーザーが書いたサマリー")


class SummaryResult(BaseModel):
    """サマリー評価結果"""

    score: float = Field(ge=0.0, le=1.0, description="サマリースコア")
    feedback: str = Field(description="フィードバック")
    key_points_covered: list[str] = Field(
        default_factory=list, description="カバーされた要点"
    )
    key_points_missed: list[str] = Field(
        default_factory=list, description="見落とされた要点"
    )


class ComprehensionHistoryItem(BaseModel):
    """コンプリヘンション履歴アイテム"""

    material_id: str
    topic: str
    difficulty: str
    score: float
    completed_at: datetime
    questions_correct: int
    questions_total: int


class ComprehensionHistory(BaseModel):
    """コンプリヘンション履歴"""

    items: list[ComprehensionHistoryItem] = Field(default_factory=list)
    total_sessions: int = 0
    avg_score: float = 0.0
