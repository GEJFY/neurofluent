# =============================================================================
# FluentEdge AI - GCP モジュール変数
# =============================================================================

variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "project_id" {
  description = "GCP プロジェクト ID"
  type        = string
}

variable "environment" {
  description = "デプロイ環境 (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "GCP リージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "backend_image" {
  description = "バックエンドコンテナイメージ名"
  type        = string
}

variable "frontend_image" {
  description = "フロントエンドコンテナイメージ名"
  type        = string
}

variable "db_tier" {
  description = "Cloud SQL インスタンスティア"
  type        = string
  default     = "db-f1-micro"
}

variable "redis_tier" {
  description = "Memorystore Redis ティア (BASIC, STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "labels" {
  description = "リソースに付与するラベル"
  type        = map(string)
  default     = {}
}
