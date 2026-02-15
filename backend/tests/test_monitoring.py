"""Application Insights モニタリングのテスト"""

from unittest.mock import MagicMock, patch


class TestInitMonitoring:
    """init_monitoring() のテスト"""

    def test_skips_when_not_configured(self):
        """Connection Stringが未設定時はスキップする"""
        with patch("app.monitoring.settings") as mock_settings:
            mock_settings.appinsights_connection_string = ""

            from app.monitoring import init_monitoring

            with patch("app.monitoring.logger") as mock_logger:
                init_monitoring()
                mock_logger.info.assert_called_once_with(
                    "monitoring_skipped",
                    reason="APPINSIGHTS_CONNECTION_STRING not configured",
                )

    def test_initializes_when_configured(self):
        """Connection String設定時にAzure Monitorが初期化される"""
        mock_configure = MagicMock()
        mock_azure_module = MagicMock()
        mock_azure_module.configure_azure_monitor = mock_configure

        with patch("app.monitoring.settings") as mock_settings:
            mock_settings.appinsights_connection_string = "InstrumentationKey=test-key"
            mock_settings.environment = "dev"

            # init_monitoring() 内の from azure.monitor.opentelemetry import ... をモック
            with patch.dict(
                "sys.modules",
                {"azure.monitor.opentelemetry": mock_azure_module},
            ):
                from app.monitoring import init_monitoring

                init_monitoring()
                mock_configure.assert_called_once()


class TestMonitoringConfig:
    """モニタリング設定のテスト"""

    def test_appinsights_connection_string_field(self):
        """config.pyにappinsights_connection_stringフィールドが存在する"""
        from app.config import Settings

        # .env読み込みを無効化してデフォルト値をテスト
        s = Settings(appinsights_connection_string="test-conn-string", _env_file=None)
        assert s.appinsights_connection_string == "test-conn-string"

    def test_appinsights_default_empty(self):
        """デフォルト値が空文字列（.envを読まない場合）"""
        from app.config import Settings

        s = Settings(_env_file=None)
        assert s.appinsights_connection_string == ""
