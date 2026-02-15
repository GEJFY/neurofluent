"""Phase 2-4 テーブル追加

Revision ID: 002_phase2_4
Revises: 001_initial
Create Date: 2026-02-14

追加テーブル: pattern_mastery, sound_pattern_mastery, subscriptions
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "002_phase2_4"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === pattern_mastery テーブル (Phase 2: ビジネス英語パターン習熟度) ===
    op.create_table(
        "pattern_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("pattern_id", sa.String(100), nullable=False, index=True),
        sa.Column("pattern_category", sa.String(50), nullable=False, index=True),
        sa.Column(
            "skill_stage",
            sa.String(20),
            nullable=False,
            server_default="understood",
            comment="習熟段階: understood, drilling, acquired",
        ),
        sa.Column("practice_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "last_practiced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "first_used_in_freetalk",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="フリートークで初めて使用された日時",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # === sound_pattern_mastery テーブル (Phase 3: 音声パターン習熟度) ===
    op.create_table(
        "sound_pattern_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "pattern_type",
            sa.String(30),
            nullable=False,
            index=True,
            comment="パターン種別: linking, reduction, flapping, deletion, weak_form, phoneme_*",
        ),
        sa.Column(
            "pattern_text",
            sa.String(500),
            nullable=False,
            comment="対象テキスト（例: 'want to' -> 'wanna'）",
        ),
        sa.Column(
            "ipa_notation",
            sa.String(500),
            nullable=True,
            comment="IPA表記（例: /wɑːnə/）",
        ),
        sa.Column("accuracy", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("practice_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # === subscriptions テーブル (Phase 3: Stripe決済管理) ===
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True, unique=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True, unique=True),
        sa.Column(
            "plan",
            sa.String(50),
            nullable=False,
            server_default="free",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "current_period_start",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "current_period_end",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
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


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("sound_pattern_mastery")
    op.drop_table("pattern_mastery")
