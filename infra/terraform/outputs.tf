# =============================================================================
# FluentEdge AI - 統一出力インターフェース
# どのクラウドにデプロイしても同じ出力キーで結果を取得可能
# =============================================================================

output "backend_url" {
  description = "バックエンド API の URL"
  value = coalesce(
    try(module.azure[0].backend_url, ""),
    try(module.aws[0].backend_url, ""),
    try(module.gcp[0].backend_url, ""),
    "not-deployed"
  )
}

output "frontend_url" {
  description = "フロントエンドアプリの URL"
  value = coalesce(
    try(module.azure[0].frontend_url, ""),
    try(module.aws[0].frontend_url, ""),
    try(module.gcp[0].frontend_url, ""),
    "not-deployed"
  )
}

output "database_host" {
  description = "PostgreSQL データベースのホスト名"
  value = coalesce(
    try(module.azure[0].database_host, ""),
    try(module.aws[0].database_host, ""),
    try(module.gcp[0].database_host, ""),
    "not-deployed"
  )
  sensitive = true
}

output "redis_host" {
  description = "Redis キャッシュのホスト名"
  value = coalesce(
    try(module.azure[0].redis_host, ""),
    try(module.aws[0].redis_host, ""),
    try(module.gcp[0].redis_host, ""),
    "not-deployed"
  )
  sensitive = true
}

output "cloud_provider" {
  description = "デプロイ先クラウドプロバイダー"
  value       = var.cloud_provider
}

output "environment" {
  description = "デプロイ環境"
  value       = var.environment
}
