# =============================================================================
# FluentEdge AI - Azure モジュール出力
# 統一インターフェース: backend_url, frontend_url, database_host, redis_host
# =============================================================================

output "backend_url" {
  description = "バックエンド Container App の URL"
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "frontend_url" {
  description = "フロントエンド Container App の URL"
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "database_host" {
  description = "PostgreSQL Flexible Server の FQDN"
  value       = azurerm_postgresql_flexible_server.main.fqdn
  sensitive   = true
}

output "redis_host" {
  description = "Redis Cache のホスト名"
  value       = azurerm_redis_cache.main.hostname
  sensitive   = true
}

output "resource_group_name" {
  description = "リソースグループ名"
  value       = azurerm_resource_group.main.name
}

output "acr_login_server" {
  description = "ACR ログインサーバー"
  value       = azurerm_container_registry.main.login_server
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = azurerm_key_vault.main.vault_uri
}
