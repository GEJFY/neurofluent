# =============================================================================
# FluentEdge AI - GCP モジュール出力
# 統一インターフェース: backend_url, frontend_url, database_host, redis_host
# =============================================================================

output "backend_url" {
  description = "バックエンド Cloud Run の URL"
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  description = "フロントエンド Cloud Run の URL"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "database_host" {
  description = "Cloud SQL PostgreSQL のプライベート IP"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "redis_host" {
  description = "Memorystore Redis のホスト"
  value       = google_redis_instance.main.host
  sensitive   = true
}

output "artifact_registry_url" {
  description = "Artifact Registry の URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}"
}

output "vpc_id" {
  description = "VPC ネットワーク ID"
  value       = google_compute_network.main.id
}
