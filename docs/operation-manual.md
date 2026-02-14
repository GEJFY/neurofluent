# FluentEdge AI 運用マニュアル

FluentEdge AI の本番・ステージング環境における運用手順をまとめたドキュメントです。
アプリケーション構成、起動・停止手順、ログ監視、ヘルスチェック、バックアップ、
スケーリング、障害対応、定期メンテナンスの各トピックを網羅しています。

---

## 目次

1. [アプリケーション構成図](#アプリケーション構成図)
2. [起動・停止手順](#起動停止手順)
3. [ログ監視](#ログ監視)
4. [ヘルスチェック](#ヘルスチェック)
5. [アラート設定](#アラート設定)
6. [バックアップ・リストア](#バックアップリストア)
7. [スケーリング](#スケーリング)
8. [障害対応](#障害対応)
9. [定期メンテナンス](#定期メンテナンス)

---

## アプリケーション構成図

```text
+------------------------------------------------------------------+
|                        ロードバランサー                             |
|                     (HTTPS 終端 / SSL)                            |
+--------+------------------------+--------------------------------+
         |                        |
         v                        v
+------------------+    +------------------+
|   Frontend       |    |   Backend        |
|   Next.js 15     |    |   FastAPI 0.115  |
|   React 19       |    |   Python 3.11    |
|   Port: 3000     |    |   Port: 8000     |
+------------------+    +--------+---------+
                                 |
                    +------------+-------------+
                    |            |             |
                    v            v             v
           +------------+  +----------+  +-----------+
           | PostgreSQL  |  |  Redis   |  |  LLM API  |
           |   16        |  |  7       |  | (マルチ   |
           | + pgvector  |  | (Cache)  |  |  クラウド) |
           +------------+  +----------+  +-----------+
                                          |
                          +---------------+----------------+
                          |               |                |
                          v               v                v
                  +-------------+ +-------------+ +-------------+
                  | Azure AI    | | Anthropic   | | AWS Bedrock |
                  | Foundry     | | Direct      | | / GCP       |
                  | (Primary)   | | (Fallback)  | | Vertex AI   |
                  +-------------+ +-------------+ +-------------+
```

### コンポーネント一覧

| コンポーネント | 技術 | ポート | 説明 |
| --- | --- | --- | --- |
| Frontend | Next.js 15 / React 19 | 3000 | SPA / SSR フロントエンド |
| Backend | FastAPI 0.115 / Python 3.11 | 8000 | REST API サーバー |
| PostgreSQL | PostgreSQL 16 + pgvector | 5432 | メインデータベース |
| Redis | Redis 7 Alpine | 6379 | キャッシュ / セッション |
| LLM Layer | マルチクラウド対応 | -- | Claude Sonnet / Haiku |
| Prometheus | prom/prometheus | 9090 | メトリクス収集 (オプション) |
| Grafana | grafana/grafana | 3001 | ダッシュボード (オプション) |

---

## 起動・停止手順

### Docker Compose 環境

```bash
# DB + Redis のみ起動
docker compose --profile db up -d

# 全サービス起動 (Backend + Frontend + DB + Redis)
docker compose --profile full up -d

# 監視系を含めた全サービス
docker compose --profile full --profile monitoring up -d

# 停止
docker compose --profile full down

# 全サービス停止 + ボリューム削除
docker compose --profile full down -v

# コンテナ状態確認
docker compose ps

# 特定サービスのログ確認
docker compose logs -f backend
docker compose logs -f postgres
```

### ローカル開発 (個別起動)

```bash
# 1. インフラ起動
docker compose --profile db up -d

# 2. バックエンド起動
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 3. フロントエンド起動 (別ターミナル)
cd frontend
npm run dev
```

### 本番環境 (Container Apps)

```bash
# バックエンドのリスタート
az containerapp revision restart \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision <revision-name>

# レプリカ数を0にして停止
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --min-replicas 0 --max-replicas 0

# 復旧 (レプリカ数を戻す)
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --min-replicas 2 --max-replicas 20
```

---

## ログ監視

### structlog 構造化ログ

FluentEdge AI は structlog による構造化ログを採用しています。

- **開発環境**: カラー付きコンソール出力
- **本番環境**: JSON 形式出力

### ログ出力形式

```json
{
  "event": "request_completed",
  "request_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "method": "POST",
  "path": "/api/talk/message",
  "status_code": 200,
  "duration_ms": 1523.45,
  "timestamp": "2026-02-14T10:30:15.123456Z",
  "level": "info"
}
```

### リクエストID追跡

全リクエストに UUID ベースのリクエストID (`X-Request-ID`) が自動付与されます。
レスポンスヘッダーにも同じ ID が返されるため、フロントエンドからバックエンドまでのトレーシングが可能です。

```bash
# レスポンスヘッダーでリクエストIDを確認
curl -i http://localhost:8000/health
# X-Request-ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### ログレベル設定

| 環境 | `LOG_LEVEL` | 出力内容 |
| --- | --- | --- |
| dev | `DEBUG` | 全ログ (SQL クエリ含む) |
| staging | `INFO` | 通常運用ログ |
| production | `WARNING` | 警告とエラーのみ |

### ローカル環境のログ確認

```bash
# バックエンドログ (ターミナルに直接出力)
uvicorn app.main:app --reload --port 8000

# PostgreSQL ログ
docker compose logs -f postgres

# Redis ログ
docker compose logs -f redis

# 全サービスのログを追跡
docker compose logs -f
```

### Azure 環境のログ確認

```bash
# Container Apps リアルタイムログ
az containerapp logs show \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --follow

# 直近 100 行
az containerapp logs show \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --tail 100
```

### ログ分析クエリ例 (KQL)

```text
// エラーログの抽出
ContainerAppConsoleLogs_CL
| where ContainerName_s == "fluentedge-backend"
| where Log_s contains "ERROR" or Log_s contains "error"
| order by TimeGenerated desc
| take 100

// リクエストID でのトレーシング
ContainerAppConsoleLogs_CL
| where Log_s contains "a1b2c3d4-5678-90ab"
| order by TimeGenerated asc

// 遅延リクエストの検出 (3秒超)
ContainerAppConsoleLogs_CL
| where Log_s contains "request_completed"
| where Log_s contains "duration_ms"
| extend parsed = parse_json(Log_s)
| where todouble(parsed.duration_ms) > 3000
| order by TimeGenerated desc

// LLM プロバイダーエラー
ContainerAppConsoleLogs_CL
| where Log_s contains "LLM_PROVIDER_ERROR" or Log_s contains "プロバイダー失敗"
| order by TimeGenerated desc
| take 50

// 1時間あたりのエラー率
ContainerAppConsoleLogs_CL
| where ContainerName_s == "fluentedge-backend"
| summarize
    total = count(),
    errors = countif(Log_s contains "ERROR")
    by bin(TimeGenerated, 1h)
| extend error_rate = toreal(errors) / toreal(total) * 100
| order by TimeGenerated desc
```

---

## ヘルスチェック

### エンドポイント

```bash
curl http://localhost:8000/health
```

レスポンス:

```json
{
  "status": "healthy",
  "service": "fluentedge-api"
}
```

### Docker Compose ヘルスチェック

docker-compose.yml で各サービスに healthcheck が設定されています:

| サービス | ヘルスチェック方法 | 間隔 |
| --- | --- | --- |
| PostgreSQL | `pg_isready -U fluentedge` | 5秒 |
| Redis | `redis-cli ping` | 5秒 |
| Backend | `httpx.get('http://localhost:8000/health')` | 30秒 |
| Frontend | `wget --spider http://localhost:3000/` | 30秒 |

### データベース・Redis の状態確認

```bash
# PostgreSQL 接続テスト
docker compose exec postgres pg_isready -U fluentedge

# PostgreSQL アクティブ接続数
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'fluentedge';"

# PostgreSQL テーブルサイズ
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT tablename, pg_size_pretty(pg_total_relation_size('public.' || tablename))
      FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size('public.' || tablename) DESC;"

# Redis 接続テスト
docker compose exec redis redis-cli ping

# Redis メモリ使用量
docker compose exec redis redis-cli info memory

# Redis キー数
docker compose exec redis redis-cli dbsize
```

---

## アラート設定

### 推奨アラートルール

| メトリクス | 閾値 | 重要度 | 説明 |
| --- | --- | --- | --- |
| CPU 使用率 | > 80% (5分間) | Warning | コンテナの CPU 逼迫 |
| メモリ使用率 | > 85% (5分間) | Warning | コンテナのメモリ逼迫 |
| HTTP 5xx エラー率 | > 1% (5分間) | Critical | サーバーエラーの多発 |
| レスポンスタイム P95 | > 3000ms (5分間) | Warning | レスポンス遅延 |
| PostgreSQL CPU | > 80% (5分間) | Warning | DB の CPU 逼迫 |
| PostgreSQL ストレージ | > 85% | Critical | DB のストレージ逼迫 |
| Redis メモリ使用率 | > 80% | Warning | キャッシュのメモリ逼迫 |
| LLM サーキットブレーカー | オープン状態 | Critical | LLM プロバイダー全断 |
| ヘルスチェック失敗 | 3回連続 | Critical | サービスダウン |

### Azure アラート設定例

```bash
# 月間予算アラート
az consumption budget create \
  --budget-name fluentedge-monthly \
  --amount 300 \
  --category Cost \
  --resource-group rg-fluentedge-production \
  --time-grain Monthly \
  --start-date 2026-02-01 \
  --end-date 2027-01-31
```

---

## バックアップ・リストア

### PostgreSQL バックアップ

#### ローカル環境

```bash
# ダンプ取得
docker compose exec postgres pg_dump -U fluentedge fluentedge > backup_$(date +%Y%m%d).sql

# テーブル単位のダンプ
docker compose exec postgres pg_dump -U fluentedge -t users fluentedge > users_backup.sql

# リストア
docker compose exec -T postgres psql -U fluentedge fluentedge < backup_20260214.sql
```

#### Azure 環境

Azure Database for PostgreSQL Flexible Server は自動バックアップが有効です (デフォルト 7 日間保持)。

```bash
# バックアップ状況の確認
az postgres flexible-server backup list \
  --resource-group rg-fluentedge-production \
  --name fluentedge-prod-pg

# ポイントインタイムリストア
az postgres flexible-server restore \
  --resource-group rg-fluentedge-production \
  --name fluentedge-prod-pg-restored \
  --source-server fluentedge-prod-pg \
  --restore-time "2026-02-14T10:00:00Z"
```

### Redis バックアップ

#### ローカル環境

```bash
# RDB スナップショットの手動トリガー
docker compose exec redis redis-cli BGSAVE

# スナップショットファイルの取得
docker compose cp redis:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

#### Azure 環境

Azure Cache for Redis の Standard SKU 以上でデータ永続化が有効です。

```bash
# エクスポート
az redis export \
  --name fluentedge-prod-redis \
  --resource-group rg-fluentedge-production \
  --prefix backup \
  --container <storage-container-sas-url>
```

---

## スケーリング

### Container Apps オートスケーリング

| パラメータ | dev | staging | production |
| --- | --- | --- | --- |
| CPU | 0.5 vCPU | 1.0 vCPU | 2.0 vCPU |
| メモリ | 1.0 GiB | 2.0 GiB | 4.0 GiB |
| 最小レプリカ | 0 | 1 | 2 |
| 最大レプリカ | 3 | 5 | 20 |
| ゼロスケール | 有効 | 無効 | 無効 |

### 手動スケーリング

```bash
# レプリカ数の手動調整
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --min-replicas 5 \
  --max-replicas 30

# PostgreSQL のスケールアップ
az postgres flexible-server update \
  --name fluentedge-prod-pg \
  --resource-group rg-fluentedge-production \
  --sku-name Standard_D8s_v3

# PostgreSQL ストレージ拡張 (ダウンタイムなし)
az postgres flexible-server update \
  --name fluentedge-prod-pg \
  --resource-group rg-fluentedge-production \
  --storage-size 512
```

---

## 障害対応

### LLM フォールバック

FluentEdge AI はマルチクラウド LLM 対応により、単一プロバイダー障害時に自動フォールバックします。

```text
障害発生フロー:
1. プライマリプロバイダー (Azure AI Foundry) でリクエスト失敗
2. RetryPolicy: 最大3回リトライ (exponential backoff)
3. リトライ全失敗 -> CircuitBreaker: 失敗カウント増加
4. 連続5回失敗 -> CircuitBreaker がオープン状態に遷移
5. フォールバックプロバイダー (Anthropic Direct) に自動切替
6. 60秒後に CircuitBreaker がハーフオープン -> プライマリで再試行
7. 成功すればプライマリに復帰
```

### LLM 障害対応手順

```bash
# 1. ログでエラー内容を確認
az containerapp logs show \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --tail 50

# 2. LLMプロバイダーの稼働状況を確認
# Azure: https://status.azure.com
# Anthropic: https://status.anthropic.com
# AWS: https://health.aws.amazon.com

# 3. 必要に応じて環境変数でプロバイダーを手動切替
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --set-env-vars "LLM_PROVIDER=anthropic"
```

### DB 接続エラー対応

```bash
# 1. PostgreSQL の状態確認
az postgres flexible-server show \
  --name fluentedge-prod-pg \
  --resource-group rg-fluentedge-production \
  --query "state"

# 2. 接続数の確認
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT count(*) FROM pg_stat_activity;"

# 3. アイドル接続の強制切断
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT pg_terminate_backend(pid)
      FROM pg_stat_activity
      WHERE state = 'idle' AND query_start < now() - interval '1 hour';"

# 4. バックエンドの再起動 (接続プールのリセット)
az containerapp revision restart \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision <current-revision>
```

### ロールバック手順

```bash
# 1. リビジョン一覧を確認
az containerapp revision list \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --output table

# 2. 前のリビジョンをアクティブ化
az containerapp revision activate \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision <previous-revision-name>

# 3. トラフィックを前のリビジョンに100%切替
az containerapp ingress traffic set \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision-weight <previous-revision-name>=100
```

---

## 定期メンテナンス

### 日次

| 作業 | 方法 | 担当 |
| --- | --- | --- |
| ヘルスチェック確認 | `/health` エンドポイント監視 | 自動 |
| エラーログ確認 | KQL クエリ / Grafana | 運用担当 |
| LLM サーキットブレーカー状態確認 | ログ確認 | 運用担当 |

### 週次

| 作業 | 方法 | 担当 |
| --- | --- | --- |
| DB バックアップの確認 | Azure Portal / az CLI | 運用担当 |
| Redis メモリ使用量の確認 | `redis-cli info memory` | 運用担当 |
| API レスポンスタイム分析 | KQL / Grafana | 運用担当 |
| セキュリティアラート確認 | GitHub Dependabot / pip-audit | 開発担当 |

### 月次

| 作業 | 方法 | 担当 |
| --- | --- | --- |
| 依存パッケージの更新確認 | `pip list --outdated` / `npm outdated` | 開発担当 |
| DB テーブルサイズの確認 | `pg_total_relation_size` | 運用担当 |
| LLM API コスト分析 | `api_usage_log` テーブル集計 | 運用担当 |
| SSL 証明書の有効期限確認 | Container Apps (自動更新) | 自動 |
| VACUUM ANALYZE の実行 | PostgreSQL メンテナンス | 運用担当 |

### DB メンテナンスコマンド

```bash
# テーブルの VACUUM ANALYZE (不要な行を回収し、統計情報を更新)
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "VACUUM ANALYZE;"

# レコード数確認
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT schemaname, tablename, n_live_tup
      FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"

# API 使用量コスト集計 (月次)
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT api_provider, model_name,
             SUM(input_tokens) as total_input,
             SUM(output_tokens) as total_output,
             SUM(estimated_cost_usd) as total_cost
      FROM api_usage_log
      WHERE created_at >= date_trunc('month', CURRENT_DATE)
      GROUP BY api_provider, model_name
      ORDER BY total_cost DESC;"
```

---

関連ドキュメント:

- [セットアップガイド](setup-guide.md) -- ローカル開発環境の構築
- [API リファレンス](api-reference.md) -- 全エンドポイントの仕様
- [デプロイメントガイド](deployment-guide.md) -- デプロイ手順
- [保守運用マニュアル](maintenance-manual.md) -- 詳細な保守手順
