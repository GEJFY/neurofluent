#!/usr/bin/env bash
# =============================================================================
# FluentEdge AI - Azure 初期セットアップスクリプト
# リソースグループ、ACR、Key Vault、サービスプリンシパルの作成
# Usage: ./scripts/setup-azure.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# 設定（必要に応じて変更）
# ---------------------------------------------------------------------------
PROJECT_NAME="${PROJECT_NAME:-fluentedge}"
LOCATION="${AZURE_LOCATION:-japaneast}"
RESOURCE_GROUP="${PROJECT_NAME}-rg"
ACR_NAME="${PROJECT_NAME}acr"
KEYVAULT_NAME="${PROJECT_NAME}-kv"
SP_NAME="${PROJECT_NAME}-github-sp"
SUBSCRIPTION_ID=""

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# ---------------------------------------------------------------------------
# 前提条件チェック
# ---------------------------------------------------------------------------
echo "============================================================"
echo -e "${BLUE} FluentEdge AI - Azure 初期セットアップ${NC}"
echo "============================================================"
echo ""

log_info "前提条件を確認中..."

if ! command -v az &> /dev/null; then
    log_error "Azure CLI がインストールされていません"
    log_error "https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

if ! az account show &> /dev/null; then
    log_error "Azure にログインしてください: az login"
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
ACCOUNT_NAME=$(az account show --query user.name -o tsv)

log_ok "Azure CLI 確認完了"
log_info "Subscription: ${SUBSCRIPTION_ID}"
log_info "Account: ${ACCOUNT_NAME}"
echo ""

# 確認プロンプト
echo "以下のリソースを作成します:"
echo "  - Resource Group:     ${RESOURCE_GROUP} (${LOCATION})"
echo "  - Container Registry: ${ACR_NAME}"
echo "  - Key Vault:          ${KEYVAULT_NAME}"
echo "  - Service Principal:  ${SP_NAME}"
echo ""
read -rp "続行しますか? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    log_info "セットアップをキャンセルしました"
    exit 0
fi
echo ""

# ---------------------------------------------------------------------------
# Step 1: リソースグループの作成
# ---------------------------------------------------------------------------
log_info "=== Step 1: リソースグループの作成 ==="

if az group show --name "${RESOURCE_GROUP}" &> /dev/null; then
    log_warn "リソースグループ ${RESOURCE_GROUP} は既に存在します"
else
    az group create \
        --name "${RESOURCE_GROUP}" \
        --location "${LOCATION}" \
        --tags project="${PROJECT_NAME}" managed-by="cli"

    log_ok "リソースグループ作成完了: ${RESOURCE_GROUP}"
fi
echo ""

# ---------------------------------------------------------------------------
# Step 2: Azure Container Registry (ACR) の作成
# ---------------------------------------------------------------------------
log_info "=== Step 2: Azure Container Registry の作成 ==="

if az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" &> /dev/null; then
    log_warn "ACR ${ACR_NAME} は既に存在します"
else
    az acr create \
        --name "${ACR_NAME}" \
        --resource-group "${RESOURCE_GROUP}" \
        --sku Basic \
        --admin-enabled true \
        --location "${LOCATION}" \
        --tags project="${PROJECT_NAME}"

    log_ok "ACR 作成完了: ${ACR_NAME}"
fi

# ACR認証情報の取得
ACR_LOGIN_SERVER=$(az acr show --name "${ACR_NAME}" --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name "${ACR_NAME}" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "${ACR_NAME}" --query "passwords[0].value" -o tsv)

log_ok "ACR ログインサーバー: ${ACR_LOGIN_SERVER}"
echo ""

# ---------------------------------------------------------------------------
# Step 3: Key Vault の作成
# ---------------------------------------------------------------------------
log_info "=== Step 3: Azure Key Vault の作成 ==="

if az keyvault show --name "${KEYVAULT_NAME}" --resource-group "${RESOURCE_GROUP}" &> /dev/null; then
    log_warn "Key Vault ${KEYVAULT_NAME} は既に存在します"
else
    az keyvault create \
        --name "${KEYVAULT_NAME}" \
        --resource-group "${RESOURCE_GROUP}" \
        --location "${LOCATION}" \
        --enable-rbac-authorization true \
        --tags project="${PROJECT_NAME}"

    log_ok "Key Vault 作成完了: ${KEYVAULT_NAME}"
fi
echo ""

# ---------------------------------------------------------------------------
# Step 4: サービスプリンシパルの作成 (CI/CD用)
# ---------------------------------------------------------------------------
log_info "=== Step 4: サービスプリンシパルの作成 ==="

SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "${SP_NAME}" \
    --role Contributor \
    --scopes "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}" \
    --sdk-auth 2>/dev/null || true)

if [[ -z "$SP_OUTPUT" || "$SP_OUTPUT" == "null" ]]; then
    log_warn "サービスプリンシパルの作成に失敗、または既に存在します"
    log_warn "既存のSPを使用する場合は、手動でAZURE_CREDENTIALSを設定してください"
    SP_OUTPUT="(取得できませんでした - 手動で確認してください)"
else
    log_ok "サービスプリンシパル作成完了: ${SP_NAME}"
fi
echo ""

# ---------------------------------------------------------------------------
# Step 5: Key Vault にシークレットを保存
# ---------------------------------------------------------------------------
log_info "=== Step 5: Key Vault にシークレットを保存 ==="

# 初期シークレットの設定
SECRETS=(
    "database-url=postgresql+asyncpg://fluentedge:CHANGE_ME@postgres:5432/fluentedge"
    "redis-url=redis://redis:6379/0"
    "secret-key=$(openssl rand -hex 32 2>/dev/null || python3 -c 'import secrets; print(secrets.token_hex(32))')"
)

for secret in "${SECRETS[@]}"; do
    KEY="${secret%%=*}"
    VALUE="${secret#*=}"
    az keyvault secret set \
        --vault-name "${KEYVAULT_NAME}" \
        --name "${KEY}" \
        --value "${VALUE}" \
        --output none 2>/dev/null || log_warn "シークレット ${KEY} の設定に失敗（権限を確認してください）"
done

log_ok "Key Vault シークレット設定完了"
echo ""

# ---------------------------------------------------------------------------
# GitHub Secrets 設定ガイド出力
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo -e "${GREEN} セットアップ完了${NC}"
echo "============================================================"
echo ""
echo "以下の値を GitHub リポジトリの Settings > Secrets に設定してください:"
echo ""
echo "------------------------------------------------------------"
echo "Secret Name              | Value"
echo "------------------------------------------------------------"
echo "AZURE_CREDENTIALS        | (下記JSON参照)"
echo "ACR_LOGIN_SERVER         | ${ACR_LOGIN_SERVER}"
echo "ACR_USERNAME             | ${ACR_USERNAME}"
echo "ACR_PASSWORD             | ${ACR_PASSWORD}"
echo "AZURE_RESOURCE_GROUP     | ${RESOURCE_GROUP}"
echo "------------------------------------------------------------"
echo ""
echo "AZURE_CREDENTIALS の値 (JSON):"
echo "------------------------------------------------------------"
if [[ "$SP_OUTPUT" != "(取得できませんでした"* ]]; then
    echo "$SP_OUTPUT"
else
    echo "(サービスプリンシパルを手動で作成し、JSON出力を設定してください)"
fi
echo "------------------------------------------------------------"
echo ""
echo "GitHub Environment の設定:"
echo "  1. Settings > Environments > 'staging' を作成"
echo "  2. Settings > Environments > 'production' を作成"
echo "     - Required reviewers を有効化（本番デプロイ承認用）"
echo ""
echo "Environment Variables (各環境ごと):"
echo "  NEXT_PUBLIC_API_URL = https://api-<env>.fluentedge.com"
echo ""
log_warn "ACR_PASSWORD は安全に保管してください"
log_warn "Key Vault のシークレット (database-url) のパスワードを変更してください"
echo "============================================================"
