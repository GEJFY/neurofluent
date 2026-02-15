"""ユーザーモデル - FluentEdge認証・プロフィール管理"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """ユーザーテーブル - 認証情報とプロフィール設定を保持"""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(512), nullable=False)
    entra_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    native_language: Mapped[str] = mapped_column(
        String(10), default="ja", nullable=False
    )
    target_level: Mapped[str] = mapped_column(String(10), default="C1", nullable=False)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    subscription_plan: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False
    )
    api_usage_monthly: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    api_usage_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # リレーション
    conversation_sessions: Mapped[list["ConversationSession"]] = relationship(
        "ConversationSession", back_populates="user", lazy="selectin"
    )
    review_items: Mapped[list["ReviewItem"]] = relationship(
        "ReviewItem", back_populates="user", lazy="selectin"
    )
    daily_stats: Mapped[list["DailyStat"]] = relationship(
        "DailyStat", back_populates="user", lazy="selectin"
    )
    api_usage_logs: Mapped[list["ApiUsageLog"]] = relationship(
        "ApiUsageLog", back_populates="user", lazy="selectin"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="user", uselist=False, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
