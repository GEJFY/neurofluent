# =============================================================================
# FluentEdge AI - Azure モジュール変数
# =============================================================================

variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境 (dev, staging, prod)"
  type        = string
}

variable "location" {
  description = "Azure リージョン"
  type        = string
  default     = "japaneast"
}

variable "backend_image" {
  description = "バックエンドコンテナイメージ名"
  type        = string
}

variable "frontend_image" {
  description = "フロントエンドコンテナイメージ名"
  type        = string
}

variable "database_sku" {
  description = "PostgreSQL Flexible Server SKU 名"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "redis_sku" {
  description = "Redis Cache SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

variable "tags" {
  description = "リソースに付与するタグ"
  type        = map(string)
  default     = {}
}
