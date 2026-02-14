#!/usr/bin/env bash
# =============================================================================
# FluentEdge AI - 手動デプロイスクリプト
# Usage: ./scripts/deploy.sh --env <dev|staging|production>
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# デフォルト設定
# ---------------------------------------------------------------------------
ENVIRONMENT=""
ACR_NAME="${ACR_NAME:-fluentedgeacr}"
ACR_LOGIN_SERVER="${ACR_LOGIN_SERVER:-${ACR_NAME}.azurecr.io}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-fluentedge-rg}"
IMAGE_TAG=""
SKIP_INFRA=false
SKIP_MIGRATION=false
DRY_RUN=false

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---------------------------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------------------------
log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

FluentEdge AI デプロイスクリプト

Options:
  --env <dev|staging|production>  デプロイ先環境 (必須)
  --tag <tag>                     イメージタグ (デフォルト: git SHA)
  --skip-infra                    インフラデプロイをスキップ
  --skip-migration                DBマイグレーションをスキップ
  --dry-run                       実行内容の表示のみ
  -h, --help                      ヘルプ表示

Environment variables:
  ACR_NAME              ACR名 (default: fluentedgeacr)
  ACR_LOGIN_SERVER      ACRログインサーバー
  AZURE_RESOURCE_GROUP  リソースグループ名 (default: fluentedge-rg)

Examples:
  $(basename "$0") --env staging
  $(basename "$0") --env production --tag v1.2.0
  $(basename "$0") --env dev --skip-infra --skip-migration
EOF
    exit 0
}

# ---------------------------------------------------------------------------
# 引数パース
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --skip-infra)
            SKIP_INFRA=true
            shift
            ;;
        --skip-migration)
            SKIP_MIGRATION=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            ;;
    esac
done

# バリデーション
if [[ -z "$ENVIRONMENT" ]]; then
    log_error "--env は必須です (dev|staging|production)"
    usage
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
    log_error "無効な環境: $ENVIRONMENT (dev|staging|production を指定)"
    exit 1
fi

# イメージタグ設定
if [[ -z "$IMAGE_TAG" ]]; then
    IMAGE_TAG=$(git rev-parse --short HEAD 2>/dev/null || echo "latest")
fi

# ---------------------------------------------------------------------------
# 本番デプロイの確認
# ---------------------------------------------------------------------------
if [[ "$ENVIRONMENT" == "production" && "$DRY_RUN" == "false" ]]; then
    echo ""
    log_warn "本番環境へのデプロイを実行します"
    log_warn "Image tag: $IMAGE_TAG"
    echo ""
    read -rp "続行しますか? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        log_info "デプロイをキャンセルしました"
        exit 0
    fi
fi

# ---------------------------------------------------------------------------
# 前提条件チェック
# ---------------------------------------------------------------------------
log_info "前提条件を確認中..."

for cmd in docker az; do
    if ! command -v "$cmd" &> /dev/null; then
        log_error "$cmd がインストールされていません"
        exit 1
    fi
done

# Azure ログイン確認
if ! az account show &> /dev/null; then
    log_error "Azure にログインしてください: az login"
    exit 1
fi

log_ok "前提条件チェック完了"

# ---------------------------------------------------------------------------
# Step 1: Dockerイメージのビルド
# ---------------------------------------------------------------------------
echo ""
log_info "=== Step 1: Dockerイメージのビルド ==="

BACKEND_IMAGE="${ACR_LOGIN_SERVER}/fluentedge-backend:${IMAGE_TAG}"
FRONTEND_IMAGE="${ACR_LOGIN_SERVER}/fluentedge-frontend:${IMAGE_TAG}"

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY-RUN] docker build -t ${BACKEND_IMAGE} ./backend"
    log_info "[DRY-RUN] docker build -t ${FRONTEND_IMAGE} ./frontend"
else
    log_info "Backend イメージをビルド中..."
    docker build -t "${BACKEND_IMAGE}" \
        -t "${ACR_LOGIN_SERVER}/fluentedge-backend:latest" \
        ./backend

    log_info "Frontend イメージをビルド中..."
    docker build -t "${FRONTEND_IMAGE}" \
        -t "${ACR_LOGIN_SERVER}/fluentedge-frontend:latest" \
        --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-https://api.fluentedge.com}" \
        ./frontend

    log_ok "イメージビルド完了"
fi

# ---------------------------------------------------------------------------
# Step 2: ACRへプッシュ
# ---------------------------------------------------------------------------
echo ""
log_info "=== Step 2: ACRへイメージをプッシュ ==="

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY-RUN] az acr login --name ${ACR_NAME}"
    log_info "[DRY-RUN] docker push ${BACKEND_IMAGE}"
    log_info "[DRY-RUN] docker push ${FRONTEND_IMAGE}"
else
    log_info "ACR にログイン中..."
    az acr login --name "${ACR_NAME}"

    log_info "Backend イメージをプッシュ中..."
    docker push "${BACKEND_IMAGE}"
    docker push "${ACR_LOGIN_SERVER}/fluentedge-backend:latest"

    log_info "Frontend イメージをプッシュ中..."
    docker push "${FRONTEND_IMAGE}"
    docker push "${ACR_LOGIN_SERVER}/fluentedge-frontend:latest"

    log_ok "ACRへのプッシュ完了"
fi

# ---------------------------------------------------------------------------
# Step 3: インフラデプロイ (Bicep)
# ---------------------------------------------------------------------------
echo ""
if [[ "$SKIP_INFRA" == "true" ]]; then
    log_warn "=== Step 3: インフラデプロイ (スキップ) ==="
else
    log_info "=== Step 3: Bicepでインフラをデプロイ ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] az deployment group create --resource-group ${RESOURCE_GROUP} --template-file ./infra/main.bicep"
    else
        az deployment group create \
            --resource-group "${RESOURCE_GROUP}" \
            --template-file ./infra/main.bicep \
            --parameters \
                environment="${ENVIRONMENT}" \
                acrLoginServer="${ACR_LOGIN_SERVER}" \
                imageTag="${IMAGE_TAG}" \
            --verbose

        log_ok "インフラデプロイ完了"
    fi
fi

# ---------------------------------------------------------------------------
# Step 4: Container Appsを更新
# ---------------------------------------------------------------------------
echo ""
log_info "=== Step 4: Container Appsを更新 ==="

BACKEND_APP="fluentedge-backend-${ENVIRONMENT}"
FRONTEND_APP="fluentedge-frontend-${ENVIRONMENT}"

if [[ "$DRY_RUN" == "true" ]]; then
    log_info "[DRY-RUN] az containerapp update --name ${BACKEND_APP} --image ${BACKEND_IMAGE}"
    log_info "[DRY-RUN] az containerapp update --name ${FRONTEND_APP} --image ${FRONTEND_IMAGE}"
else
    log_info "Backend Container App を更新中..."
    az containerapp update \
        --name "${BACKEND_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --image "${BACKEND_IMAGE}"

    log_info "Frontend Container App を更新中..."
    az containerapp update \
        --name "${FRONTEND_APP}" \
        --resource-group "${RESOURCE_GROUP}" \
        --image "${FRONTEND_IMAGE}"

    log_ok "Container Apps 更新完了"
fi

# ---------------------------------------------------------------------------
# Step 5: DBマイグレーション
# ---------------------------------------------------------------------------
echo ""
if [[ "$SKIP_MIGRATION" == "true" ]]; then
    log_warn "=== Step 5: DBマイグレーション (スキップ) ==="
else
    log_info "=== Step 5: DBマイグレーション実行 ==="

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] az containerapp exec --name ${BACKEND_APP} --command 'alembic upgrade head'"
    else
        az containerapp exec \
            --name "${BACKEND_APP}" \
            --resource-group "${RESOURCE_GROUP}" \
            --command "alembic upgrade head"

        log_ok "マイグレーション完了"
    fi
fi

# ---------------------------------------------------------------------------
# デプロイサマリー
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo -e "${GREEN} FluentEdge AI デプロイ完了${NC}"
echo "============================================================"
echo ""
echo "  Environment:    ${ENVIRONMENT}"
echo "  Image Tag:      ${IMAGE_TAG}"
echo "  Backend Image:  ${BACKEND_IMAGE}"
echo "  Frontend Image: ${FRONTEND_IMAGE}"
echo "  Resource Group: ${RESOURCE_GROUP}"
echo "  Backend App:    ${BACKEND_APP}"
echo "  Frontend App:   ${FRONTEND_APP}"
echo "  Timestamp:      $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}  [DRY-RUN] 実際のデプロイは実行されていません${NC}"
    echo ""
fi

echo "============================================================"
