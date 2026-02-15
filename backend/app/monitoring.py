"""Azure Application Insights モニタリング - OpenTelemetry ベース"""

import structlog

from app.config import settings

logger = structlog.get_logger()


def init_monitoring() -> None:
    """Application Insights を初期化（Connection String 未設定時はスキップ）"""
    if not settings.appinsights_connection_string:
        logger.info(
            "monitoring_skipped", reason="APPINSIGHTS_CONNECTION_STRING not configured"
        )
        return

    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(
        connection_string=settings.appinsights_connection_string,
        enable_live_metrics=True,
        instrumentation_options={
            "azure_sdk": {"enabled": True},
            "flask": {"enabled": False},
            "django": {"enabled": False},
            "fastapi": {"enabled": True},
            "psycopg2": {"enabled": True},
            "requests": {"enabled": False},
            "urllib": {"enabled": False},
            "urllib3": {"enabled": False},
            "httpx": {"enabled": True},
        },
    )

    logger.info(
        "monitoring_initialized",
        provider="application_insights",
        environment=settings.environment,
    )
