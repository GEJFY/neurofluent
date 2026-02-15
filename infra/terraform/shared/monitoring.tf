# =============================================================================
# FluentEdge AI - 監視・アラート共通設定
# 各クラウドの監視サービスを使用したアラート定義
# =============================================================================

# 監視設計方針:
#
# Azure: Azure Monitor + Log Analytics
# AWS:   CloudWatch Metrics + Alarms
# GCP:   Cloud Monitoring + Alerting Policies

variable "monitoring_config" {
  description = "監視・アラート設定"
  type = object({
    enable_alerts       = bool
    alert_email         = string
    cpu_threshold       = number
    memory_threshold    = number
    error_rate_threshold = number
    response_time_ms    = number
  })
  default = {
    enable_alerts       = true
    alert_email         = "admin@example.com"
    cpu_threshold       = 80     # CPU使用率 80% でアラート
    memory_threshold    = 85     # メモリ使用率 85% でアラート
    error_rate_threshold = 5     # エラーレート 5% でアラート
    response_time_ms    = 3000   # レスポンスタイム 3秒 でアラート
  }
}

# アラートルール:
#
# Critical (即時通知):
#   - サービスダウン (ヘルスチェック失敗 3回連続)
#   - DB接続エラー
#   - LLMプロバイダー全滅 (サーキットブレーカー全開)
#
# Warning (メール通知):
#   - CPU/メモリ使用率の閾値超過
#   - エラーレート閾値超過
#   - レスポンスタイム劣化
#   - LLMフォールバック発生
#
# Info (ログのみ):
#   - デプロイ完了
#   - スケーリングイベント
#   - バックアップ完了
