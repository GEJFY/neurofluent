# FluentEdge AI デプロイガイド

FluentEdge AI のデプロイ手順書です。Docker Compose による開発・小規模デプロイ、
Terraform によるマルチクラウドデプロイ (Azure / AWS / GCP)、GitHub Actions CI/CD、
環境変数管理、SSL/TLS 設定を網羅しています。

---

## 目次

1. [デプロイ方式の選択](#デプロイ方式の選択)
2. [Docker Compose デプロイ](#docker-compose-デプロイ)
3. [Terraform デプロイ](#terraform-デプロイ)
4. [CI/CD パイプライン (GitHub Actions)](#cicd-パイプライン-github-actions)
5. [環境変数一覧テーブル](#環境変数一覧テーブル)
6. [SSL/TLS 設定](#ssltls-設定)
7. [デプロイチェックリスト](#デプロイチェックリスト)
8. [コスト見積もり](#コスト見積もり)

---

## デプロイ方式の選択

| 方式 | 用途 | クラウド | 複雑度 |
| --- | --- | --- | --- |
| Docker Compose | 開発・小規模・デモ | ローカル / 単一 VM | 低 |
| Terraform + Azure | 本番 (Azure) | Azure Container Apps | 中 |
| Terraform + AWS | 本番 (AWS) | ECS Fargate | 中 |
| Terraform + GCP | 本番 (GCP) | Cloud Run | 中 |
| Bicep (レガシー) | Azure 限定 | Azure Container Apps | 中 |

---

## Docker Compose デプロイ

開発環境や小規模なデモ環境向けのデプロイ方法です。

### プロファイル構成

| プロファイル | 含まれるサービス | 用途 |
| --- | --- | --- |
| `db` | PostgreSQL, Redis | DB のみ (ローカル開発) |
| `full` | PostgreSQL, Redis, Backend, Frontend | 全サービス |
| `monitoring` | Prometheus, Grafana | 監視 (オプション) |

### 起動手順

```bash
# 1. 環境変数の設定
cp .env.example .env
# .env を編集

# 2. 全サービス起動
docker compose --profile full up -d

# 3. 動作確認
curl http://localhost:8500/health
curl http://localhost:3500

# 4. 監視系も含めて起動する場合
docker compose --profile full --profile monitoring up -d
```

### リソース制限

docker-compose.yml で設定済みのメモリ制限:

| サービス | メモリ上限 |
| --- | --- |
| PostgreSQL | 512 MB |
| Redis | 256 MB |
| Backend | 1 GB |
| Frontend | 512 MB |
| Prometheus | 256 MB |
| Grafana | 256 MB |

### 本番用の Docker Compose 運用

単一サーバーで本番運用する場合は、以下の追加設定を推奨します:

```bash
# リバースプロキシ (nginx) を前段に配置
# SSL 終端を nginx で処理
# restart: unless-stopped が設定済み

# バックアップの自動化
crontab -e
# 毎日 3:00 に DB バックアップ
0 3 * * * docker compose exec -T postgres pg_dump -U fluentedge fluentedge > /backup/db_$(date +\%Y\%m\%d).sql
```

---

## Terraform デプロイ

### 前提条件

| ツール | バージョン | 確認コマンド |
| --- | --- | --- |
| Terraform | >= 1.7.0 | `terraform version` |
| Azure CLI | 最新版 | `az --version` |
| AWS CLI | 最新版 (AWS の場合) | `aws --version` |
| gcloud CLI | 最新版 (GCP の場合) | `gcloud version` |
| Docker | 最新版 | `docker --version` |

### ディレクトリ構成

```text
infra/terraform/
  main.tf                    # ルートモジュール (クラウド選択)
  variables.tf               # 入力変数定義
  outputs.tf                 # 出力定義
  providers.tf               # プロバイダー設定
  modules/
    azure/                   # Azure モジュール
      main.tf                #   Container Apps, PostgreSQL, Redis, ACR, Key Vault
      variables.tf
      outputs.tf
    aws/                     # AWS モジュール
      main.tf                #   ECS Fargate, RDS, ElastiCache, ECR
      variables.tf
      outputs.tf
    gcp/                     # GCP モジュール
      main.tf                #   Cloud Run, Cloud SQL, Memorystore, Artifact Registry
      variables.tf
      outputs.tf
  shared/
    networking.tf            # 共通ネットワーク設定
    dns.tf                   # DNS 設定
    monitoring.tf            # 監視設定
  environments/
    dev.tfvars               # 開発環境パラメータ
    staging.tfvars           # ステージング環境パラメータ
    prod.tfvars              # 本番環境パラメータ
```

### クラウド選択

`cloud_provider` 変数で Azure / AWS / GCP を切り替えます:

```hcl
variable "cloud_provider" {
  description = "デプロイ先クラウド (azure, aws, gcp)"
  type        = string
  default     = "azure"
}
```

### Azure へのデプロイ

```bash
# 1. Azure CLI にログイン
az login
az account set --subscription "<subscription-id>"

# 2. リモートステート用ストレージの作成 (初回のみ)
az group create --name fluentedge-tfstate --location japaneast
az storage account create --name fluentedgetfstate \
  --resource-group fluentedge-tfstate --sku Standard_LRS
az storage container create --name tfstate \
  --account-name fluentedgetfstate

# 3. Terraform 初期化
cd infra/terraform
terraform init

# 4. プラン確認
terraform plan -var-file=environments/dev.tfvars

# 5. デプロイ実行
terraform apply -var-file=environments/dev.tfvars
```

### AWS へのデプロイ

```bash
# 1. AWS CLI 設定
aws configure

# 2. Terraform 初期化・デプロイ
cd infra/terraform
terraform init
terraform plan \
  -var="cloud_provider=aws" \
  -var-file=environments/dev.tfvars
terraform apply \
  -var="cloud_provider=aws" \
  -var-file=environments/dev.tfvars
```

### GCP へのデプロイ

```bash
# 1. gcloud CLI 設定
gcloud auth application-default login
gcloud config set project <project-id>

# 2. Terraform 初期化・デプロイ
cd infra/terraform
terraform init
terraform plan \
  -var="cloud_provider=gcp" \
  -var="gcp_project_id=<project-id>" \
  -var-file=environments/dev.tfvars
terraform apply \
  -var="cloud_provider=gcp" \
  -var="gcp_project_id=<project-id>" \
  -var-file=environments/dev.tfvars
```

### 環境別パラメータ

#### dev.tfvars

```hcl
environment    = "dev"
cloud_provider = "azure"
azure_location = "japaneast"
database_sku   = "B_Standard_B1ms"
redis_sku      = "Basic"
```

#### staging.tfvars

```hcl
environment    = "staging"
cloud_provider = "azure"
azure_location = "japaneast"
database_sku   = "GP_Standard_D2s_v3"
redis_sku      = "Standard"
```

#### prod.tfvars

```hcl
environment    = "prod"
cloud_provider = "azure"
azure_location = "japaneast"
database_sku   = "GP_Standard_D4s_v3"
redis_sku      = "Standard"
```

### Terraform 管理コマンド

```bash
# 現在の状態確認
terraform show

# 特定リソースの削除
terraform destroy -target=module.azure[0].azurerm_container_app.backend

# 全リソース削除 (要注意)
terraform destroy -var-file=environments/dev.tfvars

# ステート操作
terraform state list
terraform state show <resource-address>
```

---

## CI/CD パイプライン (GitHub Actions)

### ワークフロー構成

```text
.github/workflows/
  ci.yml       # テスト・Lint・セキュリティスキャン (PR / push)
  deploy.yml   # デプロイ (main マージ時)
  e2e.yml      # E2E テスト (デプロイ後)
```

### CI ワークフロー (ci.yml)

PR とプッシュ時に自動実行される CI パイプラインです。

```text
ジョブ構成:
1. backend-test    -- Python Lint (Ruff) + pytest + カバレッジ
2. frontend-test   -- ESLint + Vitest + Next.js ビルド
3. security-scan   -- pip-audit + npm audit
4. docker-build    -- Docker イメージビルド検証
5. container-scan  -- Trivy コンテナスキャン (PR のみ)
```

実行条件:

| イベント | ブランチ | 実行ジョブ |
| --- | --- | --- |
| push | main, develop | 全ジョブ |
| pull_request | main | 全ジョブ |

### デプロイワークフロー (deploy.yml)

main ブランチへのマージ時に自動デプロイを実行します。

```text
デプロイフロー:
1. コードのチェックアウト
2. Azure CLI ログイン (サービスプリンシパル)
3. Docker イメージのビルド
4. ACR / ECR / Artifact Registry へのプッシュ
5. Container Apps / ECS / Cloud Run の更新
6. ヘルスチェック確認
7. Slack / Teams 通知 (本番のみ)
```

### 必要な GitHub Secrets

| シークレット名 | 説明 | 必須 |
| --- | --- | --- |
| `AZURE_CREDENTIALS` | Azure サービスプリンシパル JSON | Azure デプロイ時 |
| `ACR_LOGIN_SERVER` | ACR ログインサーバー | Azure デプロイ時 |
| `ACR_USERNAME` | ACR ユーザー名 | Azure デプロイ時 |
| `ACR_PASSWORD` | ACR パスワード | Azure デプロイ時 |
| `AWS_ACCESS_KEY_ID` | AWS アクセスキー | AWS デプロイ時 |
| `AWS_SECRET_ACCESS_KEY` | AWS シークレットキー | AWS デプロイ時 |
| `GCP_SA_KEY` | GCP サービスアカウントキー | GCP デプロイ時 |
| `CODECOV_TOKEN` | Codecov トークン | カバレッジ連携時 |

### サービスプリンシパルの作成 (Azure)

```bash
az ad sp create-for-rbac \
  --name "github-actions-fluentedge" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/rg-fluentedge-dev \
  --json-auth
```

出力された JSON を GitHub Secrets の `AZURE_CREDENTIALS` に設定します。

---

## 環境変数一覧テーブル

### 環境別の差異

| 変数 | dev | staging | production |
| --- | --- | --- | --- |
| `ENVIRONMENT` | dev | staging | production |
| `LOG_LEVEL` | DEBUG | INFO | WARNING |
| `JWT_EXPIRY_HOURS` | 24 | 12 | 8 |
| `BACKEND_CORS_ORIGINS` | localhost:3500 | staging.fluentedge.ai | fluentedge.ai |
| `LLM_PROVIDER` | local / azure_foundry | azure_foundry | azure_foundry |
| `LLM_FALLBACK_PROVIDERS` | (なし) | anthropic | anthropic,bedrock |
| `LLM_RATE_LIMIT_RPM` | 60 | 60 | 120 |

### シークレット管理

本番環境ではシークレットをクラウドのシークレットマネージャーで管理します:

| クラウド | サービス | コマンド例 |
| --- | --- | --- |
| Azure | Key Vault | `az keyvault secret set --vault-name <kv> --name <key> --value <val>` |
| AWS | Secrets Manager | `aws secretsmanager create-secret --name <key> --secret-string <val>` |
| GCP | Secret Manager | `gcloud secrets create <key> --data-file=<file>` |

### Azure Key Vault への登録例

```bash
KV_NAME=fluentedge-prod-kv

az keyvault secret set --vault-name $KV_NAME \
  --name azure-ai-foundry-api-key --value "<your-api-key>"

az keyvault secret set --vault-name $KV_NAME \
  --name jwt-secret-key --value "$(openssl rand -hex 32)"

az keyvault secret set --vault-name $KV_NAME \
  --name stripe-secret-key --value "<your-stripe-key>"

az keyvault secret set --vault-name $KV_NAME \
  --name database-password --value "<secure-password>"
```

---

## SSL/TLS 設定

### Docker Compose 環境 (開発)

開発環境では HTTP (ポート 8500 / 3500) で動作します。
HTTPS が必要な場合は nginx をリバースプロキシとして追加します:

```bash
# Let's Encrypt + nginx の例
# docker-compose.yml に追加するか、Caddy を利用
```

### Azure Container Apps

Container Apps はデフォルトで `*.azurecontainerapps.io` ドメインの SSL 証明書を提供します。

**カスタムドメインの設定**:

```bash
# 1. DNS レコード追加
# api.fluentedge.ai CNAME fluentedge-prod-backend.azurecontainerapps.io

# 2. ホスト名バインド
az containerapp hostname add \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --hostname api.fluentedge.ai

# 3. マネージド証明書バインド
az containerapp hostname bind \
  --name fluentedge-prod-backend \
  --resource-group rg-fluentedge-production \
  --hostname api.fluentedge.ai \
  --environment fluentedge-prod-cae \
  --validation-method CNAME
```

マネージド証明書は自動更新されるため手動更新は不要です。

### AWS / GCP

- **AWS**: Application Load Balancer + ACM (AWS Certificate Manager) で SSL 終端
- **GCP**: Cloud Run のデフォルト SSL またはカスタムドメイン + Cloud Armor

---

## デプロイチェックリスト

### 本番デプロイ前の確認

- [ ] 全テストが CI でパスしていること
- [ ] Docker イメージのビルドが成功していること
- [ ] 環境変数 / シークレットが全て設定されていること
- [ ] データベースマイグレーションが準備されていること
- [ ] CORS 設定が本番ドメインに対応していること
- [ ] JWT シークレットが十分な長さのランダム文字列であること
- [ ] SSL 証明書が正常にバインドされていること
- [ ] ヘルスチェックが正常に応答すること
- [ ] アラートルールが設定されていること
- [ ] バックアップが正常に動作していること
- [ ] ロールバック手順が確認されていること
- [ ] LLM フォールバックプロバイダーが設定されていること

### デプロイ後の確認

- [ ] `/health` エンドポイントが `200 OK` を返すこと
- [ ] ユーザー登録・ログインが機能すること
- [ ] AI 会話 (LLM 呼び出し) が正常に動作すること
- [ ] フロントエンドが正常に表示されること
- [ ] エラーログに異常がないこと

---

## コスト見積もり

### 月間コスト概算 (Azure)

| リソース | dev | staging | production (100ユーザー) |
| --- | --- | --- | --- |
| Container Apps | 約 $15 | 約 $50 | 約 $200 |
| PostgreSQL | 約 $30 | 約 $100 | 約 $400 |
| Redis | 約 $0 | 約 $50 | 約 $100 |
| Container Registry | 約 $5 | 約 $5 | 約 $20 |
| Key Vault | 約 $1 | 約 $1 | 約 $1 |
| Claude API | 約 $10 | 約 $50 | 約 $500-2,000 |
| Log Analytics | 約 $5 | 約 $10 | 約 $30 |
| **合計** | **約 $66** | **約 $266** | **約 $1,251-2,751** |

### コスト最適化

| 施策 | 対象 | 効果 |
| --- | --- | --- |
| dev ゼロスケール | Container Apps | 未使用時の課金削減 |
| Burstable SKU | PostgreSQL (dev) | 低コスト |
| Claude Haiku 活用 | API コスト | Sonnet の約 1/10 |
| 会話履歴圧縮 | API コスト | トークン数削減 |
| Redis キャッシュ | 全体 | DB クエリ削減 |
| 予約インスタンス | PostgreSQL (prod) | 最大 40% 割引 |
| ローカル LLM (Ollama) | 開発環境 | API コスト 0 |

---

関連ドキュメント:

- [セットアップガイド](setup-guide.md) -- ローカル環境構築
- [運用マニュアル](operation-manual.md) -- 運用手順
- [保守運用マニュアル](maintenance-manual.md) -- 保守手順
- [アーキテクチャ設計書](architecture.md) -- システム構成
