# =============================================================================
# FluentEdge AI - DNS設定テンプレート
# 各クラウドの DNS サービスを使用したドメイン管理
# =============================================================================

# DNS設計方針:
#
# Azure: Azure DNS Zone
# AWS:   Route 53 Hosted Zone
# GCP:   Cloud DNS Managed Zone
#
# レコード構成:
#   fluentedge.example.com          -> フロントエンド (A/CNAME)
#   api.fluentedge.example.com      -> バックエンド (A/CNAME)
#   *.fluentedge.example.com        -> ワイルドカード (開発環境等)

variable "dns_config" {
  description = "DNS設定"
  type = object({
    domain_name     = string
    enable_ssl      = bool
    subdomain_api   = string
    subdomain_app   = string
  })
  default = {
    domain_name     = "fluentedge.example.com"
    enable_ssl      = true
    subdomain_api   = "api"
    subdomain_app   = "app"
  }
}

# SSL/TLS 証明書:
# Azure: App Service Managed Certificate / Key Vault
# AWS:   ACM (AWS Certificate Manager)
# GCP:   Google-managed SSL Certificate
