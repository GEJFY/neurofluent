# =============================================================================
# FluentEdge AI - GCP モジュール
# Cloud Run + Cloud SQL + Memorystore Redis + Secret Manager
# =============================================================================

# =============================================================================
# 必要な API の有効化
# =============================================================================
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",              # Cloud Run
    "sqladmin.googleapis.com",         # Cloud SQL Admin
    "redis.googleapis.com",            # Memorystore Redis
    "secretmanager.googleapis.com",    # Secret Manager
    "artifactregistry.googleapis.com", # Artifact Registry
    "vpcaccess.googleapis.com",        # VPC Access (Cloud Run -> DB)
    "compute.googleapis.com",          # Compute Engine (ネットワーク)
  ])

  project = var.project_id
  service = each.key

  disable_dependent_services = false
  disable_on_destroy         = false
}

# =============================================================================
# Artifact Registry (コンテナレジストリ)
# =============================================================================
resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "${var.project_name}-${var.environment}"
  description   = "FluentEdge ${var.environment} コンテナイメージ"
  format        = "DOCKER"
  labels        = var.labels

  depends_on = [google_project_service.services["artifactregistry.googleapis.com"]]
}

# =============================================================================
# VPC ネットワーク (Cloud SQL / Redis のプライベート接続用)
# =============================================================================
resource "google_compute_network" "main" {
  name                    = "${var.project_name}-${var.environment}-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.services["compute.googleapis.com"]]
}

resource "google_compute_subnetwork" "main" {
  name          = "${var.project_name}-${var.environment}-subnet"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.main.id
}

# プライベートサービス接続 (Cloud SQL 用)
resource "google_compute_global_address" "private_ip" {
  name          = "${var.project_name}-${var.environment}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip.name]
}

# VPC Access Connector (Cloud Run -> VPC)
resource "google_vpc_access_connector" "main" {
  name          = "${var.project_name}-${var.environment}-vpc-conn"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.main.name

  depends_on = [google_project_service.services["vpcaccess.googleapis.com"]]
}

# =============================================================================
# Cloud Run v2 - バックエンド
# =============================================================================
resource "google_cloud_run_v2_service" "backend" {
  name     = "${var.project_name}-${var.environment}-backend"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/${var.backend_image}"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = var.environment == "prod" ? "2" : "1"
          memory = var.environment == "prod" ? "1Gi" : "512Mi"
        }
      }

      # 環境変数
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "REDIS_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_url.secret_id
            version = "latest"
          }
        }
      }
    }

    # VPC 接続 (Cloud SQL / Redis へのアクセス)
    vpc_access {
      connector = google_vpc_access_connector.main.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    scaling {
      min_instance_count = var.environment == "prod" ? 2 : 0
      max_instance_count = var.environment == "prod" ? 20 : 3
    }
  }

  labels = var.labels

  depends_on = [
    google_project_service.services["run.googleapis.com"],
    google_secret_manager_secret_version.database_url,
    google_secret_manager_secret_version.redis_url,
  ]
}

# Cloud Run バックエンドの公開アクセス許可
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  name     = google_cloud_run_v2_service.backend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud Run v2 - フロントエンド
# =============================================================================
resource "google_cloud_run_v2_service" "frontend" {
  name     = "${var.project_name}-${var.environment}-frontend"
  location = var.region

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/${var.frontend_image}"

      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }

    scaling {
      min_instance_count = var.environment == "prod" ? 2 : 0
      max_instance_count = var.environment == "prod" ? 20 : 3
    }
  }

  labels = var.labels

  depends_on = [google_project_service.services["run.googleapis.com"]]
}

# Cloud Run フロントエンドの公開アクセス許可
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  name     = google_cloud_run_v2_service.frontend.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Cloud SQL - PostgreSQL 16
# =============================================================================
resource "google_sql_database_instance" "main" {
  name             = "${var.project_name}-${var.environment}-pg"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_size         = var.environment == "prod" ? 50 : 10
    disk_autoresize   = true
    disk_type         = "PD_SSD"

    # pgvector 拡張対応フラグ
    database_flags {
      name  = "cloudsql.enable_pgvector"
      value = "on"
    }

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "prod"
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 35 : 7
      }
    }

    maintenance_window {
      day          = 7 # 日曜日
      hour         = 3 # 03:00 UTC
      update_track = "stable"
    }
  }

  deletion_protection = var.environment == "prod"

  depends_on = [
    google_service_networking_connection.private_vpc,
    google_project_service.services["sqladmin.googleapis.com"],
  ]
}

# データベース作成
resource "google_sql_database" "main" {
  name     = "fluentedge"
  instance = google_sql_database_instance.main.name
}

# データベースユーザー
resource "random_password" "sql_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "google_sql_user" "main" {
  name     = "fluentedgeadmin"
  instance = google_sql_database_instance.main.name
  password = random_password.sql_password.result
}

# =============================================================================
# Memorystore Redis
# =============================================================================
resource "google_redis_instance" "main" {
  name               = "${var.project_name}-${var.environment}-redis"
  tier               = var.redis_tier
  memory_size_gb     = var.environment == "prod" ? 2 : 1
  region             = var.region
  redis_version      = "REDIS_7_2"
  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  display_name       = "FluentEdge ${var.environment} Redis"
  labels             = var.labels

  depends_on = [
    google_service_networking_connection.private_vpc,
    google_project_service.services["redis.googleapis.com"],
  ]
}

# =============================================================================
# Secret Manager (シークレット管理)
# =============================================================================
resource "google_secret_manager_secret" "database_url" {
  secret_id = "${var.project_name}-${var.environment}-database-url"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.services["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = "postgresql+asyncpg://fluentedgeadmin:${random_password.sql_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/fluentedge?sslmode=require"
}

resource "google_secret_manager_secret" "redis_url" {
  secret_id = "${var.project_name}-${var.environment}-redis-url"

  replication {
    auto {}
  }

  labels = var.labels

  depends_on = [google_project_service.services["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "redis_url" {
  secret      = google_secret_manager_secret.redis_url.id
  secret_data = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}/0"
}
