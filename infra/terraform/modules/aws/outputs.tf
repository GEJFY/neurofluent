# =============================================================================
# FluentEdge AI - AWS モジュール出力
# 統一インターフェース: backend_url, frontend_url, database_host, redis_host
# =============================================================================

output "backend_url" {
  description = "バックエンド ALB の URL (ポート 8000)"
  value       = "http://${aws_lb.main.dns_name}:8000"
}

output "frontend_url" {
  description = "フロントエンド ALB の URL"
  value       = "http://${aws_lb.main.dns_name}"
}

output "database_host" {
  description = "RDS PostgreSQL のエンドポイント"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "redis_host" {
  description = "ElastiCache Redis のプライマリエンドポイント"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "ecs_cluster_name" {
  description = "ECS クラスター名"
  value       = aws_ecs_cluster.main.name
}

output "ecr_backend_url" {
  description = "バックエンド ECR リポジトリ URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "フロントエンド ECR リポジトリ URL"
  value       = aws_ecr_repository.frontend.repository_url
}
