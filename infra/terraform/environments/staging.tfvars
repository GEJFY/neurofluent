# =============================================================================
# FluentEdge AI - ステージング環境設定
# =============================================================================

environment    = "staging"
project_name   = "fluentedge"
cloud_provider = "azure"

# Azure
azure_location = "japaneast"
database_sku   = "GP_Standard_D2s_v3"
redis_sku      = "Standard"

# コンテナイメージ (ステージング - CIでタグ付け)
backend_image  = "fluentedge-backend:staging"
frontend_image = "fluentedge-frontend:staging"
