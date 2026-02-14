# セットアップガイド

FluentEdge AI のローカル開発環境を構築するための手順書です。

---

## 目次

1. [前提条件](#前提条件)
2. [リポジトリのクローン](#リポジトリのクローン)
3. [環境変数の設定](#環境変数の設定)
4. [データベース・キャッシュの起動 (Docker Compose)](#データベースキャッシュの起動-docker-compose)
5. [データベースマイグレーション (Alembic)](#データベースマイグレーション-alembic)
6. [Azure AI Foundry API キーの取得・設定](#azure-ai-foundry-api-キーの取得設定)
7. [バックエンドの起動と確認](#バックエンドの起動と確認)
8. [フロントエンドの起動と確認](#フロントエンドの起動と確認)
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
| Azure CLI | 最新版 (任意) | `az --version` | [learn.microsoft.com](https://learn.microsoft.com/cli/azure/) |

### バージョン確認の実行例

```bash
python --version    # Python 3.11.x
node --version      # v20.x.x
npm --version       # 10.x.x
docker --version    # Docker version 27.x.x
docker compose version  # Docker Compose version v2.x.x
git --version       # git version 2.x.x
```

> **Windows ユーザーへの注意**: Docker Desktop for Windows を使用し、WSL2 バックエンドを有効にすることを推奨します。

---

## リポジトリのクローン

```bash
git clone <repository-url>
cd neurofluent
```

---

## 環境変数の設定

### 手順 1: テンプレートをコピー

```bash
cp .env.example .env
```

### 手順 2: `.env` ファイルを編集

`.env` ファイルを開き、以下の値を設定します。

```ini
# ===========================================
# FluentEdge - 環境変数
# ===========================================

# --- Claude (Azure AI Foundry Marketplace) --- [必須]
AZURE_AI_FOUNDRY_ENDPOINT=https://<your-endpoint>.services.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=<your-api-key>
CLAUDE_SONNET_MODEL=claude-sonnet-4-5-20250929
CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001

# --- Azure OpenAI --- [任意: 将来の音声機能用]
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime
AZURE_OPENAI_TTS_DEPLOYMENT=gpt-4o-mini-tts

# --- Azure Speech Services --- [任意: 将来の発音評価用]
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=eastus2

# --- Database --- [Docker Compose デフォルトに合わせる]
DATABASE_URL=postgresql+asyncpg://fluentedge:fluentedge@localhost:5432/fluentedge
DATABASE_URL_SYNC=postgresql://fluentedge:fluentedge@localhost:5432/fluentedge

# --- Redis ---
REDIS_URL=redis://localhost:6379/0

# --- Auth (JWT) ---
# 開発時は任意の文字列で OK。本番では必ず十分な長さのランダム文字列を使用
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# --- Application ---
ENVIRONMENT=dev
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=http://localhost:3000
```

### 必須・任意の区分

| 変数名 | 必須 | 説明 |
| --- | --- | --- |
| `AZURE_AI_FOUNDRY_ENDPOINT` | Yes | Claude API エンドポイント |
| `AZURE_AI_FOUNDRY_API_KEY` | Yes | Claude API キー |
| `CLAUDE_SONNET_MODEL` | Yes | 会話・フィードバック生成用モデル |
| `CLAUDE_HAIKU_MODEL` | Yes | 評価・スコアリング用モデル |
| `DATABASE_URL` | Yes | PostgreSQL 接続文字列 (async) |
| `DATABASE_URL_SYNC` | Yes | PostgreSQL 接続文字列 (sync, Alembic 用) |
| `REDIS_URL` | Yes | Redis 接続文字列 |
| `JWT_SECRET_KEY` | Yes | JWT 署名キー |
| `AZURE_OPENAI_ENDPOINT` | No | 将来の音声機能用 |
| `AZURE_SPEECH_KEY` | No | 将来の発音評価用 |

> **セキュリティ警告**: `.env` ファイルは `.gitignore` に含まれています。絶対に Git にコミットしないでください。

---

## データベース・キャッシュの起動 (Docker Compose)

`docker-compose.yml` により、PostgreSQL 16 (pgvector 拡張) と Redis 7 をローカルで起動します。

### 起動

```bash
docker compose up -d
```

### 起動状態の確認

```bash
docker compose ps
```

期待される出力:

```
NAME                   STATUS          PORTS
fluentedge-postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
fluentedge-redis       Up (healthy)    0.0.0.0:6379->6379/tcp
```

### 接続テスト

```bash
# PostgreSQL の接続テスト
docker compose exec postgres pg_isready -U fluentedge
# 期待出力: /var/run/postgresql:5432 - accepting connections

# Redis の接続テスト
docker compose exec redis redis-cli ping
# 期待出力: PONG
```

### 停止・削除

```bash
# コンテナの停止
docker compose down

# データも含めて完全削除 (ボリューム削除)
docker compose down -v
```

---

## データベースマイグレーション (Alembic)

### 手順 1: バックエンドの仮想環境を作成

```bash
cd backend

# 仮想環境を作成
python -m venv venv

# 有効化 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 有効化 (Windows Command Prompt)
venv\Scripts\activate.bat

# 有効化 (macOS / Linux)
source venv/bin/activate
```

> **OneDrive 環境の注意**: OneDrive 同期フォルダ内で `venv` を作成する場合、一時的に同期を停止することを推奨します。大量の小さなファイルが生成され、同期負荷が高くなるためです。

### 手順 2: 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

インストールされる主要パッケージ:

| パッケージ | バージョン | 用途 |
| --- | --- | --- |
| `fastapi` | 0.115.6 | Web フレームワーク |
| `uvicorn[standard]` | 0.34.0 | ASGI サーバー |
| `sqlalchemy[asyncio]` | 2.0.36 | ORM (非同期対応) |
| `asyncpg` | 0.30.0 | PostgreSQL 非同期ドライバ |
| `psycopg2-binary` | 2.9.10 | PostgreSQL 同期ドライバ (Alembic 用) |
| `alembic` | 1.14.1 | データベースマイグレーション |
| `redis` | 5.2.1 | Redis クライアント |
| `httpx` | 0.28.1 | HTTP クライアント (Claude API 呼び出し) |
| `python-jose[cryptography]` | 3.3.0 | JWT トークン処理 |
| `passlib[bcrypt]` | 1.7.4 | パスワードハッシュ化 |
| `pydantic-settings` | 2.7.1 | 環境変数バリデーション |
| `email-validator` | 2.1.1 | メールアドレスバリデーション |

### 手順 3: マイグレーションを実行

```bash
# テーブルの作成
alembic upgrade head
```

マイグレーションが正常に完了すると、以下のテーブルが作成されます:

- `users` -- ユーザー情報
- `conversation_sessions` -- 会話セッション
- `conversation_messages` -- 会話メッセージ
- `review_items` -- 復習アイテム (FSRS)
- `daily_stats` -- 日次統計
- `api_usage_logs` -- API 使用量ログ

> マイグレーションファイルが `backend/alembic/versions/` に存在しない場合は、初回マイグレーションを生成してから実行してください:
>
> ```bash
> alembic revision --autogenerate -m "initial tables"
> alembic upgrade head
> ```

### マイグレーション管理コマンド

```bash
# 現在のリビジョンを確認
alembic current

# マイグレーション履歴を表示
alembic history

# 新しいマイグレーションファイルを生成
alembic revision --autogenerate -m "add column xxx"

# マイグレーションを 1 つ戻す
alembic downgrade -1

# 全マイグレーションを取り消す
alembic downgrade base
```

---

## Azure AI Foundry API キーの取得・設定

FluentEdge AI は Claude Sonnet 4.5 / Haiku 4.5 を Azure AI Foundry Marketplace 経由で使用します。

### 手順 1: Azure ポータルにログイン

[Azure Portal](https://portal.azure.com/) にアクセスしてログインします。

### 手順 2: Azure AI Foundry リソースを作成

1. 「リソースの作成」から「Azure AI Foundry」を検索
2. 以下の設定でリソースを作成:
   - **リソースグループ**: 新規作成または既存を選択
   - **リージョン**: `East US 2` 推奨 (Claude モデルの可用性)
   - **名前**: 任意 (例: `fluentedge-ai-foundry`)

### 手順 3: Claude モデルをデプロイ

1. [Azure AI Foundry Studio](https://ai.azure.com) にアクセス
2. 「Model catalog」 → 「Anthropic」で検索
3. 以下の 2 つのモデルをデプロイ:
   - **Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`) -- 会話生成・フィードバック用
   - **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) -- 回答評価・スコアリング用
4. デプロイ完了後、**エンドポイント URL** と **API キー** をメモ

### 手順 4: `.env` に反映

```ini
AZURE_AI_FOUNDRY_ENDPOINT=https://<your-endpoint>.services.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=<取得した API キー>
CLAUDE_SONNET_MODEL=claude-sonnet-4-5-20250929
CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001
```

### 手順 5: 接続テスト

バックエンドが起動した状態で、会話セッションを開始して接続を確認します:

```bash
# ユーザー登録
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","name":"Test User"}'

# レスポンスの access_token を使って会話を開始
curl -X POST http://localhost:8000/api/talk/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <取得したトークン>" \
  -d '{"mode":"small_talk"}'
```

AI からの応答が返れば、Claude API の接続は正常です。

---

## バックエンドの起動と確認

### 起動

```bash
cd backend

# 仮想環境を有効化 (未実行の場合)
source venv/bin/activate    # Windows: venv\Scripts\activate

# 開発サーバー起動 (ホットリロード有効)
uvicorn app.main:app --reload --port 8000
```

起動成功時の出力:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/health
# 期待レスポンス: {"status":"healthy","service":"fluentedge-api"}

# ユーザー登録
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","name":"テストユーザー"}'
# 期待レスポンス: {"access_token":"eyJhbGci...","token_type":"bearer"}

# ログイン
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
# 期待レスポンス: {"access_token":"eyJhbGci...","token_type":"bearer"}

# ユーザー情報取得 (<TOKEN> は上記で取得したトークン)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

### API ドキュメント

ブラウザで以下の URL にアクセスすると、インタラクティブな API ドキュメントが利用できます:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## フロントエンドの起動と確認

### 起動

新しいターミナルウィンドウを開いて実行します:

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run dev
```

起動成功時の出力:

```
  ▲ Next.js 15.1.x
  - Local:        http://localhost:3000
  - Environments: .env
```

### 動作確認

1. ブラウザで http://localhost:3000 にアクセス
2. ログインページが表示されることを確認
3. バックエンドで登録したユーザーでログイン
4. ダッシュボードが表示されれば成功

### ビルド確認

```bash
# 本番ビルドが正常に完了するか確認
npm run build

# Lint チェック
npm run lint
```

---

## トラブルシューティング

### PostgreSQL に接続できない

**症状**: `Connection refused` エラー、`asyncpg.exceptions.ConnectionRefusedError`

**対策**:

1. Docker コンテナが起動しているか確認
   ```bash
   docker compose ps
   docker compose logs postgres
   ```

2. ポート 5432 が他プロセスに使われていないか確認
   ```bash
   # Windows PowerShell
   netstat -ano | findstr :5432

   # macOS / Linux
   lsof -i :5432
   ```

3. `.env` の `DATABASE_URL` が Docker Compose の設定と一致しているか確認
   ```ini
   DATABASE_URL=postgresql+asyncpg://fluentedge:fluentedge@localhost:5432/fluentedge
   ```

4. コンテナの再起動
   ```bash
   docker compose down && docker compose up -d
   ```

### `ModuleNotFoundError: No module named 'app'`

**症状**: `uvicorn` 起動時にモジュールが見つからない

**対策**:

1. `backend/` ディレクトリから実行していることを確認
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. 仮想環境が有効化されているか確認
   ```bash
   which python     # macOS / Linux
   where python     # Windows
   # venv 内の python パスが表示されること
   ```

3. 依存パッケージがインストール済みか確認
   ```bash
   pip list | grep fastapi
   ```

### Alembic マイグレーションエラー

**症状**: `alembic upgrade head` が失敗する

**対策**:

1. PostgreSQL が起動・接続可能であることを確認

2. `DATABASE_URL_SYNC` (非 async URL) が正しいか確認
   ```ini
   DATABASE_URL_SYNC=postgresql://fluentedge:fluentedge@localhost:5432/fluentedge
   ```

3. マイグレーションファイルの存在確認
   ```bash
   ls alembic/versions/
   ```

4. 初回の場合はマイグレーションを生成
   ```bash
   alembic revision --autogenerate -m "initial tables"
   alembic upgrade head
   ```

5. 既存マイグレーションとの競合がある場合
   ```bash
   alembic current    # 現在のリビジョンを確認
   alembic history    # 履歴を確認
   alembic downgrade -1  # 1 つ戻す
   ```

### CORS エラー

**症状**: ブラウザのコンソールに `Access-Control-Allow-Origin` エラー

**対策**:

1. `.env` の `BACKEND_CORS_ORIGINS` を確認
   ```ini
   BACKEND_CORS_ORIGINS=http://localhost:3000
   ```

2. フロントエンドのポートが 3000 であることを確認

3. 複数オリジンを許可する場合はカンマ区切り
   ```ini
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

### フロントエンドのビルドエラー

**症状**: `npm run dev` で型エラーが発生する

**対策**:

1. Node.js のバージョンを確認 (20 LTS 以上が必要)
   ```bash
   node --version
   ```

2. `node_modules` を再インストール
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### Claude API 呼び出しエラー

**症状**: 会話開始や瞬間英作文で AI 応答が返らない

**対策**:

1. `.env` の API キーとエンドポイントが正しいか確認
   ```ini
   AZURE_AI_FOUNDRY_ENDPOINT=https://<endpoint>.services.ai.azure.com/
   AZURE_AI_FOUNDRY_API_KEY=<your-key>
   ```

2. エンドポイント URL の末尾にスラッシュ `/` があるか確認

3. Azure AI Foundry Studio でモデルのデプロイ状態を確認

4. API キーの有効期限を確認

5. バックエンドのコンソールログで HTTP エラーコードを確認

### OneDrive 同期による問題

**症状**: `venv` 作成時にファイルロックエラー、同期の大幅な遅延

**対策**:

1. OneDrive の同期を一時停止してから `venv` を作成
   - タスクバーの OneDrive アイコンを右クリック
   - 「同期の一時停止」を選択
   - `python -m venv venv` を実行
   - 同期を再開

2. 代替手段: OneDrive 管理外のパスに `venv` を作成
   ```bash
   python -m venv C:\dev\fluentedge-venv
   C:\dev\fluentedge-venv\Scripts\activate
   ```

### Redis 接続エラー

**症状**: `ConnectionRefusedError` (Redis)

**対策**:

1. Redis コンテナが起動しているか確認
   ```bash
   docker compose logs redis
   ```

2. ポート 6379 の使用状況を確認

3. `.env` の `REDIS_URL` が正しいか確認
   ```ini
   REDIS_URL=redis://localhost:6379/0
   ```

### `pip install` でのビルドエラー (Windows)

**症状**: `psycopg2-binary` のインストール時にコンパイルエラー

**対策**:

```bash
pip install psycopg2-binary --only-binary :all:
```

### Windows 固有の注意点

- **パスの長さ制限**: Windows のパス長制限 (260 文字) に注意。OneDrive パスが長い場合、`npm install` が失敗することがあります。プロジェクトを短いパスに移動してください。

- **PowerShell 実行ポリシー**: `venv` をアクティベートできない場合:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **改行コード**: Git の `core.autocrlf` 設定を確認。Docker 内では LF が必要です。
  ```bash
  git config core.autocrlf input
  ```

---

全てのセットアップが完了したら、[運用マニュアル](operation-manual.md) で各機能の使い方を確認してください。
