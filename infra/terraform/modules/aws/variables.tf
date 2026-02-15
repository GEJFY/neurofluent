# =============================================================================
# FluentEdge AI - AWS モジュール変数
# =============================================================================

variable "project_name" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "デプロイ環境 (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "backend_image" {
  description = "バックエンドコンテナイメージ名"
  type        = string
}

variable "frontend_image" {
  description = "フロントエンドコンテナイメージ名"
  type        = string
}

variable "db_instance_class" {
  description = "RDS PostgreSQL インスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache Redis ノードタイプ"
  type        = string
  default     = "cache.t3.micro"
}

variable "tags" {
  description = "リソースに付与するタグ"
  type        = map(string)
  default     = {}
}
