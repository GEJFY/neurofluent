"""学習統計モデル - 日次パフォーマンスデータの蓄積"""

import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DailyStat(Base):
    """日次統計テーブル - ユーザーごとの日別学習実績"""

    __tablename__ = "daily_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    practice_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sessions_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reviews_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_expressions_learned: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    grammar_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    listening_speed_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    pronunciation_avg_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    weak_patterns: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # リレーション
    user: Mapped["User"] = relationship("User", back_populates="daily_stats")

    def __repr__(self) -> str:
        return f"<DailyStat user={self.user_id} date={self.date}>"
