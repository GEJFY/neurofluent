"""発音トレーニング（Pronunciation）スキーマ - 音素・韻律の練習・評価

日本語話者に特有の発音問題（/r/-/l/, /θ/-/s/, /v/-/b/等）に
フォーカスしたミニマルペア、舌を鍛える練習、文練習の
エクササイズ生成と評価のためのスキーマ。
"""

from pydantic import BaseModel, Field


class PronunciationExercise(BaseModel):
    """発音エクササイズ"""

    exercise_id: str = Field(description="エクササイズの一意識別子")
    target_phoneme: str = Field(description="対象音素 (例: /r/-/l/, /θ/-/s/)")
    exercise_type: str = Field(
        description="エクササイズ種別: minimal_pair, tongue_twister, sentence"
    )
    word_a: str = Field(description="単語A（ミニマルペアの場合）またはメイン単語")
    word_b: str | None = Field(default=None, description="単語B（ミニマルペアの場合）")
    sentence: str = Field(description="練習文")
    ipa: str = Field(description="IPA表記")
    audio_url: str | None = Field(default=None, description="音声URL（TTS生成の場合）")
    difficulty: str = Field(default="B2", description="難易度レベル")
    tip: str = Field(default="", description="発音のコツ（日本語話者向け）")


class PhonemeResult(BaseModel):
    """音素評価結果"""

    target_phoneme: str = Field(description="評価対象の音素")
    accuracy: float = Field(ge=0.0, le=1.0, description="音素精度スコア")
    is_correct: bool = Field(description="正しく発音できたか")
    feedback: str = Field(description="フィードバックコメント")
    common_error_pattern: str = Field(
        default="", description="該当する一般的な間違いパターン"
    )


class PronunciationEvaluateRequest(BaseModel):
    """発音評価リクエスト（メタデータ部分）"""

    target_phoneme: str = Field(description="評価対象の音素")
    reference_text: str = Field(description="参照テキスト（発話すべきテキスト）")
    exercise_id: str | None = Field(default=None, description="エクササイズID")


class ProsodyExercise(BaseModel):
    """韻律エクササイズ - ストレス・リズム・イントネーション"""

    exercise_id: str = Field(description="エクササイズの一意識別子")
    sentence: str = Field(description="練習文")
    stress_pattern: str = Field(description="ストレスパターン (例: 'oOo' = 弱強弱)")
    intonation_type: str = Field(
        description="イントネーション種別: rising, falling, rise-fall, fall-rise"
    )
    audio_url: str | None = Field(default=None, description="音声URL")
    explanation: str = Field(default="", description="パターンの解説")
    context: str = Field(default="", description="使用場面の説明")


class JapaneseSpeakerPhoneme(BaseModel):
    """日本語話者の音素問題"""

    phoneme_pair: str = Field(description="音素ペア (例: /r/-/l/)")
    description_ja: str = Field(description="日本語での問題説明")
    description_en: str = Field(default="", description="英語での問題説明")
    examples: list[str] = Field(default_factory=list, description="例文リスト")
    practice_words: list[str] = Field(
        default_factory=list, description="練習用単語リスト"
    )
    common_mistake: str = Field(default="", description="よくある間違いの説明")
    tip: str = Field(default="", description="発音のコツ")


class PronunciationProgressItem(BaseModel):
    """音素別進捗"""

    phoneme: str
    accuracy: float = 0.0
    practice_count: int = 0
    trend: str = "stable"


class PronunciationOverallProgress(BaseModel):
    """発音全体の進捗"""

    overall_accuracy: float = 0.0
    total_evaluations: int = 0
    phoneme_progress: list[PronunciationProgressItem] = Field(default_factory=list)
    strongest_phonemes: list[str] = Field(default_factory=list)
    weakest_phonemes: list[str] = Field(default_factory=list)
