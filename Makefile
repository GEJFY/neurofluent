# FluentEdge AI - 開発コマンド集
# ===================================

.PHONY: help setup dev dev-backend dev-frontend test lint docker-up docker-down docker-build migrate clean

help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === セットアップ ===

setup: ## 初回セットアップ（venv + npm install + docker）
	cd backend && python -m venv venv && venv/Scripts/pip install -r requirements-dev.txt
	cd frontend && npm install
	docker compose up -d postgres redis
	@echo "セットアップ完了。.env.example を .env にコピーして設定してください。"

setup-env: ## .env ファイルを .env.example から作成
	cp .env.example .env
	@echo ".env を作成しました。APIキーを設定してください。"

# === 開発サーバー ===

dev: ## バックエンド + フロントエンド 同時起動
	$(MAKE) docker-up
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## バックエンドのみ起動
	cd backend && venv/Scripts/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## フロントエンドのみ起動
	cd frontend && npm run dev

# === テスト ===

test: ## 全テスト実行
	cd backend && venv/Scripts/python -m pytest tests/ -v --tb=short

test-cov: ## カバレッジ付きテスト
	cd backend && venv/Scripts/python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch: ## テスト ウォッチモード
	cd backend && venv/Scripts/python -m pytest tests/ -v --tb=short -f

# === リント ===

lint: ## リントチェック（backend + frontend）
	cd backend && venv/Scripts/python -m ruff check app/ tests/
	cd frontend && npm run lint

lint-fix: ## リント自動修正
	cd backend && venv/Scripts/python -m ruff check --fix app/ tests/
	cd backend && venv/Scripts/python -m ruff format app/ tests/

# === データベース ===

migrate: ## Alembic マイグレーション実行
	cd backend && venv/Scripts/python -m alembic upgrade head

migrate-new: ## 新規マイグレーション作成 (MSG=メッセージ)
	cd backend && venv/Scripts/python -m alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## マイグレーション1つ戻す
	cd backend && venv/Scripts/python -m alembic downgrade -1

# === Docker ===

docker-up: ## Docker サービス起動（PostgreSQL + Redis）
	docker compose up -d postgres redis

docker-down: ## Docker サービス停止
	docker compose down

docker-build: ## 全Dockerイメージをビルド
	docker compose build

docker-all: ## フルスタック Docker 起動
	docker compose up -d --build

docker-logs: ## Docker ログ表示
	docker compose logs -f

# === クリーンアップ ===

clean: ## キャッシュ・一時ファイル削除
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/.next frontend/out
	rm -f test.db

clean-all: clean ## 全クリーンアップ（venv + node_modules 含む）
	rm -rf backend/venv
	rm -rf frontend/node_modules
