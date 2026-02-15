# =============================================================================
# FluentEdge AI - 共通ネットワーク設定
# 各クラウドモジュールの VPC/VNet 設計ガイドライン
# =============================================================================

# ネットワーク設計方針:
#
# Azure:
#   - VNet (10.0.0.0/16) + サブネット分離
#   - app-subnet (10.0.1.0/24) - Container Apps
#   - db-subnet  (10.0.2.0/24) - PostgreSQL Flexible Server
#   - redis-subnet (10.0.3.0/24) - Redis Cache
#
# AWS:
#   - VPC (10.1.0.0/16) + パブリック/プライベートサブネット
#   - public-a  (10.1.1.0/24) - ALB
#   - public-c  (10.1.2.0/24) - ALB
#   - private-a (10.1.11.0/24) - ECS Fargate
#   - private-c (10.1.12.0/24) - ECS Fargate
#   - db-a      (10.1.21.0/24) - RDS
#   - db-c      (10.1.22.0/24) - RDS
#
# GCP:
#   - VPC + カスタムサブネット
#   - app-subnet (10.2.1.0/24) - Cloud Run (VPC connector)
#   - db-subnet  (10.2.2.0/24) - Cloud SQL
#   - redis-range (10.2.3.0/24) - Memorystore

# セキュリティグループ/ファイアウォール共通方針:
# - インバウンド: 80/443 (HTTP/HTTPS) のみ公開
# - バックエンド: 8000 (内部のみ)
# - PostgreSQL: 5432 (DB サブネットからのみ)
# - Redis: 6379 (App サブネットからのみ)

variable "network_config" {
  description = "ネットワーク設定"
  type = object({
    vpc_cidr    = string
    enable_nat  = bool
    enable_vpn  = bool
  })
  default = {
    vpc_cidr    = "10.0.0.0/16"
    enable_nat  = true
    enable_vpn  = false
  }
}
