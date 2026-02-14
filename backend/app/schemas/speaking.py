"""瞬間英作文（Flash Translation）スキーマ"""

from pydantic import BaseModel, Field


class FlashExercise(BaseModel):
    """フラッシュ翻訳エクササイズ"""

    exercise_id: str = Field(description="エクササイズの一意識別子")
    japanese: str = Field(description="翻訳元の日本語文")
    english_target: str = Field(description="目標英訳")
    acceptable_alternatives: list[str] = Field(
        default_factory=list,
        description="許容される代替英訳",
    )
    key_pattern: str = Field(description="注目する文法・表現パターン")
    difficulty: str = Field(description="難易度レベル（A2, B1, B2, C1, C2）")
    time_limit_seconds: int = Field(default=15, description="制限時間（秒）")
    hints: list[str] = Field(
        default_factory=list,
        description="ヒントのリスト",
    )


class FlashCheckRequest(BaseModel):
    """フラッシュ翻訳回答チェックリクエスト"""

    exercise_id: str
    user_answer: str = Field(min_length=1)
    target: str = Field(min_length=1)


class FlashCheckResponse(BaseModel):
    """フラッシュ翻訳回答チェックレスポンス"""

    is_correct: bool
    score: float = Field(ge=0.0, le=1.0, description="正答スコア（0.0〜1.0）")
    corrected: str = Field(description="修正後の英文")
    explanation: str = Field(description="解説・フィードバック")
    review_item_created: bool = Field(
        default=False,
        description="復習アイテムが作成されたか",
    )
