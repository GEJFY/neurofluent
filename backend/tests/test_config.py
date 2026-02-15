"""アプリケーション設定のテスト"""

from app.config import Settings


class TestSettings:
    """Settings設定クラスのテスト（_env_file=Noneで.envを読まずにテスト）"""

    def _make(self, **kwargs):
        """テスト用のSettingsインスタンスを作成（.envを読まない）"""
        return Settings(_env_file=None, **kwargs)

    def test_default_values(self):
        """デフォルト値が正しく設定される"""
        s = self._make()
        assert s.environment == "dev"
        assert s.log_level == "INFO"
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expiry_hours == 24
        assert s.llm_provider == "azure_foundry"

    def test_gpt5_model_defaults(self):
        """GPT-5モデル設定のデフォルト値"""
        s = self._make()
        assert s.gpt5_smart_model == "gpt-5-mini"
        assert s.gpt5_fast_model == "gpt-5-nano"
        assert s.gpt5_powerful_model == "gpt-5"

    def test_azure_openai_api_version_default(self):
        """Azure OpenAI APIバージョンのデフォルト値"""
        s = self._make()
        assert s.azure_openai_api_version == "2024-10-21"

    def test_rate_limit_defaults(self):
        """レートリミットのデフォルト値"""
        s = self._make()
        assert s.rate_limit_authenticated == 100
        assert s.rate_limit_unauthenticated == 30

    def test_cors_origins_list_single(self):
        """CORS origins のリスト変換（単一）"""
        s = self._make(backend_cors_origins="http://localhost:3000")
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_cors_origins_list_multiple(self):
        """CORS origins のリスト変換（複数）"""
        s = self._make(
            backend_cors_origins="http://localhost:3000,https://app.example.com"
        )
        assert s.cors_origins_list == [
            "http://localhost:3000",
            "https://app.example.com",
        ]

    def test_cors_origins_list_with_spaces(self):
        """CORS origins のリスト変換（スペース含む）"""
        s = self._make(backend_cors_origins="http://a.com , http://b.com")
        assert s.cors_origins_list == ["http://a.com", "http://b.com"]

    def test_cors_origins_list_empty(self):
        """CORS origins が空の場合"""
        s = self._make(backend_cors_origins="")
        assert s.cors_origins_list == []

    def test_custom_settings(self):
        """カスタム設定値が反映される"""
        s = self._make(
            environment="production",
            jwt_secret_key="custom-secret",
            llm_provider="anthropic",
            gpt5_smart_model="gpt-5-custom",
        )
        assert s.environment == "production"
        assert s.jwt_secret_key == "custom-secret"
        assert s.llm_provider == "anthropic"
        assert s.gpt5_smart_model == "gpt-5-custom"

    def test_llm_resilience_defaults(self):
        """LLMレジリエンス設定のデフォルト値"""
        s = self._make()
        assert s.llm_circuit_breaker_threshold == 5
        assert s.llm_circuit_breaker_timeout == 60.0
        assert s.llm_retry_max == 3
        assert s.llm_rate_limit_rpm == 60

    def test_app_version_default(self):
        """アプリバージョンのデフォルト値"""
        s = self._make()
        assert s.app_version == "1.0.0"

    def test_appinsights_default_empty(self):
        """AppInsights接続文字列のデフォルト値が空"""
        s = self._make()
        assert s.appinsights_connection_string == ""

    def test_extra_ignore(self):
        """未知の設定フィールドが無視される"""
        s = self._make(unknown_field="value")
        assert not hasattr(s, "unknown_field")
