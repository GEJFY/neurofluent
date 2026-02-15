# =============================================================================
# FluentEdge AI - Terraform Root Module
# マルチクラウド対応 (Azure / AWS / GCP)
# =============================================================================

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  # リモートステート (Azure Blob Storage)
  # どのクラウドにデプロイしても state 管理は Azure で統一
  backend "azurerm" {
    resource_group_name  = "fluentedge-tfstate"
    storage_account_name = "fluentedgetfstate"
    container_name       = "tfstate"
    key                  = "fluentedge.tfstate"
  }
}

# =============================================================================
# プロバイダー選択に基づくモジュール呼び出し
# count で切り替えることで各クラウドモジュールは独立して使用可能
# =============================================================================

# Azure モジュール
module "azure" {
  count  = var.cloud_provider == "azure" ? 1 : 0
  source = "./modules/azure"

  project_name = var.project_name
  environment  = var.environment
  location     = var.azure_location

  backend_image  = var.backend_image
  frontend_image = var.frontend_image

  database_sku = var.database_sku
  redis_sku    = var.redis_sku

  tags = local.common_tags
}

# AWS モジュール
module "aws" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  source = "./modules/aws"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  backend_image  = var.backend_image
  frontend_image = var.frontend_image

  db_instance_class = var.aws_db_instance_class
  redis_node_type   = var.aws_redis_node_type

  tags = local.common_tags
}

# GCP モジュール
module "gcp" {
  count  = var.cloud_provider == "gcp" ? 1 : 0
  source = "./modules/gcp"

  project_name = var.project_name
  project_id   = var.gcp_project_id
  environment  = var.environment
  region       = var.gcp_region

  backend_image  = var.backend_image
  frontend_image = var.frontend_image

  db_tier    = var.gcp_db_tier
  redis_tier = var.gcp_redis_tier

  labels = local.common_tags
}

# =============================================================================
# 共通タグ / ラベル
# =============================================================================
locals {
  common_tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}
