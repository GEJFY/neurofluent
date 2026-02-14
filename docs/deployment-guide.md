# デプロイメントガイド

FluentEdge AI を Azure にデプロイするための手順書です。Bicep テンプレートによる IaC を採用し、dev / staging / production の 3 環境構成をサポートします。

---

## 目次

1. [Azure 前提条件](#azure-前提条件)
2. [Bicep によるリソースデプロイ](#bicep-によるリソースデプロイ)
3. [Docker イメージのビルドと ACR へのプッシュ](#docker-イメージのビルドと-acr-へのプッシュ)
4. [Container Apps へのデプロイ](#container-apps-へのデプロイ)
5. [環境変数の設定 (Azure)](#環境変数の設定-azure)
6. [SSL / カスタムドメインの設定](#ssl--カスタムドメインの設定)
7. [モニタリングとログ](#モニタリングとログ)
8. [スケーリング設定](#スケーリング設定)
9. [CI/CD 統合の概要](#cicd-統合の概要)
10. [コスト見積もり (環境別)](#コスト見積もり-環境別)

---

## Azure 前提条件

### 必要なもの

| 項目 | 説明 |
| --- | --- |
| Azure サブスクリプション | 有効なサブスクリプション |
| Azure CLI | 最新バージョン (`az --version` で確認) |
| Docker | ローカルでのイメージビルド用 |
| リソースグループ | 環境ごとに作成 |
| Azure AI Foundry アクセス | Claude Sonnet 4.5 / Haiku 4.5 のデプロイ済み |

### Azure CLI のセットアップ

```bash
# Azure CLI のインストール確認
az --version

# ログイン
az login

# サブスクリプションの確認・切り替え
az account show
az account set --subscription "<subscription-id>"

# 必要なプロバイダーの登録
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
az provider register --namespace Microsoft.KeyVault
```

### リソースグループの作成

```bash
# 開発環境
az group create --name rg-fluentedge-dev --location eastus2

# ステージング環境
az group create --name rg-fluentedge-staging --location eastus2

# 本番環境
az group create --name rg-fluentedge-production --location eastus2
```

> **リージョン**: `eastus2` を推奨します。Azure AI Foundry の Claude モデルの可用性が高いリージョンです。

---

## Bicep によるリソースデプロイ

### Bicep テンプレートの構成

```text
infra/
├── main.bicep                  # メインオーケストレーション
├── modules/
│   ├── container-apps.bicep    # Container Apps Environment + Backend/Frontend
│   ├── container-registry.bicep # Azure Container Registry
│   ├── postgresql.bicep        # PostgreSQL Flexible Server
│   ├── redis.bicep             # Azure Cache for Redis
│   └── key-vault.bicep         # Azure Key Vault
└── environments/
    └── dev.bicepparam          # 開発環境パラメータ
```

### 作成されるリソース

| リソース | 命名規則 | 説明 |
| --- | --- | --- |
| Container Apps Environment | `fluentedge-<env>-cae` | バックエンド + フロントエンドコンテナ |
| Container Registry | `fluentedge<env>acr` | Docker イメージ管理 |
| PostgreSQL Flexible Server | `fluentedge-<env>-pg` | pgvector 拡張対応データベース |
| Azure Cache for Redis | `fluentedge-<env>-redis` | セッション・キャッシュ |
| Key Vault | `fluentedge-<env>-kv` | シークレット管理 |

### デプロイコマンド

#### 開発環境

```bash
az deployment group create \
  --resource-group rg-fluentedge-dev \
  --template-file infra/main.bicep \
  --parameters infra/environments/dev.bicepparam
```

#### ステージング環境

```bash
az deployment group create \
  --resource-group rg-fluentedge-staging \
  --template-file infra/main.bicep \
  --parameters environment=staging
```

#### 本番環境

```bash
az deployment group create \
  --resource-group rg-fluentedge-production \
  --template-file infra/main.bicep \
  --parameters environment=production
```

### デプロイ出力の確認

```bash
# デプロイ結果の出力を確認
az deployment group show \
  --resource-group rg-fluentedge-dev \
  --name main \
  --query properties.outputs
```

出力例:

```json
{
  "acrLoginServer": {"value": "fluentedgedevacr.azurecr.io"},
  "keyVaultName": {"value": "fluentedge-dev-kv"},
  "backendUrl": {"value": "https://fluentedge-dev-backend.azurecontainerapps.io"},
  "frontendUrl": {"value": "https://fluentedge-dev-frontend.azurecontainerapps.io"}
}
```

---

## Docker イメージのビルドと ACR へのプッシュ

### ACR へのログイン

```bash
ACR_NAME=fluentedgedevacr  # 環境に応じて変更
az acr login --name $ACR_NAME
```

### バックエンドイメージのビルドとプッシュ

```bash
# ビルド
docker build -t $ACR_NAME.azurecr.io/fluentedge-backend:latest ./backend

# タグ付け (バージョン管理)
docker tag $ACR_NAME.azurecr.io/fluentedge-backend:latest \
  $ACR_NAME.azurecr.io/fluentedge-backend:v$(date +%Y%m%d-%H%M%S)

# プッシュ
docker push $ACR_NAME.azurecr.io/fluentedge-backend:latest
docker push $ACR_NAME.azurecr.io/fluentedge-backend:v$(date +%Y%m%d-%H%M%S)
```

### フロントエンドイメージのビルドとプッシュ

> フロントエンドの Dockerfile は `frontend/Dockerfile` に作成する必要があります (未作成の場合)。

```bash
# ビルド
docker build -t $ACR_NAME.azurecr.io/fluentedge-frontend:latest ./frontend

# プッシュ
docker push $ACR_NAME.azurecr.io/fluentedge-frontend:latest
```

### ACR Task によるクラウドビルド (代替手段)

ローカルでビルドせず、ACR Task でクラウドビルドすることも可能です。

```bash
# バックエンド
az acr build \
  --registry $ACR_NAME \
  --image fluentedge-backend:latest \
  --file backend/Dockerfile \
  ./backend

# フロントエンド
az acr build \
  --registry $ACR_NAME \
  --image fluentedge-frontend:latest \
  --file frontend/Dockerfile \
  ./frontend
```

---

## Container Apps へのデプロイ

### 初回デプロイ (Bicep 経由)

初回は Bicep テンプレートのデプロイ時に Container Apps が作成されます。

### イメージの更新

```bash
RG_NAME=rg-fluentedge-dev  # 環境に応じて変更

# バックエンドの更新
az containerapp update \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --image $ACR_NAME.azurecr.io/fluentedge-backend:latest

# フロントエンドの更新
az containerapp update \
  --name fluentedge-dev-frontend \
  --resource-group $RG_NAME \
  --image $ACR_NAME.azurecr.io/fluentedge-frontend:latest
```

### デプロイ後の確認

```bash
# ヘルスチェック
BACKEND_URL=$(az containerapp show \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --query properties.configuration.ingress.fqdn -o tsv)

curl "https://$BACKEND_URL/health"
# 期待レスポンス: {"status":"healthy","service":"fluentedge-api"}

# ログ確認
az containerapp logs show \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --follow
```

### ロールバック

問題が発生した場合、前のリビジョンにロールバックできます。

```bash
# リビジョン一覧を確認
az containerapp revision list \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --output table

# 前のリビジョンをアクティブ化
az containerapp revision activate \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --revision <previous-revision-name>

# トラフィックを前のリビジョンに 100% 切り替え
az containerapp ingress traffic set \
  --name fluentedge-dev-backend \
  --resource-group $RG_NAME \
  --revision-weight <previous-revision-name>=100
```

---

## 環境変数の設定 (Azure)

### Key Vault へのシークレット登録

```bash
KV_NAME=fluentedge-dev-kv  # 環境に応じて変更

# Claude API キー
az keyvault secret set --vault-name $KV_NAME \
  --name azure-ai-foundry-api-key \
  --value "<your-api-key>"

# Claude API エンドポイント
az keyvault secret set --vault-name $KV_NAME \
  --name azure-ai-foundry-endpoint \
  --value "https://<endpoint>.services.ai.azure.com/"

# JWT シークレット (ランダム生成)
az keyvault secret set --vault-name $KV_NAME \
  --name jwt-secret-key \
  --value "$(openssl rand -hex 32)"

# データベースパスワード (自動生成される場合はスキップ)
az keyvault secret set --vault-name $KV_NAME \
  --name database-password \
  --value "<secure-password>"
```

### Container Apps の環境変数設定

```bash
# 環境変数を設定 (Key Vault 参照)
az containerapp update \
  --name fluentedge-dev-backend \
  --resource-group rg-fluentedge-dev \
  --set-env-vars \
    "ENVIRONMENT=dev" \
    "LOG_LEVEL=INFO" \
    "BACKEND_CORS_ORIGINS=https://fluentedge-dev-frontend.azurecontainerapps.io" \
    "CLAUDE_SONNET_MODEL=claude-sonnet-4-5-20250929" \
    "CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001" \
    "JWT_ALGORITHM=HS256" \
    "JWT_EXPIRY_HOURS=24"
```

### 環境変数の差異 (環境別)

| 変数 | dev | staging | production |
| --- | --- | --- | --- |
| `ENVIRONMENT` | dev | staging | production |
| `LOG_LEVEL` | DEBUG | INFO | WARNING |
| `JWT_EXPIRY_HOURS` | 24 | 12 | 8 |
| `BACKEND_CORS_ORIGINS` | `https://<dev-frontend>` | `https://staging.fluentedge.ai` | `https://fluentedge.ai` |

---

## SSL / カスタムドメインの設定

### Container Apps のデフォルト SSL

Container Apps はデフォルトで `*.azurecontainerapps.io` ドメインの SSL 証明書を提供します。追加の設定は不要です。

### カスタムドメインの設定

#### ステップ 1: DNS レコードの追加

DNS プロバイダーで以下のレコードを追加します:

```text
# CNAME レコード
api.fluentedge.ai    CNAME    fluentedge-production-backend.azurecontainerapps.io
app.fluentedge.ai    CNAME    fluentedge-production-frontend.azurecontainerapps.io

# または A レコード + TXT (検証用)
# TXT レコードは az コマンドの出力に従って設定
```

#### ステップ 2: カスタムドメインのバインド

```bash
# バックエンド
az containerapp hostname add \
  --name fluentedge-production-backend \
  --resource-group rg-fluentedge-production \
  --hostname api.fluentedge.ai

# フロントエンド
az containerapp hostname add \
  --name fluentedge-production-frontend \
  --resource-group rg-fluentedge-production \
  --hostname app.fluentedge.ai
```

#### ステップ 3: マネージド SSL 証明書のバインド

```bash
# バックエンド
az containerapp hostname bind \
  --name fluentedge-production-backend \
  --resource-group rg-fluentedge-production \
  --hostname api.fluentedge.ai \
  --environment fluentedge-production-cae \
  --validation-method CNAME

# フロントエンド
az containerapp hostname bind \
  --name fluentedge-production-frontend \
  --resource-group rg-fluentedge-production \
  --hostname app.fluentedge.ai \
  --environment fluentedge-production-cae \
  --validation-method CNAME
```

> Azure Container Apps のマネージド証明書は自動更新されるため、手動での更新は不要です。

---

## モニタリングとログ

### Azure Monitor の有効化

Container Apps Environment を作成すると、Log Analytics ワークスペースが自動的に関連付けられます。

### Container Apps のログ確認

```bash
# リアルタイムログ
az containerapp logs show \
  --name fluentedge-dev-backend \
  --resource-group rg-fluentedge-dev \
  --follow

# 直近 100 行のログ
az containerapp logs show \
  --name fluentedge-dev-backend \
  --resource-group rg-fluentedge-dev \
  --tail 100
```

### Log Analytics クエリ (KQL)

```bash
# Log Analytics ワークスペースでの KQL クエリ例
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "
    ContainerAppConsoleLogs_CL
    | where ContainerName_s == 'fluentedge-backend'
    | where TimeGenerated > ago(1h)
    | order by TimeGenerated desc
    | take 50
  "
```

### 主要な KQL クエリ

#### エラーログの確認

```kql
ContainerAppConsoleLogs_CL
| where ContainerName_s == "fluentedge-backend"
| where Log_s contains "ERROR" or Log_s contains "Exception"
| order by TimeGenerated desc
| take 100
```

#### API レスポンスタイムの分析

```kql
ContainerAppConsoleLogs_CL
| where ContainerName_s == "fluentedge-backend"
| where Log_s contains "HTTP"
| parse Log_s with * "\"" Method " " Path " HTTP/" * "\" " StatusCode " " * " " ResponseTime "ms"
| summarize avg(todouble(ResponseTime)), percentile(todouble(ResponseTime), 95), count()
    by Path
| order by count_ desc
```

### アラートの設定

#### 推奨アラートルール

| メトリクス | 閾値 | 重要度 | 説明 |
| --- | --- | --- | --- |
| CPU 使用率 | > 80% (5 分間) | Warning | コンテナの CPU 逼迫 |
| メモリ使用率 | > 85% (5 分間) | Warning | コンテナのメモリ逼迫 |
| HTTP 5xx エラー率 | > 1% (5 分間) | Critical | サーバーエラーの多発 |
| レスポンスタイム (P95) | > 3000ms (5 分間) | Warning | レスポンス遅延 |
| PostgreSQL CPU | > 80% (5 分間) | Warning | DB の CPU 逼迫 |
| PostgreSQL ストレージ | > 85% | Critical | DB のストレージ逼迫 |
| Redis メモリ使用率 | > 80% | Warning | キャッシュのメモリ逼迫 |

### PostgreSQL のモニタリング

```bash
# サーバーの状態確認
az postgres flexible-server show \
  --name fluentedge-dev-pg \
  --resource-group rg-fluentedge-dev \
  --query "state"

# メトリクスの確認
az monitor metrics list \
  --resource "/subscriptions/<sub-id>/resourceGroups/rg-fluentedge-dev/providers/Microsoft.DBforPostgreSQL/flexibleServers/fluentedge-dev-pg" \
  --metric "cpu_percent" \
  --interval PT5M
```

---

## スケーリング設定

### Container Apps オートスケーリング

Bicep テンプレートで設定される環境別のスケーリングパラメータ:

| パラメータ | dev | staging | production |
| --- | --- | --- | --- |
| **Container CPU** | 0.5 vCPU | 1.0 vCPU | 2.0 vCPU |
| **Container Memory** | 1.0 GiB | 2.0 GiB | 4.0 GiB |
| **最小レプリカ** | 0 | 1 | 2 |
| **最大レプリカ** | 3 | 5 | 20 |
| **ゼロスケール** | 有効 | 無効 | 無効 |

### 手動スケーリング

一時的な負荷増加への対応:

```bash
# レプリカ数を手動で調整
az containerapp update \
  --name fluentedge-production-backend \
  --resource-group rg-fluentedge-production \
  --min-replicas 5 \
  --max-replicas 30
```

### PostgreSQL のスケーリング

```bash
# SKU のスケールアップ (ダウンタイムあり)
az postgres flexible-server update \
  --name fluentedge-production-pg \
  --resource-group rg-fluentedge-production \
  --sku-name Standard_D8s_v3

# ストレージの拡張 (ダウンタイムなし)
az postgres flexible-server update \
  --name fluentedge-production-pg \
  --resource-group rg-fluentedge-production \
  --storage-size 512
```

### PostgreSQL の環境別 SKU

| 設定 | dev | staging | production |
| --- | --- | --- | --- |
| **SKU** | Standard_B2ms | Standard_D2s_v3 | Standard_D4s_v3 |
| **Tier** | Burstable | GeneralPurpose | GeneralPurpose |
| **ストレージ** | 32 GB | 64 GB | 256 GB |
| **HA** | 無効 | 無効 | ゾーン冗長 |

### Redis の環境別設定

| 設定 | dev | staging | production |
| --- | --- | --- | --- |
| **SKU** | Basic | Standard | Standard |
| **容量** | 0 (250 MB) | 1 (1 GB) | 2 (6 GB) |

---

## CI/CD 統合の概要

### GitHub Actions (推奨)

以下のワークフローを `.github/workflows/` に追加することで CI/CD を実現できます。

#### 推奨ワークフロー構成

```text
.github/workflows/
├── ci.yml              # テスト + Lint (PR 時)
├── deploy-dev.yml      # dev 環境へのデプロイ (main マージ時)
├── deploy-staging.yml  # staging へのデプロイ (手動トリガー)
└── deploy-prod.yml     # production へのデプロイ (手動トリガー + 承認)
```

#### CI ワークフローの概要

```text
1. コードのチェックアウト
2. Python / Node.js のセットアップ
3. 依存パッケージのインストール
4. バックエンドのテスト (pytest)
5. フロントエンドの Lint + ビルド (npm run lint && npm run build)
6. Docker イメージのビルドテスト
```

#### CD ワークフローの概要

```text
1. コードのチェックアウト
2. Azure CLI へのログイン (サービスプリンシパル)
3. Docker イメージのビルド
4. ACR へのプッシュ
5. Container Apps の更新
6. ヘルスチェックの確認
7. (本番のみ) Slack/Teams 通知
```

#### 必要な GitHub Secrets

| シークレット名 | 説明 |
| --- | --- |
| `AZURE_CREDENTIALS` | Azure サービスプリンシパルの JSON |
| `ACR_LOGIN_SERVER` | ACR のログインサーバー名 |
| `ACR_USERNAME` | ACR のユーザー名 |
| `ACR_PASSWORD` | ACR のパスワード |

#### サービスプリンシパルの作成

```bash
az ad sp create-for-rbac \
  --name "github-actions-fluentedge" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/rg-fluentedge-dev \
  --json-auth
```

### Azure DevOps (代替)

Azure DevOps Pipelines を使用する場合は、Bicep テンプレートのデプロイと Container Apps の更新を組み合わせたパイプラインを構成します。

---

## コスト見積もり (環境別)

### 月間コスト概算

| リソース | dev | staging | production (100 ユーザー) |
| --- | --- | --- | --- |
| **Container Apps** | 約 $15 | 約 $50 | 約 $200 |
| **PostgreSQL Flexible Server** | 約 $30 | 約 $100 | 約 $400 |
| **Azure Cache for Redis** | 約 $0 (Basic) | 約 $50 | 約 $100 |
| **Azure Container Registry** | 約 $5 (Basic) | 約 $5 | 約 $20 (Standard) |
| **Key Vault** | 約 $1 | 約 $1 | 約 $1 |
| **Claude API (Azure AI Foundry)** | 約 $10 | 約 $50 | 約 $500〜2,000 |
| **Log Analytics** | 約 $5 | 約 $10 | 約 $30 |
| **合計** | **約 $66** | **約 $266** | **約 $1,251〜2,751** |

> Claude API のコストはユーザーの利用頻度に大きく依存します。上記は 100 ユーザーが平均的に利用した場合の見積もりです。

### コスト最適化のポイント

| 施策 | 対象 | 効果 |
| --- | --- | --- |
| dev 環境のゼロスケール | Container Apps | 未使用時の課金を削減 |
| Burstable SKU の活用 | PostgreSQL (dev) | 低コストで十分な性能 |
| Claude Haiku の活用 | API コスト | Sonnet の約 1/10 のコスト |
| 会話履歴の圧縮 | API コスト | 送信トークン数を削減 |
| Redis キャッシュ活用 | 全体 | DB クエリと API 呼び出しの削減 |
| 予約インスタンス | PostgreSQL (prod) | 1年/3年予約で最大 40% 割引 |
| 不要リソースの停止 | dev/staging | 夜間・週末の自動停止 |

### コストアラートの設定

```bash
# 月間予算アラートの設定
az consumption budget create \
  --budget-name fluentedge-monthly \
  --amount 300 \
  --category Cost \
  --resource-group rg-fluentedge-dev \
  --time-grain Monthly \
  --start-date 2026-02-01 \
  --end-date 2027-01-31
```

---

## デプロイチェックリスト

### 本番デプロイ前の確認事項

- [ ] Bicep テンプレートのデプロイが成功していること
- [ ] Key Vault に全シークレットが設定されていること
- [ ] Docker イメージが ACR にプッシュされていること
- [ ] Container Apps が正常に起動していること
- [ ] ヘルスチェック (`/health`) が正常に応答すること
- [ ] データベースマイグレーションが完了していること
- [ ] CORS 設定が本番ドメインに対応していること
- [ ] JWT シークレットが十分な長さのランダム文字列であること
- [ ] SSL 証明書が正常にバインドされていること
- [ ] アラートルールが設定されていること
- [ ] バックアップが正常に動作していること
- [ ] ロールバック手順が確認されていること

---

関連ドキュメント:

- [セットアップガイド](setup-guide.md) -- ローカル開発環境の構築
- [運用マニュアル](operation-manual.md) -- 機能の使い方と管理操作
- [API リファレンス](api-reference.md) -- 全エンドポイントの仕様
