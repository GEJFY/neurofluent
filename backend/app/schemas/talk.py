"""会話練習(Talk)スキーマ - セッション・メッセージ・フィードバック"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackData(BaseModel):
    """AIフィードバックの構造化データ"""

    grammar_errors: list[dict] = Field(
        default_factory=list,
        description="文法エラーのリスト（original, corrected, explanation）",
    )
    expression_upgrades: list[dict] = Field(
        default_factory=list,
        description="より自然な表現への改善提案（original, upgraded, context）",
    )
    pronunciation_notes: list[str] = Field(
        default_factory=list,
        description="発音に関するメモ",
    )
    positive_feedback: str = Field(
        default="",
        description="良かった点のフィードバック",
    )
    vocabulary_level: str = Field(
        default="B2",
        description="使用語彙のCEFRレベル推定",
    )


class TalkStartRequest(BaseModel):
    """会話セッション開始リクエスト"""

    mode: str = Field(
        description="会話モード（meeting, presentation, negotiation, small_talk, interview, phone_call）"
    )
    scenario_id: str | None = Field(
        default=None,
        description="シナリオID（scenarios.pyの詳細シナリオを使用する場合）",
    )
    scenario_description: str | None = Field(
        default=None,
        description="シナリオの詳細説明（カスタムシナリオ用）",
    )


class TalkMessageRequest(BaseModel):
    """会話メッセージ送信リクエスト"""

    session_id: uuid.UUID
    content: str = Field(min_length=1)


class TalkMessageResponse(BaseModel):
    """会話メッセージレスポンス"""

    id: uuid.UUID
    role: str
    content: str
    feedback: FeedbackData | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionResponse(BaseModel):
    """セッション詳細レスポンス（メッセージ含む）"""

    id: uuid.UUID
    mode: str
    scenario_description: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    duration_seconds: int | None = None
    overall_score: dict | None = None
    messages: list[TalkMessageResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    """セッション一覧レスポンス（概要のみ）"""

    id: uuid.UUID
    mode: str
    started_at: datetime
    duration_seconds: int | None = None

    model_config = {"from_attributes": True}
