from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    environment: str = "dev"
    log_level: str = "INFO"
    backend_cors_origins: str = "http://localhost:3500"

    # Rate Limiting (API global)
    rate_limit_authenticated: int = 100
    rate_limit_unauthenticated: int = 30

    # Monitoring (Azure Application Insights)
    appinsights_connection_string: str = ""
    app_version: str = "1.0.0"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins をリストで返す"""
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]

    # Database
    database_url: str = (
        "postgresql+asyncpg://fluentedge:fluentedge@localhost:5450/fluentedge"
    )
    database_url_sync: str = (
        "postgresql://fluentedge:fluentedge@localhost:5450/fluentedge"
    )

    # Redis
    redis_url: str = "redis://localhost:6390/0"

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_realtime_deployment: str = "gpt-realtime"
    azure_openai_tts_deployment: str = "gpt-4o-mini-tts"

    # Azure AI Foundry (GPT-5 via Azure OpenAI)
    azure_ai_foundry_endpoint: str = ""
    azure_ai_foundry_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    gpt5_smart_model: str = "gpt-5-mini"
    gpt5_fast_model: str = "gpt-5-nano"
    gpt5_powerful_model: str = "gpt-5"

    # Azure Speech
    azure_speech_key: str = ""
    azure_speech_region: str = "eastus2"

    # Auth (JWT)
    jwt_secret_key: str = "change-this-to-a-random-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Stripe (Phase 3: サブスクリプション決済)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_standard: str = ""
    stripe_price_premium: str = ""

    # === LLM Provider (マルチクラウド) ===
    llm_provider: str = "azure_foundry"  # azure_foundry, anthropic, bedrock, vertex, local, openai_compat
    llm_fallback_providers: str = ""  # カンマ区切り例: "anthropic,bedrock"

    # Anthropic Direct
    anthropic_api_key: str = ""

    # AWS Bedrock
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bedrock_model_sonnet: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    aws_bedrock_model_haiku: str = "anthropic.claude-haiku-4-5-20251001-v1:0"
    aws_bedrock_model_opus: str = "anthropic.claude-opus-4-6-v1:0"

    # GCP Vertex AI
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    gcp_vertex_model_sonnet: str = "claude-sonnet-4-5-20250929"
    gcp_vertex_model_haiku: str = "claude-haiku-4-5-20251001"
    gcp_vertex_model_opus: str = "claude-opus-4-6"

    # Local / OpenAI-compatible
    local_llm_base_url: str = "http://localhost:11434/v1"
    local_llm_api_key: str = "ollama"  # Ollamaはダミーキー可
    local_model_smart: str = "llama3.1:8b"
    local_model_fast: str = "llama3.1:8b"

    # LLM Resilience（レジリエンス設定）
    llm_circuit_breaker_threshold: int = 5
    llm_circuit_breaker_timeout: float = 60.0
    llm_retry_max: int = 3
    llm_rate_limit_rpm: int = 60

    model_config = {"env_file": "../.env", "extra": "ignore"}


settings = Settings()
