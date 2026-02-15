"""音声パターンモデル - 発音パターンの習熟度を管理"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SoundPatternMastery(Base):
    """音声パターン習熟度テーブル - リンキング・リダクション等の発音パターン追跡"""

    __tablename__ = "sound_pattern_mastery"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    pattern_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="パターン種別: linking, reduction, flapping, deletion, weak_form",
    )
    pattern_text: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="対象テキスト（例: 'want to' -> 'wanna'）"
    )
    ipa_notation: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="IPA表記（例: /wɑːnə/）"
    )
    accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    practice_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<SoundPatternMastery user={self.user_id} type={self.pattern_type} accuracy={self.accuracy}>"
