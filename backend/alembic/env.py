"""Alembic環境設定 - 非同期対応マイグレーション

全モデルをインポートしてBaseのメタデータをAlembicに提供し、
autogenerateによるマイグレーション自動生成を可能にする。
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.config import settings
from app.database import Base

# 全モデルをインポート（Alembicがテーブル定義を検出するために必要）
from app.models import (  # noqa: F401
    ApiUsageLog,
    ConversationMessage,
    ConversationSession,
    DailyStat,
    ReviewItem,
    User,
)

# Alembic Config オブジェクト
config = context.config

# ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembicが使用するメタデータ
target_metadata = Base.metadata


def get_url() -> str:
    """環境変数から非同期DB URLを取得（async_engine_from_configで使用）"""
    return settings.database_url


def run_migrations_offline() -> None:
    """オフラインモードでマイグレーションを実行（SQL出力のみ）"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """マイグレーション実行のコアロジック"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """非同期エンジンを使用してマイグレーションを実行"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """オンラインモードでマイグレーションを実行（DB接続あり）"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
