"""Key Vault統合のテスト"""

import os
from unittest.mock import MagicMock, patch

from app.keyvault import load_secrets_from_keyvault


class TestKeyVault:
    """Key Vault シークレット読み込みのテスト"""

    def test_skip_when_no_vault_url(self):
        """AZURE_KEY_VAULT_URL未設定時はスキップされる"""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AZURE_KEY_VAULT_URL", None)
            result = load_secrets_from_keyvault()
            assert result == 0

    def test_loads_secrets_successfully(self):
        """シークレットを正常に読み込める"""
        mock_secret = MagicMock()
        mock_secret.value = "test-secret-value"

        mock_client = MagicMock()
        mock_client.get_secret.return_value = mock_secret

        mock_credential = MagicMock()

        with patch.dict(
            os.environ,
            {"AZURE_KEY_VAULT_URL": "https://test.vault.azure.net/"},
            clear=False,
        ):
            # 対象の環境変数をクリア
            for env_var in [
                "AZURE_AI_FOUNDRY_API_KEY",
                "AZURE_SPEECH_KEY",
                "JWT_SECRET_KEY",
                "STRIPE_SECRET_KEY",
                "STRIPE_WEBHOOK_SECRET",
                "DATABASE_URL",
                "REDIS_URL",
            ]:
                os.environ.pop(env_var, None)

            with patch(
                "azure.identity.DefaultAzureCredential",
                return_value=mock_credential,
            ):
                with patch(
                    "azure.keyvault.secrets.SecretClient",
                    return_value=mock_client,
                ):
                    result = load_secrets_from_keyvault()
                    assert result > 0

    def test_skips_existing_env_vars(self):
        """既存の環境変数がある場合はスキップされる"""
        mock_client = MagicMock()

        with patch.dict(
            os.environ,
            {
                "AZURE_KEY_VAULT_URL": "https://test.vault.azure.net/",
                "AZURE_AI_FOUNDRY_API_KEY": "existing-value",
                "AZURE_SPEECH_KEY": "existing-value",
                "JWT_SECRET_KEY": "existing-value",
                "STRIPE_SECRET_KEY": "existing-value",
                "STRIPE_WEBHOOK_SECRET": "existing-value",
                "DATABASE_URL": "existing-value",
                "REDIS_URL": "existing-value",
            },
        ):
            with patch("azure.identity.DefaultAzureCredential"):
                with patch(
                    "azure.keyvault.secrets.SecretClient",
                    return_value=mock_client,
                ):
                    result = load_secrets_from_keyvault()
                    assert result == 0
                    mock_client.get_secret.assert_not_called()

    def test_handles_connection_failure(self):
        """接続エラー時は0を返す"""
        with patch.dict(
            os.environ,
            {"AZURE_KEY_VAULT_URL": "https://test.vault.azure.net/"},
        ):
            with patch(
                "azure.identity.DefaultAzureCredential",
                side_effect=Exception("Connection failed"),
            ):
                result = load_secrets_from_keyvault()
                assert result == 0
