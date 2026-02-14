# =============================================================================
# FluentEdge AI - 入力変数定義
# =============================================================================

# -----------------------------------------------------------------------------
# 共通変数
# -----------------------------------------------------------------------------

variable "cloud_provider" {
  description = "デプロイ先クラウドプロバイダー (azure, aws, gcp)"
  type        = string
  default     = "azure"

  validation {
    condition     = contains(["azure", "aws", "gcp"], var.cloud_provider)
    error_message = "cloud_provider は azure, aws, gcp のいずれかを指定してください。"
  }
}

variable "project_name" {
  description = "プロジェクト名 (リソース命名に使用)"
  type        = string
  default     = "fluentedge"
}

variable "environment" {
  description = "デプロイ環境 (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment は dev, staging, prod のいずれかを指定してください。"
  }
}

# -----------------------------------------------------------------------------
# コンテナイメージ
# -----------------------------------------------------------------------------

variable "backend_image" {
  description = "バックエンドコンテナイメージ名"
  type        = string
  default     = "fluentedge-backend:latest"
}

variable "frontend_image" {
  description = "フロントエンドコンテナイメージ名"
  type        = string
  default     = "fluentedge-frontend:latest"
}

# -----------------------------------------------------------------------------
# Azure 固有変数
# -----------------------------------------------------------------------------

variable "azure_location" {
  description = "Azure リージョン"
  type        = string
  default     = "japaneast"
}

variable "database_sku" {
  description = "Azure PostgreSQL Flexible Server SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "redis_sku" {
  description = "Azure Redis Cache SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Basic"
}

# -----------------------------------------------------------------------------
# AWS 固有変数
# -----------------------------------------------------------------------------

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "aws_db_instance_class" {
  description = "AWS RDS インスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "aws_redis_node_type" {
  description = "AWS ElastiCache ノードタイプ"
  type        = string
  default     = "cache.t3.micro"
}

# -----------------------------------------------------------------------------
# GCP 固有変数
# -----------------------------------------------------------------------------

variable "gcp_project_id" {
  description = "GCP プロジェクト ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "GCP リージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "gcp_db_tier" {
  description = "GCP Cloud SQL インスタンスティア"
  type        = string
  default     = "db-f1-micro"
}

variable "gcp_redis_tier" {
  description = "GCP Memorystore Redis ティア (BASIC, STANDARD_HA)"
  type        = string
  default     = "BASIC"
}
