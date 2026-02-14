"""復習アイテムモデル - 間隔反復学習(FSRS)のカード管理"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReviewItem(Base):
    """復習アイテムテーブル - FSRSアルゴリズムで管理される学習カード"""

    __tablename__ = "review_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversation_sessions.id"),
        nullable=True,
    )
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # FSRS固有フィールド（安定度・難易度を保持）
    stability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)

    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="review_items")
    source_session: Mapped["ConversationSession | None"] = relationship(
        "ConversationSession", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ReviewItem {self.id} type={self.item_type}>"
