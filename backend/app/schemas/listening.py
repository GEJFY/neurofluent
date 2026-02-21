"""リスニング・シャドーイング・発音スキーマ - 音声関連エンドポイント用"""

from pydantic import BaseModel, Field


class PronunciationWordScore(BaseModel):
    """単語レベルの発音スコア"""

    word: str = Field(description="対象の単語")
    accuracy_score: float = Field(
        ge=0.0, le=100.0, description="発音正確度スコア（0-100）"
    )
    error_type: str | None = Field(
        default=None,
        description="エラー種別: None, Mispronunciation, Omission, Insertion, UnexpectedBreak, MissingBreak, Monotone",
    )


class PronunciationResult(BaseModel):
    """発音評価結果"""

    accuracy_score: float = Field(
        ge=0.0, le=100.0, description="発音正確度スコア（0-100）"
    )
    fluency_score: float = Field(ge=0.0, le=100.0, description="流暢さスコア（0-100）")
    prosody_score: float = Field(ge=0.0, le=100.0, description="韻律スコア（0-100）")
    completeness_score: float = Field(
        ge=0.0, le=100.0, description="完全性スコア（0-100）"
    )
    word_scores: list[PronunciationWordScore] = Field(
        default_factory=list, description="単語レベルのスコアリスト"
    )

    model_config = {"from_attributes": True}


class ShadowingMaterial(BaseModel):
    """シャドーイング教材"""

    text: str = Field(description="シャドーイング対象テキスト（2-4文のビジネス英語）")
    suggested_speeds: list[float] = Field(
        default_factory=lambda: [0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
        description="推奨再生速度リスト",
    )
    key_phrases: list[str] = Field(
        default_factory=list, description="重要フレーズリスト"
    )
    vocabulary_notes: list[dict] = Field(
        default_factory=list, description="語彙注釈リスト（word, meaning, example）"
    )
    difficulty: str = Field(
        default="intermediate", description="難易度: beginner, intermediate, advanced"
    )

    model_config = {"from_attributes": True}


class ShadowingStartRequest(BaseModel):
    """シャドーイング開始リクエスト"""

    topic: str | None = Field(
        default=None,
        description="トピック: business_meeting, earnings_call, team_discussion, client_presentation, casual_networking",
    )
    difficulty: str = Field(
        default="intermediate", description="難易度: beginner, intermediate, advanced"
    )
    mode: str = Field(
        default="standard",
        description="モード: standard（通常）, chunk（チャンク分割）, parallel（パラレルリーディング）",
    )
    accent: str = Field(
        default="us",
        description="アクセント: us, uk, india, singapore, australia, ireland, hongkong, southafrica",
    )
    gender: str = Field(
        default="female",
        description="話者の性別: female, male",
    )
    environment: str = Field(
        default="clean",
        description="環境音: clean, phone_call, video_call, office, cafe, conference_room",
    )


class ShadowingEvaluateRequest(BaseModel):
    """シャドーイング評価リクエスト（音声ファイルと共に送信）"""

    reference_text: str = Field(min_length=1, description="リファレンステキスト")
    speed: float = Field(
        default=1.0, ge=0.5, le=2.0, description="シャドーイング時の再生速度"
    )


class ShadowingResult(BaseModel):
    """シャドーイング評価結果"""

    overall_score: float = Field(ge=0.0, le=100.0, description="総合スコア（0-100）")
    accuracy: float = Field(ge=0.0, le=100.0, description="発音正確度スコア")
    fluency: float = Field(ge=0.0, le=100.0, description="流暢さスコア")
    prosody: float = Field(ge=0.0, le=100.0, description="韻律スコア")
    completeness: float = Field(ge=0.0, le=100.0, description="完全性スコア")
    speed_achieved: float = Field(description="実際に達成した速度倍率")
    word_scores: list[PronunciationWordScore] = Field(
        default_factory=list, description="単語レベルのスコアリスト"
    )
    areas_to_improve: list[str] = Field(
        default_factory=list, description="改善すべきポイントのリスト"
    )

    model_config = {"from_attributes": True}


class TTSRequest(BaseModel):
    """Text-to-Speechリクエスト"""

    text: str = Field(min_length=1, max_length=5000, description="変換対象テキスト")
    voice: str = Field(
        default="en-US-JennyMultilingualNeural",
        description="音声名（Azure Neural Voice）。accentが指定された場合は無視。",
    )
    speed: float = Field(
        default=1.0, ge=0.5, le=2.0, description="再生速度（0.5x - 2.0x）"
    )
    accent: str | None = Field(
        default=None,
        description="アクセント: us, uk, india, singapore, australia, ireland, hongkong, southafrica",
    )
    gender: str = Field(
        default="female",
        description="話者の性別: female, male",
    )
    environment: str = Field(
        default="clean",
        description="環境音: clean, phone_call, video_call, office, cafe, conference_room",
    )
