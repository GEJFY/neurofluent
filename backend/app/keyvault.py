"""Azure Key Vault シークレット統合

Key Vault からシークレットを取得してアプリケーション設定に反映する。
AZURE_KEY_VAULT_URL 環境変数が設定されている場合のみ有効。
DefaultAzureCredential により Managed Identity / CLI / 環境変数認証に対応。
"""

import logging
import os

logger = logging.getLogger(__name__)

# Key Vault シークレット名 → 環境変数名 のマッピング
SECRET_MAP = {
    "azure-ai-foundry-api-key": "AZURE_AI_FOUNDRY_API_KEY",
    "azure-speech-key": "AZURE_SPEECH_KEY",
    "jwt-secret-key": "JWT_SECRET_KEY",
    "stripe-secret-key": "STRIPE_SECRET_KEY",
    "stripe-webhook-secret": "STRIPE_WEBHOOK_SECRET",
    "database-url": "DATABASE_URL",
    "redis-url": "REDIS_URL",
}


def load_secrets_from_keyvault() -> int:
    """Key Vault からシークレットを読み込み環境変数に設定する

    Returns:
        読み込んだシークレット数。Key Vault未設定の場合は0。
    """
    vault_url = os.environ.get("AZURE_KEY_VAULT_URL", "")
    if not vault_url:
        logger.debug("AZURE_KEY_VAULT_URL not set, skipping Key Vault integration")
        return 0

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
    except ImportError:
        logger.warning(
            "azure-identity/azure-keyvault-secrets not installed, "
            "skipping Key Vault integration"
        )
        return 0

    try:
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

        loaded = 0
        for secret_name, env_var in SECRET_MAP.items():
            # 既に環境変数に値がある場合はスキップ（ローカル開発の.envを優先）
            if os.environ.get(env_var):
                continue
            try:
                secret = client.get_secret(secret_name)
                if secret.value:
                    os.environ[env_var] = secret.value
                    loaded += 1
                    logger.info("Loaded secret: %s -> %s", secret_name, env_var)
            except Exception as e:
                logger.warning(
                    "Failed to load secret %s: %s", secret_name, str(e)[:100]
                )

        logger.info("Key Vault: loaded %d secrets from %s", loaded, vault_url)
        return loaded

    except Exception as e:
        logger.warning("Key Vault connection failed: %s", str(e)[:200])
        return 0
