# FluentEdge AI セットアップガイド

FluentEdge AI のローカル開発環境を構築するための手順書です。
Docker Compose によるクイックスタートから、個別コンポーネントの詳細セットアップ、
マルチクラウド LLM プロバイダーの設定、テスト実行までを網羅しています。

---

## 目次

1. [前提条件](#前提条件)
2. [クイックスタート (Docker Compose)](#クイックスタート-docker-compose)
3. [バックエンド詳細セットアップ](#バックエンド詳細セットアップ)
4. [フロントエンド詳細セットアップ](#フロントエンド詳細セットアップ)
5. [LLM プロバイダー設定](#llm-プロバイダー設定)
6. [Stripe 決済設定](#stripe-決済設定)
7. [テスト実行](#テスト実行)
8. [環境変数一覧](#環境変数一覧)
9. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

以下のソフトウェアがインストールされていることを確認してください。

| ソフトウェア | 必須バージョン | 確認コマンド | インストール先 |
| --- | --- | --- | --- |
| Python | 3.11 以上 | `python --version` | [python.org](https://www.python.org/downloads/) |
| Node.js | 20 LTS 以上 | `node --version` | [nodejs.org](https://nodejs.org/) |
| npm | 10 以上 | `npm --version` | Node.js に同梱 |
| Docker Desktop | 最新版 | `docker --version` | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Docker Compose | v2 以上 | `docker compose version` | Docker Desktop に同梱 |
| Git | 最新版 | `git --version` | [git-scm.com](https://git-scm.com/) |

### バージョン確認コマンド

```bash
python --version          # Python 3.11.x
node --version            # v20.x.x
npm --version             # 10.x.x
docker --version          # Docker version 27.x.x
docker compose version    # Docker Compose version v2.x.x
git --version             # git version 2.x.x
```

> **Windows ユーザー**: Docker Desktop for Windows を使用し、WSL2 バックエンドを有効にすることを推奨します。

---

## クイックスタート (Docker Compose)

全サービスを Docker Compose で一括起動する最速のセットアップです。約 5 分で動作確認可能です。

### 手順 1: リポジトリのクローン

```bash
git clone <repository-url>
cd neurofluent
```

### 手順 2: 環境変数の設定

```bash
cp .env.example .env
```

`.env` を開き、最低限以下を設定します（LLM プロバイダーは後述の設定セクションを参照）:

```ini
# LLMプロバイダー（デフォルト: Azure AI Foundry）
LLM_PROVIDER=azure_foundry
AZURE_AI_FOUNDRY_ENDPOINT=https://<your-endpoint>.services.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=<your-api-key>

# JWT認証
JWT_SECRET_KEY=dev-secret-key-change-in-production
```

### 手順 3: 全サービスを起動

```bash
# DB + Redis のみ起動（バックエンドをローカル実行する場合）
docker compose --profile db up -d

# 全サービス一括起動（Backend + Frontend + DB + Redis）
docker compose --profile full up -d
```

### 手順 4: 動作確認

| サービス | URL |
| --- | --- |
| バックエンド API | http://localhost:8000/health |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| フロントエンド | http://localhost:3000 |

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"fluentedge-api"}
```

---

## バックエンド詳細セットアップ

Docker に頼らずバックエンドをローカルで直接実行する手順です。

### 手順 1: インフラの起動 (DB + Redis)

```bash
docker compose --profile db up -d
```

起動確認:

```bash
docker compose ps
# fluentedge-postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
# fluentedge-redis       Up (healthy)    0.0.0.0:6379->6379/tcp

# 接続テスト
docker compose exec postgres pg_isready -U fluentedge
docker compose exec redis redis-cli ping
```

### 手順 2: Python 仮想環境の作成

```bash
cd backend
python -m venv venv

# 有効化
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt:
venv\Scripts\activate.bat

# macOS / Linux:
source venv/bin/activate
```

> **OneDrive 環境の注意**: OneDrive 同期フォルダ内で venv を作成する場合、一時的に OneDrive の同期を停止してください。大量の小さなファイルが生成され同期負荷が高くなります。

### 手順 3: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

主要パッケージ一覧:

| パッケージ | バージョン | 用途 |
| --- | --- | --- |
| fastapi | 0.115.6 | Web フレームワーク |
| uvicorn[standard] | 0.34.0 | ASGI サーバー |
| sqlalchemy[asyncio] | 2.0.36 | ORM (非同期) |
| asyncpg | 0.30.0 | PostgreSQL 非同期ドライバ |
| alembic | 1.14.1 | DB マイグレーション |
| redis | 5.2.1 | Redis クライアント |
| httpx | 0.28.1 | HTTP クライアント |
| structlog | 24.4.0 | 構造化ログ |
| anthropic | 0.43.0 | Anthropic Direct API |
| boto3 | 1.35.0 | AWS Bedrock |
| google-cloud-aiplatform | 1.75.0 | GCP Vertex AI |
| stripe | 11.4.1 | Stripe 決済 |

### 手順 4: データベースマイグレーション

```bash
# マイグレーション実行
alembic upgrade head

# マイグレーションファイルが存在しない場合
alembic revision --autogenerate -m "initial tables"
alembic upgrade head
```

作成されるテーブル:
- `users` -- ユーザー情報
- `conversation_sessions` -- 会話セッション
- `conversation_messages` -- 会話メッセージ
- `review_items` -- 復習アイテム (FSRS)
- `daily_stats` -- 日次統計
- `api_usage_log` -- API 使用量ログ
- `pattern_mastery` -- パターン練習習熟度
- `sound_pattern_mastery` -- 音声パターン習熟度
- `subscriptions` -- サブスクリプション管理

### 手順 5: バックエンド起動

```bash
uvicorn app.main:app --reload --port 8000
```

起動成功時の出力:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Application startup complete.
```

### マイグレーション管理コマンド

```bash
alembic current                              # 現在のリビジョン
alembic history                              # 履歴一覧
alembic revision --autogenerate -m "説明"    # 新規マイグレーション生成
alembic upgrade head                         # 最新まで適用
alembic downgrade -1                         # 1つ戻す
```

---

## フロントエンド詳細セットアップ

### 手順 1: 依存パッケージのインストール

```bash
cd frontend
npm ci
```

### 手順 2: 開発サーバー起動

```bash
npm run dev
```

起動成功時の出力:

```
  Next.js 15.1.x
  - Local:        http://localhost:3000
```

### 手順 3: 動作確認

1. ブラウザで http://localhost:3000 にアクセス
2. ログインページが表示されることを確認
3. バックエンドで登録したユーザーでログイン
4. ダッシュボードが表示されれば成功

### ビルドとLint

```bash
npm run build          # 本番ビルド
npm run lint           # ESLint チェック
npm run test           # Vitest テスト実行
npm run test:coverage  # カバレッジ付きテスト
```

---

## LLM プロバイダー設定

FluentEdge AI はマルチクラウド LLM に対応しています。環境変数 `LLM_PROVIDER` でプライマリプロバイダーを切り替え、`LLM_FALLBACK_PROVIDERS` でフォールバック順序を指定します。

### 対応プロバイダー一覧

| プロバイダー | `LLM_PROVIDER` 値 | 必要な環境変数 |
| --- | --- | --- |
| Azure AI Foundry | `azure_foundry` | `AZURE_AI_FOUNDRY_ENDPOINT`, `AZURE_AI_FOUNDRY_API_KEY` |
| Anthropic Direct | `anthropic` | `ANTHROPIC_API_KEY` |
| AWS Bedrock | `bedrock` | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| GCP Vertex AI | `vertex` | `GCP_PROJECT_ID`, `GCP_REGION` |
| ローカル (Ollama) | `local` | `LOCAL_LLM_BASE_URL` |

### Azure AI Foundry (デフォルト)

1. [Azure Portal](https://portal.azure.com/) にログイン
2. Azure AI Foundry リソースを作成 (リージョン: `East US 2` 推奨)
3. [Azure AI Foundry Studio](https://ai.azure.com) で以下のモデルをデプロイ:
   - Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) -- 会話生成用
   - Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) -- 評価/スコアリング用
4. エンドポイント URL と API キーを `.env` に設定:

```ini
LLM_PROVIDER=azure_foundry
AZURE_AI_FOUNDRY_ENDPOINT=https://<your-endpoint>.services.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=<your-api-key>
CLAUDE_SONNET_MODEL=claude-sonnet-4-5-20250929
CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001
```

### Anthropic Direct API

1. [Anthropic Console](https://console.anthropic.com/) で API キーを取得
2. `.env` に設定:

```ini
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### AWS Bedrock

1. AWS コンソールで Bedrock の Claude モデルアクセスを有効化
2. IAM ユーザーまたはロールに `bedrock:InvokeModel` 権限を付与
3. `.env` に設定:

```ini
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_BEDROCK_MODEL_SONNET=anthropic.claude-sonnet-4-5-20250929-v1:0
AWS_BEDROCK_MODEL_HAIKU=anthropic.claude-haiku-4-5-20251001-v1:0
```

### GCP Vertex AI

1. GCP プロジェクトで Vertex AI API を有効化
2. Claude モデルへのアクセスをリクエスト
3. サービスアカウントキーまたは ADC (Application Default Credentials) を設定
4. `.env` に設定:

```ini
LLM_PROVIDER=vertex
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCP_VERTEX_MODEL_SONNET=claude-sonnet-4-5-20250929
GCP_VERTEX_MODEL_HAIKU=claude-haiku-4-5-20251001
```

### ローカル LLM (Ollama)

コスト無料でオフライン開発が可能です。

1. [Ollama](https://ollama.ai/) をインストール
2. モデルをダウンロード:

```bash
ollama pull llama3.1:8b
```

3. `.env` に設定:

```ini
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=ollama
LOCAL_MODEL_SMART=llama3.1:8b
LOCAL_MODEL_FAST=llama3.1:8b
```

> **注意**: ローカルモデルは Claude と比較して精度が低くなります。開発・テスト用途向けです。

### フォールバック設定

プライマリプロバイダーが失敗した場合、フォールバックプロバイダーに自動切替されます。

```ini
LLM_PROVIDER=azure_foundry
LLM_FALLBACK_PROVIDERS=anthropic,bedrock
```

### レジリエンス設定

```ini
LLM_CIRCUIT_BREAKER_THRESHOLD=5    # サーキットブレーカー: 連続失敗閾値
LLM_CIRCUIT_BREAKER_TIMEOUT=60.0   # サーキットブレーカー: 回復待機秒数
LLM_RETRY_MAX=3                    # リトライ最大回数
LLM_RATE_LIMIT_RPM=60              # レートリミット (リクエスト/分)
```

---

## Stripe 決済設定

サブスクリプション機能を利用する場合に設定します。

### 手順 1: Stripe アカウント作成

[Stripe Dashboard](https://dashboard.stripe.com/) でアカウントを作成します。

### 手順 2: API キーの取得

Stripe Dashboard > Developers > API keys から:
- Secret key (`sk_test_...`)
- Webhook signing secret (`whsec_...`)

### 手順 3: 料金プランの作成

Stripe Dashboard で Product + Price を作成し、Price ID を取得します。

### 手順 4: `.env` に設定

```ini
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
STRIPE_PRICE_STANDARD=price_xxxxxxxxxxxx
STRIPE_PRICE_PREMIUM=price_xxxxxxxxxxxx
```

### 手順 5: Webhook のローカルテスト

```bash
# Stripe CLI のインストール
# https://stripe.com/docs/stripe-cli

stripe listen --forward-to localhost:8000/api/subscription/webhook
```

---

## テスト実行

### バックエンドテスト (pytest)

```bash
cd backend
source venv/bin/activate

# 全テスト実行
pytest -v

# カバレッジ付き
pytest -v --cov=app --cov-report=term-missing

# 特定テスト実行
pytest tests/test_llm/ -v
pytest tests/test_routers/ -v
pytest tests/test_services/ -v
```

### フロントエンドテスト (Vitest)

```bash
cd frontend

# テスト実行
npm test

# 単発実行 (CI用)
npm run test:run

# カバレッジ付き
npm run test:coverage
```

### E2E テスト (Playwright)

```bash
cd frontend

# Playwright インストール
npx playwright install

# E2E テスト実行
npx playwright test

# UI モードで実行
npx playwright test --ui
```

---

## 環境変数一覧

| 変数名 | 必須 | デフォルト | 説明 |
| --- | --- | --- | --- |
| **アプリケーション** ||||
| `ENVIRONMENT` | No | `dev` | 実行環境 (dev/staging/production) |
| `LOG_LEVEL` | No | `INFO` | ログレベル (DEBUG/INFO/WARNING/ERROR) |
| `BACKEND_CORS_ORIGINS` | No | `http://localhost:3000` | CORS 許可オリジン (カンマ区切り) |
| **データベース** ||||
| `DATABASE_URL` | Yes | -- | PostgreSQL 接続文字列 (async) |
| `DATABASE_URL_SYNC` | Yes | -- | PostgreSQL 接続文字列 (sync, Alembic用) |
| `REDIS_URL` | Yes | -- | Redis 接続文字列 |
| **認証** ||||
| `JWT_SECRET_KEY` | Yes | -- | JWT 署名キー (本番では十分な長さのランダム文字列) |
| `JWT_ALGORITHM` | No | `HS256` | JWT アルゴリズム |
| `JWT_EXPIRY_HOURS` | No | `24` | JWT 有効期限 (時間) |
| **LLM プロバイダー** ||||
| `LLM_PROVIDER` | No | `azure_foundry` | プライマリプロバイダー |
| `LLM_FALLBACK_PROVIDERS` | No | -- | フォールバック (カンマ区切り) |
| `AZURE_AI_FOUNDRY_ENDPOINT` | 条件付 | -- | Azure AI Foundry エンドポイント |
| `AZURE_AI_FOUNDRY_API_KEY` | 条件付 | -- | Azure AI Foundry API キー |
| `CLAUDE_SONNET_MODEL` | No | `claude-sonnet-4-5-20250929` | Sonnet モデルID |
| `CLAUDE_HAIKU_MODEL` | No | `claude-haiku-4-5-20251001` | Haiku モデルID |
| `ANTHROPIC_API_KEY` | 条件付 | -- | Anthropic Direct API キー |
| `AWS_REGION` | 条件付 | `us-east-1` | AWS リージョン |
| `AWS_ACCESS_KEY_ID` | 条件付 | -- | AWS アクセスキー |
| `AWS_SECRET_ACCESS_KEY` | 条件付 | -- | AWS シークレットキー |
| `GCP_PROJECT_ID` | 条件付 | -- | GCP プロジェクトID |
| `GCP_REGION` | 条件付 | `us-central1` | GCP リージョン |
| `LOCAL_LLM_BASE_URL` | 条件付 | `http://localhost:11434/v1` | ローカルLLM URL |
| **LLM レジリエンス** ||||
| `LLM_CIRCUIT_BREAKER_THRESHOLD` | No | `5` | サーキットブレーカー閾値 |
| `LLM_CIRCUIT_BREAKER_TIMEOUT` | No | `60.0` | 回復タイムアウト (秒) |
| `LLM_RETRY_MAX` | No | `3` | リトライ最大回数 |
| `LLM_RATE_LIMIT_RPM` | No | `60` | レートリミット (RPM) |
| **Stripe** ||||
| `STRIPE_SECRET_KEY` | No | -- | Stripe シークレットキー |
| `STRIPE_WEBHOOK_SECRET` | No | -- | Webhook 署名シークレット |
| `STRIPE_PRICE_STANDARD` | No | -- | Standard プラン Price ID |
| `STRIPE_PRICE_PREMIUM` | No | -- | Premium プラン Price ID |
| **Azure Speech** ||||
| `AZURE_SPEECH_KEY` | No | -- | Azure Speech Services キー |
| `AZURE_SPEECH_REGION` | No | `eastus2` | Azure Speech リージョン |
| **Azure OpenAI** ||||
| `AZURE_OPENAI_ENDPOINT` | No | -- | Azure OpenAI エンドポイント |
| `AZURE_OPENAI_API_KEY` | No | -- | Azure OpenAI API キー |

> 「条件付」は、対応する `LLM_PROVIDER` を選択した場合に必須となる変数です。

---

## トラブルシューティング

### PostgreSQL に接続できない

**症状**: `Connection refused`、`asyncpg.exceptions.ConnectionRefusedError`

```bash
# 1. コンテナの状態確認
docker compose ps
docker compose logs postgres

# 2. ポート使用状況の確認
# Windows:
netstat -ano | findstr :5432
# macOS/Linux:
lsof -i :5432

# 3. .env の DATABASE_URL を確認
# DATABASE_URL=postgresql+asyncpg://fluentedge:fluentedge@localhost:5432/fluentedge

# 4. コンテナの再起動
docker compose down && docker compose --profile db up -d
```

### `ModuleNotFoundError: No module named 'app'`

```bash
# backend/ ディレクトリから実行していることを確認
cd backend
uvicorn app.main:app --reload --port 8000

# 仮想環境が有効化されているか確認
which python  # macOS/Linux
where python  # Windows
```

### Alembic マイグレーションエラー

```bash
# DATABASE_URL_SYNC が正しいか確認
# DATABASE_URL_SYNC=postgresql://fluentedge:fluentedge@localhost:5432/fluentedge

alembic current   # 現在のリビジョン確認
alembic history   # 履歴確認
```

### CORS エラー

`.env` の `BACKEND_CORS_ORIGINS` がフロントエンドのオリジンと一致しているか確認:

```ini
BACKEND_CORS_ORIGINS=http://localhost:3000
```

### LLM API 接続エラー

```bash
# 1. LLM_PROVIDER の値が正しいか確認
# 2. 対応する API キーが設定されているか確認
# 3. バックエンドログでエラー詳細を確認

# ローカル LLM でテスト
ollama serve
curl http://localhost:11434/v1/models
```

### OneDrive 同期による問題

1. OneDrive の同期を一時停止してから venv を作成
2. 代替: OneDrive 管理外のパスに venv を作成

```bash
python -m venv C:\dev\fluentedge-venv
C:\dev\fluentedge-venv\Scripts\activate
```

### Windows 固有の注意点

- **パス長制限**: Windows の 260 文字制限に注意。パスが長い場合は短いパスに移動
- **PowerShell 実行ポリシー**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **改行コード**: Docker 内では LF が必要
  ```bash
  git config core.autocrlf input
  ```

### pip install ビルドエラー (Windows)

```bash
pip install psycopg2-binary --only-binary :all:
```

---

全てのセットアップが完了したら、[運用マニュアル](operation-manual.md) で各機能の使い方を確認してください。
