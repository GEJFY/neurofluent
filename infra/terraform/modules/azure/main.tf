# =============================================================================
# FluentEdge AI - Azure モジュール
# Azure Container Apps + PostgreSQL + Redis + Key Vault
# =============================================================================

# リソースグループ
resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
  tags     = var.tags
}

# =============================================================================
# コンテナレジストリ (ACR)
# =============================================================================
resource "azurerm_container_registry" "main" {
  name                = replace("${var.project_name}${var.environment}acr", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# =============================================================================
# Log Analytics Workspace
# =============================================================================
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project_name}-${var.environment}-logs"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# =============================================================================
# Container Apps 環境
# =============================================================================
resource "azurerm_container_app_environment" "main" {
  name                       = "${var.project_name}-${var.environment}-cae"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = var.tags
}

# =============================================================================
# バックエンド Container App
# =============================================================================
resource "azurerm_container_app" "backend" {
  name                         = "${var.project_name}-${var.environment}-backend"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"
  tags                         = var.tags

  template {
    container {
      name   = "backend"
      image  = "${azurerm_container_registry.main.login_server}/${var.backend_image}"
      cpu    = 0.5
      memory = "1Gi"

      # 環境変数 (Key Vault 参照はアプリ側で実装)
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "KEY_VAULT_URL"
        value = azurerm_key_vault.main.vault_uri
      }
    }

    min_replicas = var.environment == "prod" ? 2 : 0
    max_replicas = var.environment == "prod" ? 20 : 3
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }
}

# =============================================================================
# フロントエンド Container App
# =============================================================================
resource "azurerm_container_app" "frontend" {
  name                         = "${var.project_name}-${var.environment}-frontend"
  resource_group_name          = azurerm_resource_group.main.name
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode                = "Single"
  tags                         = var.tags

  template {
    container {
      name   = "frontend"
      image  = "${azurerm_container_registry.main.login_server}/${var.frontend_image}"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
      }
    }

    min_replicas = var.environment == "prod" ? 2 : 0
    max_replicas = var.environment == "prod" ? 20 : 3
  }

  ingress {
    external_enabled = true
    target_port      = 3000
    transport        = "http"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }
}

# =============================================================================
# PostgreSQL Flexible Server (v16 + pgvector)
# =============================================================================
resource "azurerm_postgresql_flexible_server" "main" {
  name                          = "${var.project_name}-${var.environment}-pg"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  version                       = "16"
  administrator_login           = "fluentedgeadmin"
  administrator_password        = random_password.pg_password.result
  sku_name                      = var.database_sku
  storage_mb                    = 32768
  backup_retention_days         = var.environment == "prod" ? 35 : 7
  geo_redundant_backup_enabled  = var.environment == "prod" ? true : false
  public_network_access_enabled = true # 本番ではプライベートエンドポイント推奨
  tags                          = var.tags

  high_availability {
    mode = var.environment == "prod" ? "ZoneRedundant" : "Disabled"
  }
}

# pgvector 拡張機能の有効化
resource "azurerm_postgresql_flexible_server_configuration" "pgvector" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "vector"
}

# データベース作成
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "fluentedge"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# PostgreSQL パスワード生成
resource "random_password" "pg_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# =============================================================================
# Redis Cache
# =============================================================================
resource "azurerm_redis_cache" "main" {
  name                          = "${var.project_name}-${var.environment}-redis"
  resource_group_name           = azurerm_resource_group.main.name
  location                      = azurerm_resource_group.main.location
  capacity                      = var.redis_sku == "Premium" ? 1 : 0
  family                        = var.redis_sku == "Premium" ? "P" : "C"
  sku_name                      = var.redis_sku
  non_ssl_port_enabled          = false
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true # 本番ではプライベートエンドポイント推奨
  redis_version                 = "6"
  tags                          = var.tags
}

# =============================================================================
# Key Vault (シークレット管理)
# =============================================================================

# 現在のクライアント情報取得
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                       = "${var.project_name}-${var.environment}-kv"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  soft_delete_retention_days = 7
  purge_protection_enabled   = var.environment == "prod" ? true : false
  tags                       = var.tags
}

# データベース接続文字列を Key Vault に格納
resource "azurerm_key_vault_secret" "database_url" {
  name         = "database-url"
  value        = "postgresql+asyncpg://fluentedgeadmin:${random_password.pg_password.result}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/fluentedge?sslmode=require"
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault.main]
}

# Redis 接続文字列を Key Vault に格納
resource "azurerm_key_vault_secret" "redis_url" {
  name         = "redis-url"
  value        = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:${azurerm_redis_cache.main.ssl_port}/0"
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault.main]
}
