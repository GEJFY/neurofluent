# =============================================================================
# FluentEdge AI - 開発環境設定
# =============================================================================

environment    = "dev"
project_name   = "fluentedge"
cloud_provider = "azure"

# Azure
azure_location = "japaneast"
database_sku   = "B_Standard_B1ms"
redis_sku      = "Basic"

# コンテナイメージ (開発)
backend_image  = "fluentedge-backend:latest"
frontend_image = "fluentedge-frontend:latest"
