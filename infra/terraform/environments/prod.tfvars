# =============================================================================
# FluentEdge AI - 本番環境設定
# =============================================================================

environment    = "prod"
project_name   = "fluentedge"
cloud_provider = "azure"

# Azure
azure_location = "japaneast"
database_sku   = "GP_Standard_D4s_v3"
redis_sku      = "Premium"

# コンテナイメージ (本番 - リリースタグ)
backend_image  = "fluentedge-backend:latest"
frontend_image = "fluentedge-frontend:latest"
