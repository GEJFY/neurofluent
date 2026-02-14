"""パターンプラクティススキーマ - ビジネス英語パターン練習用"""

from pydantic import BaseModel, Field


class PatternExercise(BaseModel):
    """パターン練習エクササイズ"""

    pattern_id: str = Field(description="パターンの一意識別子")
    pattern_template: str = Field(
        description="パターンテンプレート（例: 'I would like to ___ the meeting.'）"
    )
    example_sentence: str = Field(description="パターンを使った例文")
    japanese_hint: str = Field(description="日本語のヒント・説明")
    category: str = Field(
        description="カテゴリ: meeting, negotiation, presentation, email, discussion, general"
    )
    difficulty: str = Field(description="難易度レベル（A2, B1, B2, C1, C2）")
    fill_in_blank: bool = Field(
        default=False,
        description="穴埋め形式かどうか"
    )

    model_config = {"from_attributes": True}


class PatternCheckRequest(BaseModel):
    """パターン回答チェックリクエスト"""

    pattern_id: str = Field(description="パターンID")
    user_answer: str = Field(min_length=1, description="ユーザーの回答")
    expected: str = Field(min_length=1, description="期待される回答")


class PatternCheckResult(BaseModel):
    """パターン回答チェック結果"""

    is_correct: bool = Field(description="正解かどうか")
    score: float = Field(ge=0.0, le=1.0, description="正答スコア（0.0〜1.0）")
    corrected: str = Field(description="修正後の正解文")
    explanation: str = Field(description="解説・フィードバック")
    usage_tip: str = Field(
        default="",
        description="実践的な使用アドバイス"
    )

    model_config = {"from_attributes": True}


class PatternCategory(BaseModel):
    """パターンカテゴリ情報"""

    category: str = Field(description="カテゴリID")
    name: str = Field(description="カテゴリ表示名")
    description: str = Field(description="カテゴリの説明")
    pattern_count: int = Field(description="カテゴリ内のパターン数")

    model_config = {"from_attributes": True}


class PatternProgress(BaseModel):
    """パターン習熟度サマリー"""

    category: str = Field(description="カテゴリ")
    total_patterns: int = Field(description="総パターン数")
    understood: int = Field(default=0, description="理解済みパターン数")
    drilling: int = Field(default=0, description="反復練習中のパターン数")
    acquired: int = Field(default=0, description="習得済みパターン数")
    average_accuracy: float = Field(default=0.0, description="平均正答率")
    total_practice_count: int = Field(default=0, description="総練習回数")

    model_config = {"from_attributes": True}
