"""初期スキーマ作成

Revision ID: 001_initial
Revises:
Create Date: 2026-02-14

全テーブル: users, conversation_sessions, conversation_messages,
review_items, daily_stats, api_usage_log
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === pgvector拡張 ===
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # === users テーブル ===
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(512), nullable=False),
        sa.Column("entra_id", sa.String(255), unique=True, nullable=True),
        sa.Column(
            "native_language", sa.String(10), nullable=False, server_default="ja"
        ),
        sa.Column("target_level", sa.String(10), nullable=False, server_default="C1"),
        sa.Column(
            "daily_goal_minutes", sa.Integer(), nullable=False, server_default="15"
        ),
        sa.Column(
            "subscription_plan", sa.String(50), nullable=False, server_default="free"
        ),
        sa.Column(
            "api_usage_monthly", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("api_usage_reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # === conversation_sessions テーブル ===
    op.create_table(
        "conversation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("mode", sa.String(50), nullable=False),
        sa.Column("scenario_description", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("overall_score", postgresql.JSONB(), nullable=True),
        sa.Column("api_tokens_used", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # === conversation_messages テーブル ===
    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversation_sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("audio_blob_url", sa.String(1024), nullable=True),
        sa.Column("feedback", postgresql.JSONB(), nullable=True),
        sa.Column("pronunciation_score", postgresql.JSONB(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # === review_items テーブル ===
    op.create_table(
        "review_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("item_type", sa.String(50), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column(
            "source_session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversation_sessions.id"),
            nullable=True,
        ),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "next_review_at", sa.DateTime(timezone=True), nullable=True, index=True
        ),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_quality", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("stability", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default="0.3"),
    )

    # === daily_stats テーブル ===
    op.create_table(
        "daily_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("practice_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "sessions_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "reviews_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "new_expressions_learned",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("grammar_accuracy", sa.Float(), nullable=True),
        sa.Column("avg_response_time_ms", sa.Integer(), nullable=True),
        sa.Column("listening_speed_max", sa.Float(), nullable=True),
        sa.Column("pronunciation_avg_score", sa.Float(), nullable=True),
        sa.Column("weak_patterns", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_stats_user_date"),
    )

    # === api_usage_log テーブル ===
    op.create_table(
        "api_usage_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("api_provider", sa.String(50), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("audio_seconds", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "estimated_cost_usd", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("api_usage_log")
    op.drop_table("daily_stats")
    op.drop_table("review_items")
    op.drop_table("conversation_messages")
    op.drop_table("conversation_sessions")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
