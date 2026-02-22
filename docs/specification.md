# FluentEdge AI 技術仕様書

> バージョン: 1.0.0 | 最終更新: 2026-02-14 | ステータス: Phase 4 完了

---

## 目次

1. [バージョン情報](#1-バージョン情報)
2. [システム要件](#2-システム要件)
3. [技術スタック詳細](#3-技術スタック詳細)
4. [データベース設計](#4-データベース設計)
5. [API仕様概要](#5-api仕様概要)
6. [LLMプロバイダー仕様](#6-llmプロバイダー仕様)
7. [FSRSアルゴリズム仕様](#7-fsrsアルゴリズム仕様)
8. [フロントエンド仕様](#8-フロントエンド仕様)
9. [非機能要件](#9-非機能要件)

---

## 1. バージョン情報

### アプリケーションバージョン

| 項目 | バージョン | リリース日 |
|------|-----------|-----------|
| FluentEdge API | 1.0.0 | 2026-02-14 |
| FluentEdge Frontend | 0.1.0 | 2026-02-14 |
| DB Schema | v1 (Alembic管理) | 2026-02-14 |

### 開発フェーズ履歴

| フェーズ | 内容 | ステータス |
|---------|------|-----------|
| Phase 1 (MVP) | 認証・会話・スピーキング・復習・分析 | 完了 |
| Phase 2 | 音声統合（リスニング・パターン練習・リアルタイム音声） | 完了 |
| Phase 3 | 学習最適化（もごもご英語・高度分析・サブスクリプション） | 完了 |
| Phase 4 | 高度な機能（発音分析・聴解力テスト） | 完了 |
| Phase 5 | デスクトップレスポンシブ・音声UI改善・テスト拡充 | 完了 |

### セマンティックバージョニング方針

```
MAJOR.MINOR.PATCH
  |     |     |
  |     |     +-- バグ修正・セキュリティパッチ
  |     +-------- 機能追加（後方互換あり）
  +-------------- 破壊的変更（APIスキーマ変更等）
```

---

## 2. システム要件

### 開発環境

| 項目 | 最小要件 | 推奨 |
|------|---------|------|
| OS | Windows 10 / macOS 12 / Ubuntu 20.04 | Windows 11 / macOS 14 / Ubuntu 22.04 |
| CPU | 2コア | 4コア以上 |
| メモリ | 4 GB | 8 GB以上 |
| ストレージ | 5 GB（ソースコード + Docker） | 20 GB（ローカルLLMモデル含む） |
| Python | 3.11 | 3.11.x |
| Node.js | 18.x | 20.x LTS |
| Docker | 24.0 | 最新安定版 |
| Docker Compose | 2.20 | 最新安定版 |

### 本番環境

| 項目 | 最小要件 | 推奨 |
|------|---------|------|
| vCPU | 2 | 4以上 |
| メモリ | 4 GB | 8 GB以上 |
| ストレージ | 20 GB SSD | 50 GB SSD |
| PostgreSQL | 16.x | 16.x + pgvector |
| Redis | 7.x | 7.x |
| ネットワーク | HTTPS (443) | HTTPS + WSS |

### 外部サービス依存

| サービス | 用途 | 必須/任意 |
|---------|------|----------|
| Azure AI Foundry | LLMプロバイダー（デフォルト） | いずれか1つ必須 |
| Anthropic API | LLMプロバイダー（直接） | 任意（フォールバック） |
| AWS Bedrock | LLMプロバイダー | 任意（フォールバック） |
| GCP Vertex AI | LLMプロバイダー | 任意（フォールバック） |
| Ollama | ローカルLLM | 任意（開発用） |
| Azure OpenAI | リアルタイム音声・TTS | Phase 2以降で必要 |
| Azure Speech | 発音評価 | Phase 4で必要 |
| Stripe | 決済 | Phase 3で必要 |
| PostgreSQL 16 | メインDB | 必須 |
| Redis 7 | キャッシュ・セッション | 必須 |

---

## 3. 技術スタック詳細

### バックエンド

| カテゴリ | パッケージ | バージョン | 用途 |
|---------|-----------|-----------|------|
| Webフレームワーク | FastAPI | 0.115.6 | REST API + WebSocket |
| ASGIサーバー | Uvicorn | 0.34.0 | 本番サーバー |
| ORM | SQLAlchemy | 2.0.36 | 非同期DB操作 |
| DB ドライバ (async) | asyncpg | 0.30.0 | PostgreSQL非同期接続 |
| DB ドライバ (sync) | psycopg2-binary | 2.9.10 | Alembicマイグレーション用 |
| マイグレーション | Alembic | 1.14.1 | DBスキーマ管理 |
| Redis | redis-py | 5.2.1 | キャッシュ・セッション |
| HTTP クライアント | httpx | 0.28.1 | 外部API呼び出し |
| 認証 (JWT) | python-jose | 3.3.0 | JWTトークン生成・検証 |
| パスワードハッシュ | passlib (bcrypt) | 1.7.4 | パスワード暗号化 |
| 設定管理 | pydantic-settings | 2.7.1 | 環境変数バリデーション |
| メールバリデーション | email-validator | 2.1.1 | メール形式検証 |
| WebSocket | websockets | 13.1 | リアルタイム音声通信 |
| 決済 | stripe | 11.4.1 | サブスクリプション管理 |
| 数値計算 | numpy | 1.26.4 | 音声データ処理 |
| 構造化ログ | structlog | 24.4.0 | JSON形式ログ出力 |
| LLM (Anthropic) | anthropic | 0.43.0 | Anthropic Direct API |
| LLM (AWS) | boto3 | 1.35.0 | AWS Bedrock |
| LLM (GCP) | google-cloud-aiplatform | 1.75.0 | GCP Vertex AI |
| GCP認証 | google-auth | 2.37.0 | GCPサービスアカウント |

### フロントエンド

| カテゴリ | パッケージ | バージョン | 用途 |
|---------|-----------|-----------|------|
| フレームワーク | Next.js | 15.1.x | SSR + SPA |
| UIライブラリ | React | 19.0.x | コンポーネントUI |
| 状態管理 | Zustand | 5.0.x | グローバルステート |
| アイコン | lucide-react | 0.468.x | UIアイコン |
| 言語 | TypeScript | 5.7.x | 型安全なJS |
| CSS | Tailwind CSS | 4.0.x | ユーティリティCSS |
| リンター | ESLint | 9.0.x | コード品質 |
| テスト | Vitest | 2.1.x | ユニットテスト |
| テスト (DOM) | Testing Library | 16.1.x | コンポーネントテスト |
| テスト (カバレッジ) | @vitest/coverage-v8 | 2.1.x | カバレッジ計測 |
| APIモック | MSW | 2.6.x | テスト用APIモック |

### インフラ・DevOps

| カテゴリ | ツール | バージョン | 用途 |
|---------|-------|-----------|------|
| コンテナ | Docker | 24+ | アプリケーションコンテナ |
| オーケストレーション | Docker Compose | 2.20+ | ローカル・ステージング |
| IaC | Terraform | 1.5+ | マルチクラウドインフラ |
| CI/CD | GitHub Actions | - | 自動テスト・デプロイ |
| コンテナスキャン | Trivy | 最新 | 脆弱性スキャン |
| Pythonリンター | Ruff | 最新 | 高速リンティング |
| パッケージ監査 | pip-audit / npm audit | 最新 | 依存関係脆弱性チェック |

---

## 4. データベース設計

### ER図（テキスト形式）

```
+-------------------+       +---------------------------+
|      users        |       |  conversation_sessions    |
+-------------------+       +---------------------------+
| PK id (UUID)      |<------| FK user_id (UUID)         |
|    email           |  1:N  | PK id (UUID)              |
|    name            |       |    mode                   |
|    hashed_password |       |    scenario_description   |
|    entra_id        |       |    overall_score (JSONB)  |
|    native_language |       |    api_tokens_used        |
|    target_level    |       +---------------------------+
|    daily_goal_min  |                |
|    subscription_   |                | 1:N
|      plan          |                v
|    api_usage_      |       +---------------------------+
|      monthly       |       |  conversation_messages    |
+-------------------+       +---------------------------+
        |                   | PK id (UUID)              |
        |                   | FK session_id (UUID)      |
        | 1:N               |    role                   |
        v                   |    content                |
+-------------------+       |    feedback (JSONB)       |
|   review_items    |       |    pronunciation_score    |
+-------------------+       |      (JSONB)              |
| PK id (UUID)      |       +---------------------------+
| FK user_id (UUID) |
| FK source_session |       +---------------------------+
|    _id (UUID)     |       |      daily_stats          |
|    item_type      |       +---------------------------+
|    content (JSONB)|       | PK id (UUID)              |
|    stability      |       | FK user_id (UUID)         |
|    difficulty     |       |    date                   |
|    ease_factor    |       |    practice_minutes       |
|    interval_days  |       |    sessions_completed     |
|    repetitions    |       |    reviews_completed      |
|    next_review_at |       |    grammar_accuracy       |
+-------------------+       |    weak_patterns (JSONB)  |
                            +---------------------------+
+-------------------+
|  subscriptions    |       +---------------------------+
+-------------------+       |    api_usage_log          |
| PK id (UUID)      |       +---------------------------+
| FK user_id (UUID) |       | PK id (UUID)              |
|    stripe_customer|       | FK user_id (UUID)         |
|      _id          |       |    api_provider           |
|    stripe_sub_id  |       |    model_name             |
|    plan           |       |    input_tokens           |
|    status         |       |    output_tokens          |
|    cancel_at_     |       |    audio_seconds          |
|      period_end   |       |    estimated_cost_usd     |
+-------------------+       +---------------------------+

+-------------------+       +---------------------------+
| pattern_mastery   |       | sound_pattern_mastery     |
+-------------------+       +---------------------------+
| PK id (UUID)      |       | PK id (UUID)              |
| FK user_id (UUID) |       | FK user_id (UUID)         |
|    pattern_id     |       |    pattern_type           |
|    pattern_       |       |    pattern_text           |
|      category     |       |    ipa_notation           |
|    skill_stage    |       |    accuracy               |
|    practice_count |       |    practice_count         |
|    accuracy_rate  |       |    last_practiced_at      |
+-------------------+       +---------------------------+
```

### テーブル詳細

#### 4.1 users（ユーザー）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | ユーザーID |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | - | メールアドレス |
| name | VARCHAR(255) | NOT NULL | - | 表示名 |
| hashed_password | VARCHAR(512) | NOT NULL | - | bcryptハッシュ化パスワード |
| entra_id | VARCHAR(255) | UNIQUE, NULLABLE | NULL | Microsoft Entra ID |
| native_language | VARCHAR(10) | NOT NULL | 'ja' | 母国語コード |
| target_level | VARCHAR(10) | NOT NULL | 'C1' | 目標レベル（CEFR） |
| daily_goal_minutes | INTEGER | NOT NULL | 15 | 日次目標（分） |
| subscription_plan | VARCHAR(50) | NOT NULL | 'free' | プラン名 |
| api_usage_monthly | INTEGER | NOT NULL | 0 | 月間API使用回数 |
| api_usage_reset_at | TIMESTAMPTZ | NULLABLE | NULL | API使用回数リセット日時 |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新日時（自動更新） |

リレーション: conversation_sessions(1:N), review_items(1:N), daily_stats(1:N), api_usage_logs(1:N), subscription(1:1)

#### 4.2 conversation_sessions（会話セッション）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | セッションID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| mode | VARCHAR(50) | NOT NULL | - | 練習モード（free_talk, scenario等） |
| scenario_description | TEXT | NULLABLE | NULL | シナリオ説明文 |
| started_at | TIMESTAMPTZ | NOT NULL | now() | 開始日時 |
| ended_at | TIMESTAMPTZ | NULLABLE | NULL | 終了日時 |
| duration_seconds | INTEGER | NULLABLE | NULL | セッション長（秒） |
| overall_score | JSONB | NULLABLE | NULL | 総合スコア |
| api_tokens_used | INTEGER | NULLABLE | 0 | 使用トークン数 |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |

overall_score の JSONB構造例:

```json
{
  "grammar": 85,
  "vocabulary": 78,
  "fluency": 72,
  "pronunciation": 80,
  "overall": 79
}
```

#### 4.3 conversation_messages（会話メッセージ）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | メッセージID |
| session_id | UUID | FK(conversation_sessions.id, CASCADE), NOT NULL, INDEX | - | セッションID |
| role | VARCHAR(20) | NOT NULL | - | 発話者（user / assistant） |
| content | TEXT | NOT NULL | - | メッセージ本文 |
| audio_blob_url | VARCHAR(1024) | NULLABLE | NULL | 音声ファイルURL |
| feedback | JSONB | NULLABLE | NULL | AIフィードバック |
| pronunciation_score | JSONB | NULLABLE | NULL | 発音スコア詳細 |
| response_time_ms | INTEGER | NULLABLE | NULL | 応答時間（ミリ秒） |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |

feedback の JSONB構造例:

```json
{
  "corrections": [
    {
      "original": "I go to office yesterday",
      "corrected": "I went to the office yesterday",
      "explanation": "過去形 + 冠詞の欠落"
    }
  ],
  "naturalness": 3,
  "suggestions": ["Try using more varied tense structures"]
}
```

#### 4.4 review_items（復習アイテム）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | アイテムID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| item_type | VARCHAR(50) | NOT NULL | - | アイテム種別（grammar, vocabulary等） |
| content | JSONB | NOT NULL | - | 復習内容 |
| source_session_id | UUID | FK(conversation_sessions.id), NULLABLE | NULL | 抽出元セッション |
| ease_factor | FLOAT | NOT NULL | 2.5 | SM-2互換の容易度因子 |
| interval_days | INTEGER | NOT NULL | 0 | 現在の復習間隔（日） |
| repetitions | INTEGER | NOT NULL | 0 | 復習回数 |
| next_review_at | TIMESTAMPTZ | NULLABLE, INDEX | NULL | 次回復習予定日時 |
| last_reviewed_at | TIMESTAMPTZ | NULLABLE | NULL | 最終復習日時 |
| last_quality | INTEGER | NULLABLE | NULL | 最終評価（1-4） |
| stability | FLOAT | NOT NULL | 1.0 | FSRS安定度パラメータ |
| difficulty | FLOAT | NOT NULL | 0.3 | FSRS難易度パラメータ |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |

#### 4.5 daily_stats（日次統計）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | 統計ID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| date | DATE | NOT NULL, INDEX | - | 集計日 |
| practice_minutes | INTEGER | NOT NULL | 0 | 練習時間（分） |
| sessions_completed | INTEGER | NOT NULL | 0 | 完了セッション数 |
| reviews_completed | INTEGER | NOT NULL | 0 | 完了復習数 |
| new_expressions_learned | INTEGER | NOT NULL | 0 | 新規習得表現数 |
| grammar_accuracy | FLOAT | NULLABLE | NULL | 文法正確率 |
| avg_response_time_ms | INTEGER | NULLABLE | NULL | 平均応答時間（ms） |
| listening_speed_max | FLOAT | NULLABLE | NULL | リスニング最大速度 |
| pronunciation_avg_score | FLOAT | NULLABLE | NULL | 平均発音スコア |
| weak_patterns | JSONB | NULLABLE | NULL | 弱点パターン |

制約: `UNIQUE(user_id, date)` -- ユーザーごとに日付はユニーク

#### 4.6 subscriptions（サブスクリプション）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | サブスクリプションID |
| user_id | UUID | FK(users.id), UNIQUE, NOT NULL, INDEX | - | ユーザーID |
| stripe_customer_id | VARCHAR(255) | UNIQUE, NULLABLE | NULL | Stripe顧客ID |
| stripe_subscription_id | VARCHAR(255) | UNIQUE, NULLABLE | NULL | StripeサブスクリプションID |
| plan | VARCHAR(50) | NOT NULL | 'free' | プラン名 |
| status | VARCHAR(50) | NOT NULL | 'active' | 状態（active/canceled等） |
| current_period_start | TIMESTAMPTZ | NULLABLE | NULL | 現在の請求期間開始 |
| current_period_end | TIMESTAMPTZ | NULLABLE | NULL | 現在の請求期間終了 |
| cancel_at_period_end | BOOLEAN | NOT NULL | false | 期間終了時にキャンセル |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |
| updated_at | TIMESTAMPTZ | NOT NULL | now() | 更新日時 |

#### 4.7 api_usage_log（API利用ログ）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | ログID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| api_provider | VARCHAR(50) | NOT NULL | - | プロバイダー名 |
| model_name | VARCHAR(100) | NOT NULL | - | モデル名 |
| input_tokens | INTEGER | NOT NULL | 0 | 入力トークン数 |
| output_tokens | INTEGER | NOT NULL | 0 | 出力トークン数 |
| audio_seconds | FLOAT | NOT NULL | 0.0 | 音声処理時間（秒） |
| estimated_cost_usd | FLOAT | NOT NULL | 0.0 | 推定コスト（USD） |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 記録日時 |

#### 4.8 pattern_mastery（パターン習熟度）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | 習熟度ID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| pattern_id | VARCHAR(100) | NOT NULL, INDEX | - | パターン識別子 |
| pattern_category | VARCHAR(50) | NOT NULL, INDEX | - | パターンカテゴリ |
| skill_stage | VARCHAR(20) | NOT NULL | 'understood' | 習熟段階 |
| practice_count | INTEGER | NOT NULL | 0 | 練習回数 |
| accuracy_rate | FLOAT | NOT NULL | 0.0 | 正確率 |
| last_practiced_at | TIMESTAMPTZ | NOT NULL | now() | 最終練習日時 |
| first_used_in_freetalk | TIMESTAMPTZ | NULLABLE | NULL | フリートーク初使用日時 |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |

skill_stage の遷移: `understood` -> `drilling` -> `acquired`

#### 4.9 sound_pattern_mastery（音声パターン習熟度）

| カラム名 | 型 | 制約 | デフォルト | 説明 |
|---------|---|------|-----------|------|
| id | UUID | PK | uuid4() | 習熟度ID |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | - | ユーザーID |
| pattern_type | VARCHAR(30) | NOT NULL, INDEX | - | パターン種別 |
| pattern_text | VARCHAR(500) | NOT NULL | - | 対象テキスト |
| ipa_notation | VARCHAR(500) | NULLABLE | NULL | IPA表記 |
| accuracy | FLOAT | NOT NULL | 0.0 | 正確率 |
| practice_count | INTEGER | NOT NULL | 0 | 練習回数 |
| last_practiced_at | TIMESTAMPTZ | NULLABLE | NULL | 最終練習日時 |
| created_at | TIMESTAMPTZ | NOT NULL | now() | 作成日時 |

pattern_type の列挙値: `linking`, `reduction`, `flapping`, `deletion`, `weak_form`

### インデックス戦略

| テーブル | インデックス | 種別 | 目的 |
|---------|------------|------|------|
| users | email | UNIQUE | ログイン検索 |
| users | entra_id | UNIQUE | SSO検索 |
| conversation_sessions | user_id | B-tree | ユーザー別セッション取得 |
| conversation_messages | session_id | B-tree | セッション内メッセージ取得 |
| review_items | user_id | B-tree | ユーザー別復習アイテム |
| review_items | next_review_at | B-tree | 復習期限クエリ |
| daily_stats | user_id | B-tree | ユーザー別統計取得 |
| daily_stats | date | B-tree | 日付範囲クエリ |
| daily_stats | (user_id, date) | UNIQUE | ユニーク制約 |
| subscriptions | user_id | UNIQUE | 1:1リレーション |
| api_usage_log | user_id | B-tree | ユーザー別利用量集計 |
| pattern_mastery | user_id | B-tree | ユーザー別パターン取得 |
| pattern_mastery | pattern_id | B-tree | パターン検索 |
| pattern_mastery | pattern_category | B-tree | カテゴリ別検索 |
| sound_pattern_mastery | user_id | B-tree | ユーザー別検索 |
| sound_pattern_mastery | pattern_type | B-tree | 種別検索 |

---

## 5. API仕様概要

### ルーター構成

```
FastAPI App (FluentEdge API v1.0.0)
|
+-- /health             [health]           ヘルスチェック
|
+-- /api/auth           [auth]             認証（登録・ログイン）
|
+-- Phase 1 (MVP)
|   +-- /api/talk       [talk]             AI英会話
|   +-- /api/speaking   [speaking]         スピーキング練習
|   +-- /api/review     [review]           復習（FSRS）
|   +-- /api/analytics  [analytics]        学習分析
|
+-- Phase 2（音声統合）
|   +-- /api/listening             [listening]       リスニング練習
|   +-- /api/speaking/pattern      [pattern]         パターン練習
|   +-- /api/talk/realtime         [realtime-voice]  リアルタイム音声
|
+-- Phase 3（学習最適化）
|   +-- /api/listening/mogomogo    [mogomogo]        もごもご英語
|   +-- /api/analytics/advanced    [analytics-adv]   高度分析
|   +-- /api/subscription          [subscription]    サブスクリプション
|
+-- Phase 4（高度な機能）
    +-- /api/speaking/pronunciation [pronunciation]  発音分析
    +-- /api/listening/comprehension[comprehension]   聴解力テスト
```

### エンドポイント一覧（全40+エンドポイント）

| HTTP | パス | 機能 | 認証 |
|------|-----|------|------|
| GET | /health | ヘルスチェック | 不要 |
| GET | /health/ready | レディネスチェック | 不要 |
| POST | /api/auth/register | ユーザー登録 | 不要 |
| POST | /api/auth/login | ログイン（JWT発行） | 不要 |
| GET | /api/auth/me | 現在のユーザー情報 | 必要 |
| POST | /api/talk/sessions | 会話セッション開始 | 必要 |
| POST | /api/talk/sessions/{id}/messages | メッセージ送信 | 必要 |
| GET | /api/talk/sessions/{id} | セッション詳細 | 必要 |
| GET | /api/talk/sessions | セッション一覧 | 必要 |
| POST | /api/talk/sessions/{id}/end | セッション終了 | 必要 |
| POST | /api/speaking/practice | スピーキング練習 | 必要 |
| POST | /api/speaking/evaluate | スピーキング評価 | 必要 |
| GET | /api/review/items | 復習アイテム一覧 | 必要 |
| GET | /api/review/due | 復習期限アイテム | 必要 |
| POST | /api/review/items/{id}/answer | 復習回答 | 必要 |
| GET | /api/analytics/dashboard | ダッシュボード | 必要 |
| GET | /api/analytics/daily | 日次統計 | 必要 |
| GET | /api/analytics/weekly | 週次統計 | 必要 |
| POST | /api/listening/dictation | ディクテーション練習 | 必要 |
| POST | /api/listening/speed-control | 速度制御リスニング | 必要 |
| POST | /api/speaking/pattern/start | パターン練習開始 | 必要 |
| POST | /api/speaking/pattern/evaluate | パターン評価 | 必要 |
| GET | /api/speaking/pattern/progress | パターン進捗 | 必要 |
| WS | /api/talk/realtime/ws | リアルタイム音声WS | 必要 |
| POST | /api/listening/mogomogo/start | もごもご英語開始 | 必要 |
| POST | /api/listening/mogomogo/check | もごもご英語チェック | 必要 |
| GET | /api/analytics/advanced/report | 高度分析レポート | 必要 |
| GET | /api/analytics/advanced/trends | トレンド分析 | 必要 |
| POST | /api/subscription/create | サブスクリプション作成 | 必要 |
| GET | /api/subscription/status | サブスクリプション状態 | 必要 |
| POST | /api/subscription/cancel | サブスクリプションキャンセル | 必要 |
| POST | /api/subscription/webhook | Stripe Webhook | Webhook検証 |
| POST | /api/speaking/pronunciation/analyze | 発音分析 | 必要 |
| GET | /api/speaking/pronunciation/patterns | 音声パターン一覧 | 必要 |
| POST | /api/listening/comprehension/test | 聴解力テスト | 必要 |
| GET | /api/listening/comprehension/results | テスト結果 | 必要 |

### 統一エラーレスポンス形式

全てのエラーレスポンスは以下の統一形式で返却される:

```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "認証に失敗しました",
    "details": null
  }
}
```

### 例外階層

```
AppError (base)
  +-- AuthenticationError       HTTP 401
  +-- AuthorizationError        HTTP 403
  +-- NotFoundError             HTTP 404
  +-- ValidationError           HTTP 422
  +-- RateLimitError            HTTP 429
  +-- LLMProviderError          HTTP 502
  +-- LLMTimeoutError           HTTP 504
  +-- LLMRateLimitError         HTTP 429
  +-- ExternalServiceError      HTTP 502
```

---

## 6. LLMプロバイダー仕様

### プロバイダーアーキテクチャ

```
+-----------------------------------------------------------+
|                     LLMService (シングルトン)                |
+-----------------------------------------------------------+
|  設定から LLMRouter を自動構築                               |
|  PROVIDER_MAP でプロバイダーをインスタンス化                   |
+-----------------------------------------------------------+
                         |
                         v
+-----------------------------------------------------------+
|                     LLMRouter                              |
+-----------------------------------------------------------+
|  プライマリ + フォールバックプロバイダーを管理                  |
|  _execute_with_fallback() で自動切り替え                     |
|  プロバイダーごとに CircuitBreaker を保持                     |
+-----------------------------------------------------------+
          |                    |                  |
          v                    v                  v
+------------------+ +------------------+ +------------------+
| CircuitBreaker   | | CircuitBreaker   | | CircuitBreaker   |
| (provider A)     | | (provider B)     | | (provider C)     |
+------------------+ +------------------+ +------------------+
          |                    |                  |
          v                    v                  v
+------------------+ +------------------+ +------------------+
| LLMProvider      | | LLMProvider      | | LLMProvider      |
| (concrete impl)  | | (concrete impl)  | | (concrete impl)  |
+------------------+ +------------------+ +------------------+
```

### LLMProvider 抽象基底クラス

```python
class LLMProvider(ABC):
    async def chat(messages, model, temperature, max_tokens) -> str
    async def chat_json(messages, model, temperature, max_tokens) -> dict
    def get_usage_info() -> dict
    async def health_check() -> bool
```

### モデルマッピング

| プロバイダー | 設定キー | Opus モデル | Sonnet モデル | Haiku モデル |
|-------------|---------|------------|--------------|-------------|
| azure_foundry | claude_opus_model / _sonnet / _haiku | claude-opus-4-6 | claude-sonnet-4-5-20250929 | claude-haiku-4-5-20251001 |
| anthropic | (同上) | claude-opus-4-6 | claude-sonnet-4-5-20250929 | claude-haiku-4-5-20251001 |
| bedrock | aws_bedrock_model_opus / _sonnet / _haiku | anthropic.claude-opus-4-6-v1:0 | anthropic.claude-sonnet-4-5-20250929-v1:0 | anthropic.claude-haiku-4-5-20251001-v1:0 |
| vertex | gcp_vertex_model_opus / _sonnet / _haiku | claude-opus-4-6 | claude-sonnet-4-5-20250929 | claude-haiku-4-5-20251001 |
| local | local_model_smart / local_model_fast | - | llama3.1:8b | llama3.1:8b |

### コスト試算（USD / 100万トークン）

| プロバイダー | モデル | 入力単価 | 出力単価 |
|-------------|-------|---------|---------|
| azure_foundry | Opus | $5.00 | $25.00 |
| azure_foundry | Sonnet | $3.00 | $15.00 |
| azure_foundry | Haiku | $0.80 | $4.00 |
| anthropic | Opus | $5.00 | $25.00 |
| anthropic | Sonnet | $3.00 | $15.00 |
| anthropic | Haiku | $0.80 | $4.00 |
| bedrock | Opus | $5.00 | $25.00 |
| bedrock | Sonnet | $3.00 | $15.00 |
| bedrock | Haiku | $0.80 | $4.00 |
| vertex | Opus | $5.00 | $25.00 |
| vertex | Sonnet | $3.00 | $15.00 |
| vertex | Haiku | $0.80 | $4.00 |
| local | 全モデル | $0.00 | $0.00 |

### 月間コスト試算（1ユーザーあたり）

| 利用パターン | 月間セッション | 平均トークン/セッション | モデル | 月間コスト |
|-------------|-------------|---------------------|-------|-----------|
| ライトユーザー | 20回 | 入力2K + 出力1K | Haiku | 約 $0.11 |
| 標準ユーザー | 60回 | 入力3K + 出力1.5K | Haiku | 約 $0.50 |
| ヘビーユーザー | 120回 | 入力4K + 出力2K | Sonnet | 約 $5.04 |
| ローカル | 無制限 | - | Ollama | $0.00 |

### レジリエンス機能

#### サーキットブレーカー

```
状態遷移図:

    [closed] ----失敗 x N----> [open]
       ^                          |
       |                      timeout経過
       |                          |
       +---成功---[half_open]<----+
                       |
                     失敗
                       |
                       v
                    [open]
```

| パラメータ | 環境変数 | デフォルト | 説明 |
|-----------|---------|-----------|------|
| failure_threshold | LLM_CIRCUIT_BREAKER_THRESHOLD | 5 | オープン遷移の連続失敗数 |
| recovery_timeout | LLM_CIRCUIT_BREAKER_TIMEOUT | 60.0秒 | オープンからハーフオープンまでの待機時間 |

#### リトライポリシー

| パラメータ | 環境変数 | デフォルト | 説明 |
|-----------|---------|-----------|------|
| max_retries | LLM_RETRY_MAX | 3 | 最大リトライ回数 |
| base_delay | - | 1.0秒 | 初回リトライの基本待機時間 |
| max_delay | - | 30.0秒 | 最大待機時間 |

計算式: `delay = min(base_delay * 2^attempt, max_delay) * random(0.5, 1.0)`

#### レートリミッター

| パラメータ | 環境変数 | デフォルト | 説明 |
|-----------|---------|-----------|------|
| requests_per_minute | LLM_RATE_LIMIT_RPM | 60 | 1分あたり最大リクエスト数 |

方式: Token Bucket（バケットが空の場合は次のトークン補充まで待機）

---

## 7. FSRSアルゴリズム仕様

### 概要

FSRS (Free Spaced Repetition Scheduler) はオープンソースの間隔反復スケジューリングアルゴリズム。
安定度(stability)と難易度(difficulty)に基づいて最適な復習間隔を計算する。

参考: https://github.com/open-spaced-repetition/fsrs4anki

### レーティング定義

| 値 | ラベル | 意味 |
|----|-------|------|
| 1 | Again | 完全に忘れていた |
| 2 | Hard | 思い出せたが困難だった |
| 3 | Good | 適度な努力で思い出せた |
| 4 | Easy | 即座に思い出せた |

### 重みパラメータ（w0 - w18）

```
w0  = 0.4     # 初期安定度調整（Again時）
w1  = 0.9     # 初期安定度（Hard時）
w2  = 2.3     # 初期安定度（Good時）
w3  = 6.0     # 初期安定度（Easy時）
w4  = 7.0     # 難易度の初期値影響
w5  = 0.5     # 難易度更新の平均回帰係数
w6  = 1.2     # 難易度更新のレーティング影響
w7  = 0.01    # 安定度成功時の基本増加率
w8  = 1.5     # 安定度と難易度の交互作用
w9  = 0.1     # 安定度に対する記憶度の影響
w10 = 1.0     # 安定度の自己参照係数
w11 = 2.0     # 失敗時の安定度減衰
w12 = 0.02    # 失敗時の難易度影響
w13 = 0.3     # 失敗時の安定度影響
w14 = 0.5     # Hard時の安定度ペナルティ
w15 = 2.0     # Easy時の安定度ボーナス
w16 = 0.2     # 記憶度の追加影響
w17 = 3.0     # 短期記憶の減衰
w18 = 0.7     # 追加パラメータ
```

### 主要計算式

#### 記憶度（Retrievability）

```
R(t) = (1 + t / S) ^ decay

  t     = 前回復習からの経過日数
  S     = 安定度（stability）
  decay = -0.5（固定）
```

R(t)は0.0〜1.0の範囲で、復習直後は1.0に近く、時間経過とともに減少する。

#### 最適復習間隔

```
interval = S * ((1/R_desired)^(1/decay) - 1)

  S         = 安定度
  R_desired = 目標記憶保持率（デフォルト: 0.9 = 90%）
  decay     = -0.5
```

#### 初期難易度

```
D0 = w4 - exp(w5 * (rating - 1)) + 1
```

値は [0.1, 1.0] にクランプされる。

#### 難易度更新

```
D' = w5 * D0(4) + (1 - w5) * (D - w6 * (rating - 3))
```

平均回帰 + レーティングに基づく調整。

#### 成功時の安定度更新（rating >= 2）

```
S'_success = S * (
    1 + exp(w7) * (11 - D*10) * S^(-w8) *
    (exp(w9 * (1 - R)) - 1) *
    hard_penalty * easy_bonus
)

  hard_penalty = w14 (rating==2 の場合), 1.0 (それ以外)
  easy_bonus   = w15 (rating==4 の場合), 1.0 (それ以外)
```

#### 失敗時の安定度更新（rating == 1）

```
S'_fail = w11 * (D*10+0.1)^(-w12) *
          ((S+1)^w13 - 1) *
          exp(w16 * (1 - R))
```

失敗時の安定度は前回の安定度以下に制限される。

### FSRSCard データ構造

```python
@dataclass
class FSRSCard:
    stability: float = 1.0       # 安定度
    difficulty: float = 0.3      # 難易度
    interval: float = 0.0        # 現在の復習間隔（日）
    repetitions: int = 0         # 復習回数
    ease_factor: float = 2.5     # SM-2互換の容易度因子
    next_review: datetime        # 次回復習日時
    last_review: datetime | None # 最終復習日時
```

### 復習フロー

```
ユーザーが復習カードに回答
         |
         v
    repetitions == 0?
    /           \
  YES            NO
   |              |
   v              v
初期パラメータ設定   記憶度R(t)を計算
   |              |
   v              v
初期安定度 =      rating >= 2?
  w[rating-1]   /        \
   |          YES         NO
   v           |           |
初期難易度     v           v
  D0計算    S'_success   S'_fail
   |        計算          計算
   |           \         /
   v            v       v
復習間隔を計算   難易度を更新
   |                |
   v                v
next_review =    復習間隔を計算
  now + interval     |
   |                v
   v           next_review更新
 カード状態を返却 <---+
```

---

## 8. フロントエンド仕様

### 画面一覧

| 画面ID | パス | 画面名 | 認証 | Phase |
|--------|-----|--------|------|-------|
| F-001 | / | ランディングページ | 不要 | 1 |
| F-002 | /login | ログイン | 不要 | 1 |
| F-003 | /register | ユーザー登録 | 不要 | 1 |
| F-004 | /dashboard | ダッシュボード | 必要 | 1 |
| F-005 | /talk | AI英会話（テキスト＋音声） | 必要 | 1 |
| F-006 | /talk/realtime | AI英会話（音声） | 必要 | 2 |
| F-007 | /speaking | スピーキング練習 | 必要 | 1 |
| F-008 | /speaking/pattern | パターン練習 | 必要 | 2 |
| F-009 | /speaking/pronunciation | 発音分析 | 必要 | 4 |
| F-010 | /review | 復習カード（FSRS） | 必要 | 1 |
| F-011 | /listening | リスニング練習 | 必要 | 2 |
| F-012 | /listening/mogomogo | もごもご英語 | 必要 | 3 |
| F-013 | /listening/comprehension | 聴解力テスト | 必要 | 4 |
| F-014 | /analytics | 学習分析 | 必要 | 1 |
| F-015 | /analytics/advanced | 高度分析 | 必要 | 3 |
| F-016 | /subscription | サブスクリプション管理 | 必要 | 3 |
| F-017 | /settings | ユーザー設定 | 必要 | 1 |

### 状態管理（Zustand 5）

```
Zustand Store 構成:

+-------------------------+
| useAuthStore            |
|-------------------------|
| user: User | null       |
| token: string | null    |
| isAuthenticated: bool   |
| login(email, pass)      |
| logout()                |
| register(data)          |
+-------------------------+

+-------------------------+
| useTalkStore            |
|-------------------------|
| sessions: Session[]     |
| currentSession: Session |
| messages: Message[]     |
| isLoading: boolean      |
| startSession(mode)      |
| sendMessage(text)       |
| endSession()            |
+-------------------------+

+-------------------------+
| useReviewStore          |
|-------------------------|
| items: ReviewItem[]     |
| dueItems: ReviewItem[]  |
| currentItem: ReviewItem |
| fetchDueItems()         |
| submitAnswer(id, rating)|
+-------------------------+

+-------------------------+
| useAnalyticsStore       |
|-------------------------|
| dailyStats: DailyStat[] |
| weeklyStats: WeeklyStat |
| dashboard: Dashboard    |
| fetchDashboard()        |
| fetchDaily(range)       |
+-------------------------+

+-------------------------+
| useSettingsStore        |
|-------------------------|
| nativeLanguage: string  |
| targetLevel: string     |
| dailyGoal: number       |
| updateSettings(data)    |
+-------------------------+
```

### コンポーネント設計方針

- **React 19**: Server Components + Client Components の併用
- **Next.js 15**: App Router を使用
- **スタイリング**: Tailwind CSS 4（ユーティリティファースト）
- **アイコン**: lucide-react
- **フォーム**: React Hook Form（予定）
- **APIクライアント**: fetch API + カスタムフック
- **テスト**: Vitest + Testing Library + MSW

### レスポンシブ対応

| ブレークポイント | 幅 | 対象 |
|---------------|---|------|
| sm | 640px+ | スマートフォン（横） |
| md | 768px+ | タブレット |
| lg | 1024px+ | デスクトップ |
| xl | 1280px+ | ワイドデスクトップ |

### デスクトップレスポンシブデザイン詳細

全変更は `lg:` (1024px+) / `xl:` (1280px+) プレフィックスのみ使用し、モバイル/タブレット表示に影響なし。

| ページ | lg (1024px+) の変更 |
|--------|---------------------|
| AppShell | `max-w-7xl mx-auto`, パディング `lg:px-12 xl:px-16` |
| Dashboard | 統計3列グリッド (`lg:grid-cols-3`), Quick Start横並び3列 |
| Talk (setup) | 2パネルレイアウト (`lg:flex lg:gap-8`), モード2列, プレビューサイドパネル |
| Talk (session) | ChatWindow `lg:px-8` パディング, MessageBubble `lg:max-w-[60%]` |
| Talk (voice) | VoiceChat キャンバス `lg:w-96 lg:h-96` |
| Listening hub | 2列メニュー (`lg:grid-cols-2`) |
| Listening Shadowing | `lg:max-w-3xl` フォーム幅, Difficulty+Accent横並び |
| Listening Comprehension | `lg:max-w-3xl` フォーム幅, トピック4列 (`lg:grid-cols-4`) |
| Speaking hub | 2列メニュー (`lg:grid-cols-2`) |
| Speaking Pattern | カテゴリー3列 (`lg:grid-cols-3`), `lg:max-w-2xl` |
| Analytics | スキル横並び (`lg:flex lg:gap-8`) |
| Exercise Cards | FlashCard/PatternCard/ReviewCard: `lg:max-w-2xl` |

### 音声チャット (Voice Chat)

セッション中のデフォルトモードは音声モード。Web Speech API (STT) + Talk API + Azure TTS で実現。

| 項目 | 仕様 |
|------|------|
| STT | Web Speech API (SpeechRecognition) |
| AI応答 | Talk API (`POST /api/talk/sessions/{id}/messages`) |
| TTS | Azure Speech (`POST /api/tts`) |
| 対応ブラウザ | Chrome, Edge, Safari (Firefox非対応→テキストモードフォールバック) |
| デフォルト | 音声モード (`isVoiceMode = true`) |

---

## 9. 非機能要件

### 9.1 性能要件

| 項目 | 目標値 | 測定方法 |
|------|-------|---------|
| API応答時間（通常） | 200ms以下（p95） | structlogでduration_msを記録 |
| API応答時間（LLM経由） | 3秒以下（p95） | LLMレスポンス時間を含む |
| WebSocket レイテンシ | 500ms以下 | リアルタイム音声の往復時間 |
| ページロード（初回） | 2秒以下 | Lighthouse スコア |
| ページロード（遷移） | 500ms以下 | Next.js プリフェッチ |
| 同時接続WebSocket | 100接続/サーバー | 負荷テストで検証 |
| データベースクエリ | 50ms以下（p95） | SQLAlchemy + asyncpg |
| Redis キャッシュ | 5ms以下 | redis-py計測 |

### 9.2 可用性要件

| 項目 | 目標値 | 備考 |
|------|-------|------|
| 稼働率 | 99.5%（月間） | 年間ダウンタイム 43.8時間以内 |
| 計画停止 | 月1回、最大30分 | メンテナンスウィンドウ（日曜深夜） |
| RTO（復旧目標時間） | 30分 | 障害発生から復旧完了まで |
| RPO（復旧ポイント目標） | 1時間 | 許容データ損失時間 |
| ヘルスチェック間隔 | 30秒 | Docker HEALTHCHECK |
| フェイルオーバー | 自動（LLMプロバイダー） | CircuitBreaker + Fallback |

### 9.3 スケーラビリティ要件

| 項目 | 初期 | 中期（6ヶ月） | 長期（1年） |
|------|-----|-------------|------------|
| 登録ユーザー数 | 100 | 1,000 | 10,000 |
| DAU | 30 | 300 | 3,000 |
| 同時接続数 | 10 | 50 | 200 |
| 月間APIリクエスト | 10万 | 100万 | 1,000万 |
| DBサイズ | 1 GB | 10 GB | 50 GB |

スケーリング戦略:

```
初期（単一サーバー）
+--------+   +--------+   +--------+
| Backend|   |Frontend|   | DB     |
| x1     |   | x1     |   | x1     |
+--------+   +--------+   +--------+

中期（水平スケーリング）
+--------+   +--------+   +--------+   +--------+
| Backend|   | Backend|   |Frontend|   | DB     |
| x1     |   | x2     |   | x2     |   | x1     |
+--------+   +--------+   +--------+   | +Read  |
      \         /              |        | Replica|
   Load Balancer               |        +--------+
                          CDN Cache

長期（マルチリージョン）
+------------------+   +------------------+
| Region A         |   | Region B         |
| Backend x3       |   | Backend x2       |
| Frontend x2      |   | Frontend x2      |
| DB Primary       |   | DB Replica       |
| Redis Primary    |   | Redis Replica    |
+------------------+   +------------------+
         |                       |
    Global Load Balancer / CDN
```

### 9.4 セキュリティ要件

| カテゴリ | 要件 | 実装 |
|---------|------|------|
| 認証 | JWT (HS256) | python-jose, 24時間有効期限 |
| パスワード | bcryptハッシュ | passlib[bcrypt] |
| SSO | Microsoft Entra ID対応 | entra_idフィールド |
| CORS | オリジン制限 | BACKEND_CORS_ORIGINS |
| HTTPS | TLS 1.2以上必須 | リバースプロキシで終端 |
| APIキー | 環境変数のみ | .envファイル（Git除外） |
| SQLインジェクション | パラメタライズドクエリ | SQLAlchemy ORM |
| XSS | React自動エスケープ | Next.js + React |
| CSRF | SameSite Cookie | JWT Bearer方式 |
| レート制限 | Token Bucket方式 | RateLimiter（インメモリ） |
| 依存関係 | 脆弱性スキャン | pip-audit + npm audit |
| コンテナ | イメージスキャン | Trivy（CI/CDで自動実行） |
| シークレット | Gitから除外 | .gitignore + CI環境変数 |
| ログ | 個人情報マスク | structlog + フィルター |
| Webhook | 署名検証 | Stripe Webhook Secret |

### 9.5 ログ・監視要件

| 項目 | 仕様 | 備考 |
|------|------|------|
| ログ形式 | JSON（本番）/ Console（開発） | structlog |
| リクエストログ | 全リクエスト記録 | method, path, status, duration_ms |
| リクエストID | X-Request-ID ヘッダ | UUID4、全ログに付与 |
| ログレベル | 環境変数 LOG_LEVEL | デフォルト: INFO |
| ログローテーション | Docker logging driver | json-file, max 10MB x 3 |
| メトリクス | Prometheus形式（オプション） | Docker Compose monitoring profile |
| ダッシュボード | Grafana（オプション） | Docker Compose monitoring profile |
| アラート | HTTP 5xx率 > 5% で通知 | 外部監視ツール連携 |

### 9.6 テスト要件

| テスト種別 | ツール | カバレッジ目標 | 実行タイミング |
|-----------|-------|-------------|-------------|
| バックエンド単体テスト | pytest + pytest-asyncio | 80%以上 | CI (push/PR) |
| バックエンドリンティング | Ruff | 警告0件 | CI (push/PR) |
| フロントエンド単体テスト | Vitest + Testing Library | 70%以上 | CI (push/PR) |
| フロントエンドリンティング | ESLint | 警告0件 | CI (push/PR) |
| E2Eテスト | Playwright | 主要フロー100% | CI (mainブランチ) |
| セキュリティスキャン | pip-audit + npm audit | 高リスク0件 | CI (push/PR) |
| コンテナスキャン | Trivy | CRITICAL 0件 | CI (push/PR) |
| 負荷テスト | k6 / Locust（予定） | 性能要件充足 | リリース前 |

### 9.7 バックアップ・復旧要件

| 項目 | 仕様 | 備考 |
|------|------|------|
| DBバックアップ | 日次フルバックアップ | pg_dump |
| バックアップ保持 | 30日間 | ストレージコスト考慮 |
| ポイントインタイム復旧 | WALアーカイブ（推奨） | 本番環境のみ |
| リストアテスト | 月1回 | 手順書に基づく |
| Redis | 永続化不要 | キャッシュのみ使用 |
| ファイルストレージ | Azure Blob / S3 | 音声ファイル |
| Terraformステート | Azure Blob + ロック | リモートバックエンド |

---

> 本仕様書はソースコード（backend/app/ 以下）に基づいて作成されています。
> 最新の仕様はソースコードを正とし、相違がある場合はソースコードが優先されます。
