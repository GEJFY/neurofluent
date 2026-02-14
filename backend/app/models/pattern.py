"""パターン練習モデル - ビジネス英語パターンの習熟度を管理"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PatternMastery(Base):
    """パターン習熟度テーブル - ユーザーごとのパターン練習進捗を追跡"""

    __tablename__ = "pattern_mastery"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    pattern_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    pattern_category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    skill_stage: Mapped[str] = mapped_column(
        String(20), nullable=False, default="understood",
        comment="習熟段階: understood(理解済み), drilling(反復練習中), acquired(習得済み)"
    )
    practice_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    accuracy_rate: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    last_practiced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    first_used_in_freetalk: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="フリートークで初めて使用された日時（習得の指標）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PatternMastery user={self.user_id} pattern={self.pattern_id} stage={self.skill_stage}>"
