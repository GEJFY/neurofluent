# FluentEdge AI

<!-- バッジプレースホルダー -->
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6)
![License](https://img.shields.io/badge/License-MIT-green)

> 脳科学に基づくAI英語トレーニングアプリケーション。マルチクラウドLLM対応（Azure AI Foundry / Anthropic / AWS Bedrock / GCP Vertex AI / ローカルOllama）で、Claude Opus 4.6 / Sonnet 4.5 / Haiku 4.5 による会話練習、瞬間英作文、発音分析、FSRS間隔反復など12機能を提供します。

---

## アーキテクチャ概要

```text
+-------------------------------------------------------------------+
|                          クライアント                                |
|   +-----------------------------------------------------------+   |
|   |  Next.js 15 / React 19 / TypeScript 5.7                   |   |
|   |  Tailwind CSS 4 + Zustand 5 (状態管理)                     |   |
|   +----------------------------+------------------------------+   |
+--------------------------------|----------------------------------+
                                 | REST API / WebSocket
                                 v
+-------------------------------------------------------------------+
|                          バックエンド                                |
|   +-----------------------------------------------------------+   |
|   |  FastAPI 0.115 / Python 3.11 / Uvicorn                    |   |
|   |                                                            |   |
|   |  +------------------+  +---------------+  +-----------+   |   |
|   |  | LLMRouter        |  | FSRS Engine   |  | Stripe    |   |   |
|   |  | (マルチクラウド)   |  | (間隔反復)    |  | (決済)    |   |   |
|   |  | CircuitBreaker   |  |               |  |           |   |   |
|   |  | RetryPolicy      |  |               |  |           |   |   |
|   |  | RateLimiter      |  |               |  |           |   |   |
|   |  +--------+---------+  +---------------+  +-----------+   |   |
|   +-----------|------------------------------------------------+   |
+---------------|---------------------------------------------------+
                |
     +----------+----------+
     |          |          |                    +------------------+
     v          v          v                    |  データストア     |
+---------+ +--------+ +--------+ +-------+    |                  |
|Azure AI | |Anthropic| |AWS     | |GCP    |    | PostgreSQL 16    |
|Foundry  | |Direct   | |Bedrock | |Vertex |    | + pgvector       |
+---------+ +--------+ +--------+ +-------+    |                  |
     |          |          |          |         | Redis 7          |
     v          v          v          v         | (キャッシュ)      |
  Claude Opus 4.6 / Sonnet 4.5 / Haiku 4.5                +------------------+
     (または Ollama ローカルLLM)
```

### マルチクラウドLLM対応

環境変数 `LLM_PROVIDER` でプライマリプロバイダーを切り替え、`LLM_FALLBACK_PROVIDERS` でフォールバックチェーンを構成できます。

| プロバイダー | 設定値 | 特徴 |
|-------------|-------|------|
| Azure AI Foundry | `azure_foundry` | デフォルト。Marketplace経由でClaude利用 |
| Anthropic Direct | `anthropic` | Anthropic APIを直接利用 |
| AWS Bedrock | `bedrock` | AWSインフラ統合、IAM認証 |
| GCP Vertex AI | `vertex` | GCPインフラ統合 |
| ローカル (Ollama) | `local` | コスト0、オフライン開発用 |

```bash
# 例: Anthropicをプライマリ、Bedrockをフォールバックに設定
LLM_PROVIDER=anthropic
LLM_FALLBACK_PROVIDERS=bedrock,azure_foundry
```

プロバイダー障害時はサーキットブレーカーが自動検知し、フォールバックプロバイダーに切り替えます。詳細は [アーキテクチャ設計書](docs/architecture.md) を参照してください。

---

## 技術スタック

| カテゴリ | 技術 | バージョン |
| --- | --- | --- |
| **フロントエンド** | Next.js / React / TypeScript | 15.1 / 19.0 / 5.7 |
| **UI** | Tailwind CSS / Lucide React | 4.0 / 0.468 |
| **状態管理** | Zustand | 5.0 |
| **バックエンド** | FastAPI / Uvicorn | 0.115.6 / 0.34.0 |
| **ORM** | SQLAlchemy (async) | 2.0.36 |
| **マイグレーション** | Alembic | 1.14.1 |
| **DB** | PostgreSQL + pgvector | 16 |
| **キャッシュ** | Redis | 7 (Alpine) |
| **LLM** | Claude Opus 4.6 / Sonnet 4.5 / Haiku 4.5 | マルチクラウド対応 |
| **LLMプロバイダー** | Azure AI Foundry / Anthropic / Bedrock / Vertex / Ollama | 切り替え可能 |
| **認証** | JWT (HS256) / Microsoft Entra ID | python-jose / passlib |
| **決済** | Stripe | 11.4.1 |
| **ログ** | structlog (JSON) | 24.4.0 |
| **IaC** | Terraform (マルチクラウド) | 1.5+ |
| **CI/CD** | GitHub Actions | ci / deploy / e2e |
| **コンテナ** | Docker / Docker Compose | プロファイル対応 |

---

## クイックスタート

### 前提条件

- **Python** 3.11+
- **Node.js** 20 LTS+
- **Docker Desktop** (Docker Compose v2+)
- **Azure AI Foundry API キー** (Claude アクセス用)

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd neurofluent
```

### 2. 環境変数を設定

```bash
cp .env.example .env
# .env を編集して API キーなどを設定
```

最低限必要な設定:

| 変数名 | 説明 | 必須 |
| --- | --- | --- |
| `LLM_PROVIDER` | LLMプロバイダー（azure_foundry / anthropic / bedrock / vertex / local） | Yes |
| `AZURE_AI_FOUNDRY_ENDPOINT` | Azure AI Foundry エンドポイント（azure_foundry使用時） | 条件付き |
| `AZURE_AI_FOUNDRY_API_KEY` | Azure AI Foundry API キー（azure_foundry使用時） | 条件付き |
| `ANTHROPIC_API_KEY` | Anthropic APIキー（anthropic使用時） | 条件付き |
| `JWT_SECRET_KEY` | JWT 署名キー（本番では必ず変更） | Yes |
| `DATABASE_URL` | PostgreSQL 接続文字列 (async) | Yes |
| `REDIS_URL` | Redis 接続文字列 | Yes |

> LLMプロバイダーは選択したものに対応するAPIキーのみ必要です。ローカルLLM（Ollama）使用時はAPIキー不要です。

### 3. Docker でインフラを起動

```bash
docker compose up -d
```

PostgreSQL 16 (pgvector) と Redis 7 が起動します。

### 4. バックエンドをセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# バックエンド起動
uvicorn app.main:app --reload --port 8000
```

### 5. フロントエンドをセットアップ

```bash
cd frontend
npm install
npm run dev
```

### 6. 動作確認

| サービス | URL |
| --- | --- |
| バックエンド API | `http://localhost:8000/health` |
| Swagger UI (API ドキュメント) | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| フロントエンド | `http://localhost:3000` |

詳細は [セットアップガイド](docs/setup-guide.md) を参照してください。

---

## ローカル LLM (Ollama) での利用

APIキーなしで開発・テストしたい場合、Ollama を使ってローカルLLMで動作させることができます。

### Ollama をインストール・起動

```bash
# Ollama インストール（公式サイト: https://ollama.com）
# モデルをダウンロード
ollama pull llama3.1:8b

# Ollama サーバーが起動していることを確認
ollama list
```

### Ollama 用の環境変数

```bash
# .env に以下を設定
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_API_KEY=ollama
LOCAL_MODEL_SMART=llama3.1:8b
LOCAL_MODEL_FAST=llama3.1:8b
```

### バックエンドを起動

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

> ローカルLLMはAPIコスト $0.00 で動作しますが、応答品質はクラウドのClaude Sonnet/Haikuに比べて劣る場合があります。開発・テスト用途に推奨です。

---

## テスト実行方法

### バックエンドテスト

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate

# リンティング（Ruff）
ruff check .

# ユニットテスト
pytest

# カバレッジ付きテスト
pytest --cov=app --cov-report=html
```

### フロントエンドテスト

```bash
cd frontend

# リンティング（ESLint）
npm run lint

# ユニットテスト（Vitest）
npm run test:run

# カバレッジ付きテスト
npm run test:coverage
```

### セキュリティスキャン

```bash
# Python依存関係の脆弱性チェック
pip-audit -r backend/requirements.txt

# Node.js依存関係の脆弱性チェック
cd frontend && npm audit
```

### CI/CDパイプライン

GitHub Actions で以下が自動実行されます:

| ワークフロー | トリガー | 内容 |
| --- | --- | --- |
| `ci.yml` | push / PR | Ruff + pytest + ESLint + Vitest + pip-audit + npm audit + Docker build + Trivy |
| `deploy.yml` | main push | ステージング/本番デプロイ |
| `e2e.yml` | main push | Playwright E2Eテスト |

---

## プロジェクト構成

```text
neurofluent/
├── .env.example                    # 環境変数テンプレート
├── docker-compose.yml              # PostgreSQL + Redis + 全サービス（プロファイル対応）
├── README.md                       # 本ファイル
│
├── backend/                        # FastAPI バックエンド
│   ├── Dockerfile                  # Python 3.11-slim ベースイメージ
│   ├── requirements.txt            # Python 依存パッケージ
│   ├── alembic.ini                 # Alembic 設定
│   ├── alembic/versions/           # マイグレーションファイル
│   ├── tests/                      # pytest テスト
│   └── app/
│       ├── main.py                 # FastAPI エントリポイント（14ルーター登録）
│       ├── config.py               # pydantic-settings 環境設定
│       ├── database.py             # SQLAlchemy async エンジン・セッション
│       ├── dependencies.py         # JWT 認証ディペンデンシー
│       ├── exceptions.py           # 統一例外階層（AppError）
│       ├── logging_config.py       # structlog 構造化ログ設定
│       ├── llm/                    # マルチクラウドLLM抽象化レイヤー
│       │   ├── base.py             #   LLMProvider 抽象基底クラス
│       │   ├── router.py           #   LLMRouter（フォールバック管理）
│       │   ├── resilience.py       #   CircuitBreaker / RetryPolicy / RateLimiter
│       │   ├── service.py          #   LLMService（シングルトン）
│       │   └── cost.py             #   プロバイダー別コスト計算
│       ├── middleware/             # ミドルウェア
│       │   ├── error_handler.py    #   統一エラーハンドラー
│       │   └── logging_middleware.py #  リクエストログ + X-Request-ID
│       ├── models/                 # SQLAlchemy モデル（9テーブル）
│       │   ├── user.py             #   ユーザー
│       │   ├── conversation.py     #   会話セッション / メッセージ
│       │   ├── review.py           #   復習アイテム (FSRS)
│       │   ├── stats.py            #   日次統計
│       │   ├── subscription.py     #   サブスクリプション
│       │   ├── api_usage.py        #   API 使用量追跡
│       │   ├── pattern.py          #   パターン習熟度
│       │   └── sound_pattern.py    #   音声パターン習熟度
│       ├── routers/                # API ルーター（13ルーター）
│       │   ├── health.py           #   /health
│       │   ├── auth.py             #   /api/auth/*
│       │   ├── talk.py             #   /api/talk/*
│       │   ├── speaking.py         #   /api/speaking/*
│       │   ├── review.py           #   /api/review/*
│       │   ├── analytics.py        #   /api/analytics/*
│       │   ├── listening.py        #   /api/listening/*
│       │   ├── pattern.py          #   /api/speaking/pattern/*
│       │   ├── realtime.py         #   /api/talk/realtime/* (WebSocket)
│       │   ├── mogomogo.py         #   /api/listening/mogomogo/*
│       │   ├── analytics_router.py #   /api/analytics/advanced/*
│       │   ├── subscription.py     #   /api/subscription/*
│       │   ├── pronunciation.py    #   /api/speaking/pronunciation/*
│       │   └── comprehension.py    #   /api/listening/comprehension/*
│       ├── services/               # ビジネスロジック
│       │   ├── claude_service.py   #   Claude API クライアント
│       │   └── spaced_repetition.py #  FSRS アルゴリズム実装（19パラメータ）
│       └── prompts/                # LLM プロンプトテンプレート
│
├── frontend/                       # Next.js フロントエンド
│   ├── package.json                # Next.js 15 / React 19 / Zustand 5
│   ├── Dockerfile                  # Node.js 20 ベースイメージ
│   ├── vitest.config.ts            # Vitest テスト設定
│   ├── __tests__/                  # フロントエンドテスト (16ファイル)
│   ├── app/                        # Next.js App Router ページ (16ページ)
│   ├── components/                 # UIコンポーネント (chat, drill, layout, subscription, ui)
│   └── lib/                        # API クライアント / Zustand ストア / hooks
│
├── infra/                          # IaC（Infrastructure as Code）
│   ├── bicep/                      # Azure Bicep テンプレート
│   └── terraform/                  # Terraform マルチクラウド
│       ├── main.tf                 #   Azure / AWS / GCP モジュール選択
│       ├── variables.tf            #   環境・クラウド変数
│       └── modules/                #   クラウド別モジュール
│
├── .github/workflows/              # CI/CD
│   ├── ci.yml                      # テスト・スキャン・ビルド
│   ├── deploy.yml                  # デプロイ
│   └── e2e.yml                     # E2Eテスト
│
└── docs/                           # ドキュメント
    ├── setup-guide.md              #   セットアップガイド
    ├── operation-manual.md         #   運用マニュアル
    ├── api-reference.md            #   API リファレンス
    ├── deployment-guide.md         #   デプロイメントガイド
    ├── user-manual.md              #   ユーザーマニュアル
    ├── architecture.md             #   アーキテクチャ設計書
    ├── maintenance-manual.md       #   メンテナンスマニュアル
    └── specification.md            #   技術仕様書
```

---

## API エンドポイント概要

約50エンドポイントを14ルーターで提供しています。

| カテゴリ | プレフィックス | 主要機能 | Phase |
| --- | --- | --- | --- |
| ヘルスチェック | `/health` | ヘルスチェック・レディネス | 1 |
| 認証 | `/api/auth` | 登録・ログイン・ユーザー情報 | 1 |
| AI英会話 | `/api/talk` | セッション管理・メッセージ送受信 | 1 |
| スピーキング | `/api/speaking` | 瞬間英作文・評価 | 1 |
| 復習 (FSRS) | `/api/review` | 復習アイテム・間隔反復 | 1 |
| 学習分析 | `/api/analytics` | ダッシュボード・日次/週次統計 | 1 |
| リスニング | `/api/listening` | ディクテーション・速度制御 | 2 |
| パターン練習 | `/api/speaking/pattern` | ビジネス英語パターンドリル | 2 |
| リアルタイム音声 | `/api/talk/realtime` | WebSocket音声会話 | 2 |
| もごもご英語 | `/api/listening/mogomogo` | 音声変化トレーニング | 3 |
| 高度分析 | `/api/analytics/advanced` | トレンド・レポート | 3 |
| サブスクリプション | `/api/subscription` | Stripe決済・プラン管理 | 3 |
| 発音分析 | `/api/speaking/pronunciation` | Azure Speech発音評価 | 4 |
| 聴解力テスト | `/api/listening/comprehension` | 聴解力測定 | 4 |

詳細は [API リファレンス](docs/api-reference.md) を参照してください。

---

## 開発コマンド一覧

### インフラ (Docker)

```bash
docker compose up -d          # PostgreSQL + Redis 起動
docker compose down            # 停止
docker compose down -v         # ボリューム含めて完全削除
docker compose ps              # コンテナ状態確認
docker compose logs -f postgres  # PostgreSQL ログ
docker compose logs -f redis     # Redis ログ
```

### バックエンド (Python / FastAPI)

```bash
cd backend

# 仮想環境
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 開発サーバー（ホットリロード）
uvicorn app.main:app --reload --port 8000

# Alembic マイグレーション
alembic revision --autogenerate -m "説明"   # 新規作成
alembic upgrade head                         # 適用
alembic downgrade -1                         # 1つ戻す
alembic history                              # 履歴確認
alembic current                              # 現在のリビジョン
```

### フロントエンド (Node.js / Next.js)

```bash
cd frontend

npm install        # 依存パッケージインストール
npm run dev        # 開発サーバー起動
npm run build      # 本番ビルド
npm run start      # 本番サーバー起動
npm run lint       # Lint チェック
```

---

## デプロイ

### Docker Compose（開発・ステージング）

```bash
# DB のみ起動（ローカル開発用）
docker compose --profile db up -d

# 全サービス起動（Backend + Frontend + DB）
docker compose --profile full up -d

# 監視付き（Prometheus + Grafana）
docker compose --profile full --profile monitoring up -d
```

### Terraform マルチクラウドデプロイ

`infra/terraform/` にマルチクラウド対応のTerraformモジュールを提供しています。
`cloud_provider` 変数で Azure / AWS / GCP を切り替え可能です。

```bash
cd infra/terraform

# 初期化
terraform init

# Azure にデプロイ
terraform plan -var="cloud_provider=azure" -var="environment=dev"
terraform apply -var="cloud_provider=azure" -var="environment=dev"

# AWS にデプロイ
terraform plan -var="cloud_provider=aws" -var="environment=dev"
terraform apply -var="cloud_provider=aws" -var="environment=dev"

# GCP にデプロイ
terraform plan -var="cloud_provider=gcp" -var="environment=dev"
terraform apply -var="cloud_provider=gcp" -var="environment=dev"
```

### プロビジョニングされるリソース

| クラウド | コンテナ | DB | キャッシュ | シークレット |
| --- | --- | --- | --- | --- |
| Azure | Container Apps | PostgreSQL Flexible Server | Cache for Redis | Key Vault |
| AWS | ECS Fargate | RDS PostgreSQL | ElastiCache | Secrets Manager |
| GCP | Cloud Run | Cloud SQL | Memorystore | Secret Manager |

詳細は [デプロイメントガイド](docs/deployment-guide.md) を参照してください。

---

## 全12機能

| Phase | # | 機能 | 説明 |
| --- | --- | --- | --- |
| **Phase 1** | 1 | AI Free Talk | Claude Opus 4.6 / Sonnet 4.5 とのテキスト英会話 + 文法・表現フィードバック |
| | 2 | 瞬間英作文 | 日本語 → 英語の即時翻訳ドリル + AI スコアリング |
| | 3 | FSRS 間隔反復 | 19パラメータの忘却曲線アルゴリズムで最適な復習タイミングを計算 |
| | 4 | ダッシュボード | ストリーク、累計統計、学習アクティビティ可視化 |
| **Phase 2** | 5 | リスニング練習 | ディクテーション、速度制御リスニング |
| | 6 | パターン練習 | ビジネス英語パターンのドリル（understood -> drilling -> acquired） |
| | 7 | リアルタイム音声 | WebSocketベースの音声会話（Azure OpenAI Realtime API） |
| **Phase 3** | 8 | もごもご英語 | リンキング・リダクション等の音声変化トレーニング |
| | 9 | 高度分析 | スキルレーダー、トレンド分析、週次/月次レポート |
| | 10 | サブスクリプション | Stripe決済による有料プラン（Standard / Premium） |
| **Phase 4** | 11 | 発音分析 | Azure Speechによる発音評価 + 音声パターン習熟度追跡 |
| | 12 | 聴解力テスト | 総合的な聴解力測定テスト |

---

## ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [セットアップガイド](docs/setup-guide.md) | ローカル開発環境の構築手順（全LLMプロバイダー対応） |
| [運用マニュアル](docs/operation-manual.md) | 12機能の使い方と管理者向け操作 |
| [API リファレンス](docs/api-reference.md) | 全50近いエンドポイントの詳細仕様 |
| [デプロイメントガイド](docs/deployment-guide.md) | Docker Compose / Terraform マルチクラウドデプロイ |
| [ユーザーマニュアル](docs/user-manual.md) | エンドユーザー向け全機能ガイド |
| [アーキテクチャ設計書](docs/architecture.md) | システム構成・LLM抽象化・データフロー |
| [メンテナンスマニュアル](docs/maintenance-manual.md) | 保守運用・障害対応・DR手順 |
| [技術仕様書](docs/specification.md) | DB設計・FSRS仕様・非機能要件 |

---

## コントリビューション

コントリビューションを歓迎します。以下の手順でお願いします。

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### コーディング規約

- **Python**: PEP 8 準拠、型ヒント必須
- **TypeScript**: ESLint + Next.js 推奨ルール
- **コメント・ドキュメント**: 日本語
- **コード（変数名・関数名）**: 英語

---

## ライセンス

MIT License

Copyright (c) 2025 FluentEdge AI

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

---

**FluentEdge AI** -- AI の力でビジネス英語を加速する
