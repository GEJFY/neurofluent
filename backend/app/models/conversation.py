"""会話セッション・メッセージモデル - AIとの会話履歴を管理"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConversationSession(Base):
    """会話セッションテーブル - 各練習セッションのメタデータ"""

    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    mode: Mapped[str] = mapped_column(String(50), nullable=False)
    scenario_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_score: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    api_tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="conversation_sessions")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        "ConversationMessage",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<ConversationSession {self.id} mode={self.mode}>"


class ConversationMessage(Base):
    """会話メッセージテーブル - セッション内の各メッセージ"""

    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    audio_blob_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pronunciation_score: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # リレーション
    session: Mapped["ConversationSession"] = relationship(
        "ConversationSession", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage {self.id} role={self.role}>"
