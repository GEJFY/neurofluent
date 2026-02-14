from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    environment: str = "dev"
    log_level: str = "INFO"
    backend_cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://fluentedge:fluentedge@localhost:5432/fluentedge"
    database_url_sync: str = "postgresql://fluentedge:fluentedge@localhost:5432/fluentedge"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_realtime_deployment: str = "gpt-realtime"
    azure_openai_tts_deployment: str = "gpt-4o-mini-tts"

    # Claude (Azure AI Foundry)
    azure_ai_foundry_endpoint: str = ""
    azure_ai_foundry_api_key: str = ""
    claude_sonnet_model: str = "claude-sonnet-4-5-20250929"
    claude_haiku_model: str = "claude-haiku-4-5-20251001"

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

    model_config = {"env_file": "../.env", "extra": "ignore"}


settings = Settings()
