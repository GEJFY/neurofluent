"""もごもごイングリッシュ（Mogomogo）スキーマ - リンキング・リダクション訓練"""

from pydantic import BaseModel, Field


class MogomogoExercise(BaseModel):
    """もごもごエクササイズ - 音声変化パターン練習問題"""

    exercise_id: str = Field(description="エクササイズの一意識別子")
    pattern_type: str = Field(
        description="パターン種別: linking, reduction, flapping, deletion, weak_form"
    )
    audio_text: str = Field(description="音声として読み上げるテキスト")
    ipa_original: str = Field(description="元のIPA表記（正式発音）")
    ipa_modified: str = Field(description="変化後のIPA表記（自然発音）")
    explanation: str = Field(description="音声変化の解説")
    practice_sentence: str = Field(description="練習用の文")
    difficulty: str = Field(default="B2", description="難易度レベル")


class DictationRequest(BaseModel):
    """ディクテーションチェックリクエスト"""

    exercise_id: str = Field(description="エクササイズID")
    user_text: str = Field(min_length=1, description="ユーザーが聞き取ったテキスト")
    original_text: str = Field(min_length=1, description="元のテキスト")


class DictationResult(BaseModel):
    """ディクテーション結果"""

    accuracy: float = Field(ge=0.0, le=1.0, description="全体精度（0.0-1.0）")
    missed_words: list[str] = Field(default_factory=list, description="聞き取れなかった単語リスト")
    identified_patterns: list[str] = Field(
        default_factory=list,
        description="識別された音声変化パターン"
    )
    score: float = Field(ge=0.0, le=1.0, description="総合スコア")
    feedback: str = Field(description="フィードバックコメント")


class IpaExample(BaseModel):
    """IPA表記の例"""

    original: str
    modified: str
    word: str


class SoundPatternInfo(BaseModel):
    """音声変化パターン情報"""

    type: str = Field(description="パターン種別")
    name_en: str = Field(description="英語名")
    name_ja: str = Field(description="日本語名")
    description: str = Field(description="パターンの説明")
    examples: list[str] = Field(default_factory=list, description="テキスト例")
    ipa_examples: list[IpaExample] = Field(
        default_factory=list, description="IPA表記例"
    )


class MogomogoProgressItem(BaseModel):
    """パターン別習熟度"""

    pattern_type: str
    pattern_name: str
    accuracy: float = 0.0
    practice_count: int = 0
    mastery_level: str = Field(
        default="beginner",
        description="習熟レベル: beginner, developing, proficient, mastered"
    )


class MogomogoProgress(BaseModel):
    """もごもご習熟度レスポンス"""

    overall_accuracy: float = 0.0
    total_practice_count: int = 0
    patterns: list[MogomogoProgressItem] = Field(default_factory=list)
