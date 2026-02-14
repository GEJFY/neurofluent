# FluentEdge AI 保守運用マニュアル

FluentEdge AI の保守体制、定期運用、セキュリティアップデート、
依存関係更新、DB マイグレーション、障害復旧、パフォーマンスチューニング、
コスト最適化に関する詳細な手順書です。

---

## 目次

1. [保守体制](#保守体制)
2. [日次運用](#日次運用)
3. [週次運用](#週次運用)
4. [月次運用](#月次運用)
5. [セキュリティアップデート](#セキュリティアップデート)
6. [依存関係更新手順](#依存関係更新手順)
7. [DB マイグレーション手順](#db-マイグレーション手順)
8. [ローリングアップデート](#ローリングアップデート)
9. [障害復旧手順 (DR)](#障害復旧手順-dr)
10. [パフォーマンスチューニング](#パフォーマンスチューニング)
11. [コスト最適化](#コスト最適化)

---

## 保守体制

### 役割分担

| 役割 | 担当範囲 | 対応時間 |
| --- | --- | --- |
| 運用担当 | ヘルスチェック、ログ監視、アラート対応 | 平日 9:00-18:00 |
| 開発担当 | バグ修正、依存関係更新、パフォーマンス改善 | 平日 9:00-18:00 |
| 緊急対応 | サービスダウン、セキュリティインシデント | 24/7 (オンコール) |

### エスカレーションフロー

```text
1. アラート発報 (自動)
   |
2. 運用担当: 状況確認 (15分以内)
   |
   +-- 自力復旧可能 -> 対応実施 -> 報告
   |
   +-- 開発対応が必要 -> 開発担当にエスカレーション (30分以内)
       |
       +-- コード修正が必要 -> 緊急リリース手順
       |
       +-- インフラ問題 -> クラウドサポートに連絡
```

---

## 日次運用

### チェックリスト

| 項目 | 方法 | 確認基準 |
| --- | --- | --- |
| ヘルスチェック | `curl /health` | `200 OK` |
| エラーログ | KQL / Grafana | 5xx エラー率 < 1% |
| LLM 状態 | ログ確認 | サーキットブレーカーが closed |
| レスポンスタイム | メトリクス | P95 < 3000ms |
| Redis メモリ | `redis-cli info memory` | 使用率 < 80% |

### 自動化コマンド

```bash
# ヘルスチェック
curl -s http://localhost:8000/health | python -m json.tool

# 直近1時間のエラー数
docker compose logs --since 1h backend 2>&1 | grep -c "ERROR"

# Redis メモリ使用量
docker compose exec redis redis-cli info memory | grep used_memory_human
```

---

## 週次運用

### チェックリスト

| 項目 | 方法 | 確認基準 |
| --- | --- | --- |
| DB バックアップ確認 | Azure Portal / az CLI | バックアップが存在 |
| DB 容量確認 | `pg_total_relation_size` | 使用率 < 80% |
| Redis キー数 | `redis-cli dbsize` | 異常増加がない |
| セキュリティアラート | GitHub Dependabot | 重大な脆弱性がない |
| API コスト確認 | `api_usage_log` 集計 | 予算内 |

### 週次コマンド

```bash
# DB テーブルサイズ確認
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT tablename,
             pg_size_pretty(pg_total_relation_size('public.' || tablename)) as size,
             n_live_tup as rows
      FROM pg_tables
      LEFT JOIN pg_stat_user_tables USING (tablename)
      WHERE schemaname = 'public'
      ORDER BY pg_total_relation_size('public.' || tablename) DESC;"

# 今週の API コスト
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT api_provider, model_name,
             COUNT(*) as calls,
             SUM(input_tokens) as input_tok,
             SUM(output_tokens) as output_tok,
             ROUND(SUM(estimated_cost_usd)::numeric, 4) as cost_usd
      FROM api_usage_log
      WHERE created_at >= date_trunc('week', CURRENT_DATE)
      GROUP BY api_provider, model_name
      ORDER BY cost_usd DESC;"

# Dependabot アラート確認
gh api repos/{owner}/{repo}/dependabot/alerts --jq '.[].security_advisory.summary'
```

---

## 月次運用

### チェックリスト

| 項目 | 方法 | 確認基準 |
| --- | --- | --- |
| VACUUM ANALYZE | PostgreSQL コマンド | 実行完了 |
| 依存関係更新 | pip/npm チェック | 重大な更新を適用 |
| SSL 証明書確認 | Container Apps | 自動更新を確認 |
| ユーザー統計 | DB クエリ | 成長トレンド確認 |
| 月間コスト確認 | Azure Cost Management | 予算内 |
| パフォーマンスレビュー | メトリクス分析 | SLA 達成 |

### 月次コマンド

```bash
# VACUUM ANALYZE
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "VACUUM (VERBOSE, ANALYZE);"

# 月間ユーザー統計
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT
        COUNT(*) as total_users,
        COUNT(*) FILTER (WHERE created_at >= date_trunc('month', CURRENT_DATE)) as new_this_month,
        COUNT(*) FILTER (WHERE updated_at >= CURRENT_DATE - INTERVAL '30 days') as active_30d
      FROM users;"

# 月間 API コスト合計
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT
        api_provider,
        ROUND(SUM(estimated_cost_usd)::numeric, 2) as total_cost,
        SUM(input_tokens + output_tokens) as total_tokens
      FROM api_usage_log
      WHERE created_at >= date_trunc('month', CURRENT_DATE)
      GROUP BY api_provider
      ORDER BY total_cost DESC;"
```

---

## セキュリティアップデート

### Python 依存関係

```bash
cd backend

# 脆弱性スキャン
pip install pip-audit
pip-audit -r requirements.txt

# 重大な脆弱性がある場合
pip install <package>==<fixed-version>
# requirements.txt を更新
# テスト実行後にコミット
```

### Node.js 依存関係

```bash
cd frontend

# 脆弱性スキャン
npm audit

# 自動修正
npm audit fix

# 重大な脆弱性の手動修正
npm install <package>@<fixed-version>
```

### Docker イメージ

```bash
# Trivy でコンテナスキャン
docker build -t fluentedge-backend:scan ./backend
trivy image fluentedge-backend:scan

# ベースイメージの更新
# Dockerfile の FROM を最新の python:3.11-slim に更新
```

### 対応優先度

| 重要度 | 対応期限 | 例 |
| --- | --- | --- |
| Critical | 24 時間以内 | リモートコード実行、認証バイパス |
| High | 1 週間以内 | SQL インジェクション、XSS |
| Medium | 次回リリース | DoS、情報漏洩 (限定的) |
| Low | 任意 | 最小限の影響 |

---

## 依存関係更新手順

### バックエンド (Python)

```bash
cd backend
source venv/bin/activate

# 更新可能なパッケージ一覧
pip list --outdated

# 個別パッケージの更新
pip install <package>==<new-version>

# テスト実行
pytest -v

# requirements.txt の更新
pip freeze > requirements.txt.new
# 差分を確認して requirements.txt に反映
```

### フロントエンド (Node.js)

```bash
cd frontend

# 更新可能なパッケージ一覧
npm outdated

# パッチバージョンの一括更新
npm update

# メジャーバージョンの更新
npx npm-check-updates -u
npm install

# テスト実行
npm run test:run
npm run build
npm run lint
```

### 更新時の注意事項

- FastAPI のメジャーバージョンアップは API 互換性を確認
- Next.js のメジャーバージョンアップは App Router の破壊的変更を確認
- SQLAlchemy のバージョンアップは async API の互換性を確認
- 更新後は必ず全テスト (pytest + Vitest + E2E) を実行
- CI が全てパスしてからマージ

---

## DB マイグレーション手順

### 開発環境

```bash
cd backend
source venv/bin/activate

# 1. モデルを変更

# 2. マイグレーションファイル生成
alembic revision --autogenerate -m "add column xxx to table yyy"

# 3. 生成されたファイルを確認・修正
# alembic/versions/ のファイルを開いて確認

# 4. マイグレーション適用
alembic upgrade head

# 5. テスト実行
pytest -v
```

### 本番環境

```bash
# 1. バックアップ取得 (必須)
az postgres flexible-server backup list \
  --resource-group rg-fluentedge-production \
  --name fluentedge-prod-pg

# 2. ステージング環境で先にテスト
alembic upgrade head  # staging DB

# 3. メンテナンス通知 (必要に応じて)

# 4. 本番マイグレーション実行
# Container Apps のバックエンドコンテナから実行
# または、CI/CD パイプラインのデプロイステップで自動実行

# 5. マイグレーション確認
alembic current
alembic history

# 6. ロールバック (問題発生時)
alembic downgrade -1
```

### 破壊的変更がある場合

カラム削除やテーブル構造の大幅変更は、2 段階でデプロイします:

```text
Phase 1: 新しいカラム/テーブルを追加 (既存と共存)
  -> アプリケーション更新 (新カラムを使用)
  -> 動作確認

Phase 2: 旧カラム/テーブルを削除
  -> マイグレーション実行
```

---

## ローリングアップデート

### Container Apps のローリングデプロイ

```bash
# 1. 新しいイメージをビルド・プッシュ
docker build -t $ACR_NAME.azurecr.io/fluentedge-backend:v2.0.0 ./backend
docker push $ACR_NAME.azurecr.io/fluentedge-backend:v2.0.0

# 2. Container Apps を更新 (自動的にローリングデプロイ)
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --image $ACR_NAME.azurecr.io/fluentedge-backend:v2.0.0

# 3. 新リビジョンの状態確認
az containerapp revision list \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --output table

# 4. ヘルスチェック
BACKEND_URL=$(az containerapp show \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --query properties.configuration.ingress.fqdn -o tsv)
curl "https://$BACKEND_URL/health"
```

### カナリアデプロイ (段階的切替)

```bash
# 新旧バージョンでトラフィック分割
az containerapp ingress traffic set \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision-weight \
    <new-revision>=10 \
    <old-revision>=90

# 問題なければ比率を上げる
az containerapp ingress traffic set \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision-weight \
    <new-revision>=50 \
    <old-revision>=50

# 全トラフィックを新バージョンに
az containerapp ingress traffic set \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision-weight <new-revision>=100
```

---

## 障害復旧手順 (DR)

### RTO / RPO 目標

| 指標 | dev | staging | production |
| --- | --- | --- | --- |
| RTO (復旧時間目標) | 4 時間 | 2 時間 | 30 分 |
| RPO (データ損失許容) | 24 時間 | 1 時間 | 15 分 |

### DB 障害からの復旧

```bash
# 1. 最新のバックアップを確認
az postgres flexible-server backup list \
  --resource-group rg-fluentedge-production \
  --name fluentedge-prod-pg

# 2. ポイントインタイムリストア
az postgres flexible-server restore \
  --resource-group rg-fluentedge-production \
  --name fluentedge-prod-pg-restored \
  --source-server fluentedge-prod-pg \
  --restore-time "2026-02-14T10:00:00Z"

# 3. 接続先の切替
# Container Apps の DATABASE_URL を新サーバーに変更

# 4. アプリケーション再起動
az containerapp revision restart \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --revision <current-revision>
```

### 全サービスダウンからの復旧

```bash
# 1. インフラの状態確認
az containerapp show --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production --query "properties.runningStatus"

# 2. Terraform で再デプロイ (最終手段)
cd infra/terraform
terraform apply -var-file=environments/prod.tfvars

# 3. DB マイグレーション確認
alembic current
alembic upgrade head

# 4. ヘルスチェック
curl https://api.fluentedge.ai/health
```

### LLM 全プロバイダーダウン

```bash
# 1. 各プロバイダーのステータス確認
# Azure: https://status.azure.com
# Anthropic: https://status.anthropic.com
# AWS: https://health.aws.amazon.com

# 2. 利用可能なプロバイダーに切替
az containerapp update \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --set-env-vars "LLM_PROVIDER=anthropic"

# 3. 全プロバイダーが復旧不可能な場合
# -> メンテナンスモードに切替
# -> ユーザーに通知
# -> LLM 非依存機能 (復習、ダッシュボード) は継続利用可能
```

---

## パフォーマンスチューニング

### バックエンド

| 設定 | 開発 | 本番 | 調整方法 |
| --- | --- | --- | --- |
| Uvicorn ワーカー | 1 | CPU x 2 + 1 | `--workers N` |
| DB コネクションプール | 5 | 20 | `pool_size` |
| DB max_overflow | 10 | 30 | `max_overflow` |
| 会話履歴の送信数 | 10 | 6 | プロンプトで制御 |
| LLM max_tokens | 2048 | 512-1024 | API 呼び出し時 |

### データベース

```bash
# スロークエリの検出
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT query, calls, mean_exec_time, total_exec_time
      FROM pg_stat_statements
      ORDER BY mean_exec_time DESC LIMIT 10;"

# インデックスの追加
docker compose exec postgres psql -U fluentedge -d fluentedge -c "
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_review_items_user_next_review
    ON review_items (user_id, next_review_at);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversation_sessions_user_started
    ON conversation_sessions (user_id, started_at DESC);
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_daily_stats_user_date
    ON daily_stats (user_id, date DESC);
"
```

### Redis キャッシュ戦略

| データ | TTL | 用途 |
| --- | --- | --- |
| ダッシュボード統計 | 5 分 | 頻繁なクエリ軽減 |
| セッションデータ | 24 時間 | JWT 検証キャッシュ |
| エクササイズ結果 | 1 時間 | 一時データ保存 |
| LLM 応答キャッシュ | 1 時間 | 同一プロンプトの重複削減 |

---

## コスト最適化

### LLM コスト削減

| 施策 | 効果 | 実装方法 |
| --- | --- | --- |
| Haiku 活用 | Sonnet の約 1/10 | 評価・スコアリングは Haiku |
| 会話履歴圧縮 | トークン数 30-50% 削減 | 直近 N ターンのみ送信 |
| プロンプト最適化 | トークン数 10-20% 削減 | 冗長な指示を削除 |
| キャッシュ活用 | API 呼び出し 10-30% 削減 | 同一パターンの問題をキャッシュ |
| ローカル LLM (dev) | 開発コスト 0 | Ollama で開発 |

### インフラコスト削減

| 施策 | 効果 | 対象 |
| --- | --- | --- |
| dev ゼロスケール | 未使用時の課金なし | Container Apps |
| Burstable SKU | 低負荷時に低コスト | PostgreSQL (dev) |
| 予約インスタンス | 最大 40% 割引 | PostgreSQL (prod) |
| 夜間停止 | 営業時間外のコスト削減 | dev/staging 環境 |
| ログ保持期間 | ストレージコスト削減 | Log Analytics |

### コスト監視

```bash
# Azure コスト確認
az cost management query \
  --type Usage \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-fluentedge-production" \
  --timeframe MonthToDate

# LLM API コスト (アプリ内データ)
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT
        DATE(created_at) as date,
        api_provider,
        ROUND(SUM(estimated_cost_usd)::numeric, 4) as daily_cost
      FROM api_usage_log
      WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
      GROUP BY DATE(created_at), api_provider
      ORDER BY date DESC, daily_cost DESC;"
```

---

関連ドキュメント:

- [運用マニュアル](operation-manual.md) -- 基本的な運用手順
- [デプロイガイド](deployment-guide.md) -- デプロイ手順
- [アーキテクチャ設計書](architecture.md) -- システム構成
