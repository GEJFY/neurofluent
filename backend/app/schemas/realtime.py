"""リアルタイム会話スキーマ - GPT Realtime API セッション管理用"""

from pydantic import BaseModel, Field


class RealtimeSessionConfig(BaseModel):
    """リアルタイムセッション設定（クライアントへ返却）"""

    ws_url: str = Field(description="WebSocket接続先URL")
    session_token: str = Field(description="セッション認証トークン")
    model: str = Field(description="使用モデル名")
    voice: str = Field(description="AI音声の種類")
    mode: str = Field(description="会話モード")
    instructions_summary: str = Field(
        description="システムプロンプトの概要（クライアント表示用）"
    )

    model_config = {"from_attributes": True}


class RealtimeStartRequest(BaseModel):
    """リアルタイム会話セッション開始リクエスト"""

    mode: str = Field(
        default="casual_chat",
        description="会話モード: casual_chat, meeting, debate, presentation_qa, negotiation, small_talk",
    )
    scenario_description: str | None = Field(
        default=None, description="シナリオの詳細説明（カスタムシナリオ用）"
    )


class ConversationMode(BaseModel):
    """利用可能な会話モード"""

    id: str = Field(description="モードID")
    name: str = Field(description="モード表示名")
    description: str = Field(description="モードの説明")
    available: bool = Field(description="現在利用可能かどうか")
    phase: str = Field(description="実装フェーズ（phase1, phase2, phase3）")

    model_config = {"from_attributes": True}


class ConversationModeList(BaseModel):
    """利用可能な会話モード一覧レスポンス"""

    modes: list[ConversationMode] = Field(
        default_factory=list, description="利用可能な会話モードのリスト"
    )
    current_phase: str = Field(default="phase2", description="現在の実装フェーズ")

    model_config = {"from_attributes": True}
