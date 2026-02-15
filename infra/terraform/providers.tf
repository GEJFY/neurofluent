# =============================================================================
# FluentEdge AI - プロバイダー設定
# 各クラウドプロバイダーの初期化設定
# =============================================================================

# Azure Resource Manager プロバイダー
provider "azurerm" {
  features {
    # Key Vault のソフトデリート設定
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }

    # リソースグループ内にリソースが残っていても削除を許可 (dev 環境用)
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  # サブスクリプションIDは環境変数 ARM_SUBSCRIPTION_ID で設定
}

# AWS プロバイダー
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }

  # 認証情報は環境変数 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY で設定
}

# Google Cloud プロバイダー
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region

  # 認証情報は環境変数 GOOGLE_APPLICATION_CREDENTIALS で設定
}
