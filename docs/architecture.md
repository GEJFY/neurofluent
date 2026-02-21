# FluentEdge AI アーキテクチャ設計書

FluentEdge AI のシステムアーキテクチャ、コンポーネント構成、データフロー、
LLM 抽象化レイヤー、データベース設計、認証フロー、セキュリティ設計を記述します。

---

## 目次

1. [全体構成図](#全体構成図)
2. [コンポーネント構成](#コンポーネント構成)
3. [LLM 抽象化レイヤー](#llm-抽象化レイヤー)
4. [データフロー](#データフロー)
5. [データベース設計](#データベース設計)
6. [認証フロー](#認証フロー)
7. [セキュリティ設計](#セキュリティ設計)

---

## 全体構成図

```text
+======================================================================+
|                          クライアント                                  |
|  +--------------------------------------------------------------+   |
|  |  Next.js 15 / React 19 / TypeScript 5.7                      |   |
|  |  Tailwind CSS 4 / Zustand 5 (状態管理)                        |   |
|  |  Lucide React (アイコン) / PWA 対応                            |   |
|  +--------------------------------------------------------------+   |
+==================================|===================================+
                                   | REST API (HTTPS)
                                   v
+======================================================================+
|                          バックエンド                                  |
|  +--------------------------------------------------------------+   |
|  |  FastAPI 0.115 / Python 3.11 / Uvicorn 0.34                  |   |
|  |                                                                |   |
|  |  +------------------+  +------------------+  +--------------+ |   |
|  |  | Routers          |  | Services         |  | Prompts      | |   |
|  |  | (13 ルーター)     |  | (10 サービス)    |  | (8 テンプレ) | |   |
|  |  +------------------+  +------------------+  +--------------+ |   |
|  |                                                                |   |
|  |  +------------------+  +------------------+  +--------------+ |   |
|  |  | Middleware        |  | LLM Layer        |  | Schemas      | |   |
|  |  | (ログ, エラー)    |  | (マルチクラウド)  |  | (Pydantic)   | |   |
|  |  +------------------+  +------------------+  +--------------+ |   |
|  +--------------------------------------------------------------+   |
+========|===================|===================|=====================+
         |                   |                   |
         v                   v                   v
+----------------+  +----------------+  +------------------------+
| PostgreSQL 16  |  | Redis 7        |  | LLM Providers          |
| + pgvector     |  | (Cache)        |  |                        |
|                |  |                |  | +--------------------+ |
| 9 テーブル      |  | セッション      |  | | Azure AI Foundry   | |
| SQLAlchemy ORM |  | キャッシュ      |  | | Anthropic Direct   | |
| Alembic 管理   |  | 一時データ      |  | | AWS Bedrock        | |
+----------------+  +----------------+  | | GCP Vertex AI      | |
                                        | | Local (Ollama)     | |
                                        | +--------------------+ |
                                        +------------------------+
```

---

## コンポーネント構成

### Frontend

| レイヤー | 技術 | 説明 |
| --- | --- | --- |
| フレームワーク | Next.js 15 (App Router) | SSR / SSG / CSR 対応 |
| UI ライブラリ | React 19 | コンポーネントベース UI |
| 言語 | TypeScript 5.7 | 型安全な開発 |
| スタイリング | Tailwind CSS 4 | ユーティリティファースト CSS |
| 状態管理 | Zustand 5 | 軽量なグローバル状態管理 |
| アイコン | Lucide React | SVG アイコンセット |
| テスト | Vitest + Testing Library | コンポーネントテスト |
| E2E テスト | Playwright | ブラウザテスト |

#### ページ構成

```text
app/
  layout.tsx              # ルートレイアウト (AppShell)
  page.tsx                # ダッシュボード (ホーム)
  login/page.tsx          # ログインページ
  talk/page.tsx           # AI フリートーク
  talk/review/[id]/       # セッションレビュー
  speaking/flash/page.tsx # 瞬間英作文
  review/page.tsx         # FSRS 復習

components/
  chat/                   # チャット UI (ChatWindow, MessageBubble, FeedbackPanel)
  drill/                  # ドリル UI (FlashCard, ReviewCard)
  layout/                 # レイアウト (AppShell, Sidebar, BottomNav)

lib/
  api.ts                  # API クライアント
  stores/                 # Zustand ストア (auth-store, talk-store)
```

### Backend

| レイヤー | 技術 | 説明 |
| --- | --- | --- |
| フレームワーク | FastAPI 0.115 | 非同期 Web フレームワーク |
| ASGI サーバー | Uvicorn 0.34 | 高性能 Python サーバー |
| ORM | SQLAlchemy 2.0 (async) | 非同期 ORM |
| マイグレーション | Alembic 1.14 | DB スキーマ管理 |
| ログ | structlog 24.4 | 構造化ログ |
| 認証 | python-jose + passlib | JWT + bcrypt |
| 設定管理 | pydantic-settings 2.7 | 環境変数バリデーション |

#### ディレクトリ構成

```text
backend/app/
  main.py               # FastAPI アプリケーション (ルーター登録)
  config.py             # pydantic-settings 環境設定
  database.py           # SQLAlchemy async エンジン
  dependencies.py       # JWT 認証ディペンデンシー
  exceptions.py         # AppError 例外階層
  logging_config.py     # structlog 初期化

  routers/              # API ルーター (13個)
    health.py           #   /health
    auth.py             #   /api/auth/*
    talk.py             #   /api/talk/*
    speaking.py         #   /api/speaking/flash/*
    review.py           #   /api/review/*
    analytics.py        #   /api/analytics/dashboard
    listening.py        #   /api/listening/shadowing/*, tts
    pattern.py          #   /api/speaking/pattern/*
    realtime.py         #   /api/talk/realtime/*
    mogomogo.py         #   /api/listening/mogomogo/*
    analytics_router.py #   /api/analytics/advanced/*
    subscription.py     #   /api/subscription/*
    pronunciation.py    #   /api/speaking/pronunciation/*
    comprehension.py    #   /api/listening/comprehension/*

  services/             # ビジネスロジック (10個)
    claude_service.py   #   レガシー Claude API クライアント
    feedback_service.py #   文法・表現フィードバック生成
    flash_service.py    #   瞬間英作文生成・評価
    spaced_repetition.py #  FSRS アルゴリズム実装
    speech_service.py   #   Azure Speech Services 連携
    realtime_service.py #   リアルタイム音声処理
    shadowing_service.py #  シャドーイング素材生成
    pattern_service.py  #   パターン練習管理
    analytics_service.py #  高度な分析
    stripe_service.py   #   Stripe 決済
    mogomogo_service.py #   モゴモゴ英語
    pronunciation_service.py # 発音練習
    comprehension_service.py # リスニング理解度
    curriculum_service.py    # カリキュラム管理

  models/               # SQLAlchemy モデル (9テーブル)
  schemas/              # Pydantic スキーマ
  prompts/              # LLM プロンプトテンプレート
    conversation.py     #   会話システムプロンプト
    feedback.py         #   フィードバック生成プロンプト
    shadowing.py        #   シャドーイング素材生成
    comprehension.py    #   コンプリヘンション素材生成
    accent_profiles.py  #   マルチアクセント音声設定・特徴DB
    scenarios.py        #   100+ ビジネスシナリオDB
    lesson_structure.py #   3フェーズレッスン構造化プロンプト
  middleware/           # ミドルウェア (ログ, エラーハンドラ)
  llm/                  # マルチクラウド LLM 抽象化レイヤー
```

---

## LLM 抽象化レイヤー

### 設計パターン: Provider Pattern + Router + Resilience

```text
+------------------------------------------------------------------+
|  LLMService (シングルトン)                                         |
|  - claude_service のドロップインリプレース                           |
|  - chat(), chat_json(), get_usage_info()                          |
+----------------------------------+-------------------------------+
                                   |
                                   v
+------------------------------------------------------------------+
|  LLMRouter (ルーティング + フォールバック)                           |
|  - プライマリプロバイダーを優先実行                                  |
|  - サーキットブレーカーが開いたプロバイダーをスキップ                  |
|  - 全プロバイダー失敗時はエラー                                     |
+------+----------+----------+----------+----------+--------------+
       |          |          |          |          |
       v          v          v          v          v
+----------+ +----------+ +--------+ +--------+ +-------------+
| Azure AI | | Anthropic| | AWS    | | GCP    | | Local       |
| Foundry  | | Direct   | | Bedrock| | Vertex | | (Ollama)    |
+----------+ +----------+ +--------+ +--------+ +-------------+
   各プロバイダーは LLMProvider 抽象基底クラスを実装
```

### LLMProvider 抽象基底クラス

```text
LLMProvider (ABC)
  +-- name: str (プロバイダー名)
  +-- chat(): テキスト応答を取得
  +-- chat_json(): JSON 応答を取得・パース
  +-- get_usage_info(): トークン使用量付き応答
  +-- health_check(): 接続テスト
  +-- _parse_json_response(): JSON パースヘルパー
```

### レジリエンス機能

| 機能 | クラス | 説明 |
| --- | --- | --- |
| サーキットブレーカー | `CircuitBreaker` | 連続失敗でプロバイダーを一時停止 |
| リトライポリシー | `RetryPolicy` | Exponential backoff + jitter |
| レートリミッター | `RateLimiter` | Token bucket 方式 |

#### サーキットブレーカー状態遷移

```text
  [Closed] --(連続失敗 >= threshold)--> [Open]
     ^                                     |
     |                            (timeout 経過)
     |                                     |
     +----------(成功)------ [Half-Open] <--+
                              |
                        (失敗)
                              |
                              v
                           [Open]
```

### コスト管理

`llm/cost.py` でプロバイダー別のコスト推定を行います:

| プロバイダー | Sonnet (入力/出力 per 1M) | Haiku (入力/出力 per 1M) |
| --- | --- | --- |
| Azure AI Foundry | $3.00 / $15.00 | $0.80 / $4.00 |
| Anthropic Direct | $3.00 / $15.00 | $0.80 / $4.00 |
| AWS Bedrock | $3.00 / $15.00 | $0.80 / $4.00 |
| GCP Vertex AI | $3.00 / $15.00 | $0.80 / $4.00 |
| Local (Ollama) | $0.00 / $0.00 | $0.00 / $0.00 |

---

## データフロー

### AI フリートーク (メッセージ送信)

```text
[ユーザー] -> [Next.js] -> POST /api/talk/message
                               |
                               v
                        [FastAPI Router]
                               |
                               v
                     [Feedback Service]
                        |           |
                        v           v
               [LLM Service]  [LLM Service]
               (Sonnet: 応答)  (Haiku: 評価)
                        |           |
                        v           v
                  [会話応答テキスト] [フィードバックJSON]
                               |
                               v
                    [DB 保存 (Messages)]
                               |
                               v
                    [API レスポンス返却]
                               |
                               v
                    [Next.js 画面更新]
```

### 瞬間英作文 (回答チェック)

```text
[ユーザー回答] -> POST /api/speaking/flash/check
                      |
                      v
               [Flash Service]
                      |
                      v
               [LLM Service (Haiku)]
               評価プロンプト実行
                      |
                      v
               score >= 0.7?
               /            \
             Yes              No
              |                |
              v                v
         [結果返却]      [ReviewItem 作成]
                              |
                              v
                     [FSRS 初期パラメータ設定]
                              |
                              v
                         [結果返却]
```

### FSRS 復習

```text
[復習開始] -> GET /api/review/due
                  |
                  v
           [DB: next_review_at <= now のアイテム取得]
                  |
                  v
           [アイテム一覧返却]

[自己評価] -> POST /api/review/complete (rating: 1-4)
                  |
                  v
           [FSRS アルゴリズム]
           stability, difficulty 更新
           次回復習日 計算
                  |
                  v
           [DB 更新]
                  |
                  v
           [結果返却 (次回復習日, 新しい間隔)]
```

---

## データベース設計

### ER 図 (テキスト表現)

```text
+------------------+       +------------------------+
|     users        |       | conversation_sessions  |
+------------------+       +------------------------+
| id (PK, UUID)   |<------| user_id (FK)           |
| email (UNIQUE)   |   1:N | id (PK, UUID)          |
| name             |       | mode                   |
| hashed_password  |       | scenario_description   |
| target_level     |       | started_at             |
| subscription_plan|       | ended_at               |
| daily_goal_min   |       | duration_seconds       |
| native_language  |       | overall_score (JSONB)  |
| created_at       |       | api_tokens_used        |
| updated_at       |       +----------+-------------+
+--------+---------+                  |
         |                            | 1:N
         |                            v
         |                 +------------------------+
         |                 | conversation_messages  |
         |                 +------------------------+
         |                 | id (PK, UUID)          |
         |                 | session_id (FK)        |
         |                 | role                   |
         |                 | content                |
         |                 | feedback (JSONB)       |
         |                 | pronunciation_score    |
         |                 | response_time_ms       |
         |                 +------------------------+
         |
         | 1:N
         +----->+-----------------------+
         |      | review_items          |
         |      +-----------------------+
         |      | id (PK, UUID)         |
         |      | user_id (FK)          |
         |      | item_type             |
         |      | content (JSONB)       |
         |      | stability (FSRS)      |
         |      | difficulty (FSRS)     |
         |      | ease_factor           |
         |      | interval_days         |
         |      | repetitions           |
         |      | next_review_at        |
         |      +-----------------------+
         |
         | 1:N
         +----->+-----------------------+
         |      | daily_stats           |
         |      +-----------------------+
         |      | id (PK, UUID)         |
         |      | user_id (FK)          |
         |      | date (UNIQUE w/ user) |
         |      | practice_minutes      |
         |      | sessions_completed    |
         |      | reviews_completed     |
         |      | grammar_accuracy      |
         |      | weak_patterns (JSONB) |
         |      +-----------------------+
         |
         | 1:N
         +----->+-----------------------+
         |      | api_usage_log         |
         |      +-----------------------+
         |      | id (PK, UUID)         |
         |      | user_id (FK)          |
         |      | api_provider          |
         |      | model_name            |
         |      | input_tokens          |
         |      | output_tokens         |
         |      | estimated_cost_usd    |
         |      +-----------------------+
         |
         | 1:N
         +----->+-----------------------+
         |      | pattern_mastery       |
         |      +-----------------------+
         |      | id (PK, UUID)         |
         |      | user_id (FK)          |
         |      | pattern_id            |
         |      | pattern_category      |
         |      | skill_stage           |
         |      | practice_count        |
         |      | accuracy_rate         |
         |      +-----------------------+
         |
         | 1:N
         +----->+------------------------+
         |      | sound_pattern_mastery  |
         |      +------------------------+
         |      | id (PK, UUID)          |
         |      | user_id (FK)           |
         |      | pattern_type           |
         |      | pattern_text           |
         |      | ipa_notation           |
         |      | accuracy               |
         |      | practice_count         |
         |      +------------------------+
         |
         | 1:1
         +----->+-----------------------+
                | subscriptions         |
                +-----------------------+
                | id (PK, UUID)         |
                | user_id (FK, UNIQUE)  |
                | stripe_customer_id    |
                | stripe_subscription_id|
                | plan                  |
                | status                |
                | current_period_start  |
                | current_period_end    |
                | cancel_at_period_end  |
                +-----------------------+
```

### テーブル一覧

| テーブル | レコード規模 | 説明 |
| --- | --- | --- |
| users | 小 | ユーザー認証・プロフィール |
| conversation_sessions | 中 | 会話セッションメタデータ |
| conversation_messages | 大 | 会話メッセージ (最大容量テーブル) |
| review_items | 中 | FSRS 復習カード |
| daily_stats | 中 | 日次統計 (ユーザー x 日数) |
| api_usage_log | 大 | API 呼び出しログ |
| pattern_mastery | 小 | パターン習熟度 |
| sound_pattern_mastery | 小 | 音声パターン習熟度 |
| subscriptions | 小 | Stripe サブスクリプション |

---

## 認証フロー

```text
[ユーザー] ---(email + password)---> POST /api/auth/login
                                          |
                                          v
                                    [passlib.bcrypt]
                                    パスワード検証
                                          |
                                     成功 / 失敗
                                    /           \
                              [JWT 生成]    [401 エラー]
                              python-jose
                              HS256 署名
                                    |
                                    v
                              {access_token}
                                    |
                                    v
[クライアント] <--- Token 保存 (Zustand + localStorage)

--- 以降の API リクエスト ---

[クライアント] ---(Authorization: Bearer <token>)---> [FastAPI]
                                                          |
                                                          v
                                                   [dependencies.py]
                                                   get_current_user()
                                                   JWT デコード + 検証
                                                          |
                                                     有効 / 無効
                                                    /           \
                                              [User取得]    [401 エラー]
                                              DB参照
                                                    |
                                                    v
                                              [API 処理実行]
```

---

## セキュリティ設計

### 認証・認可

| 項目 | 実装 |
| --- | --- |
| パスワードハッシュ | bcrypt (passlib) |
| トークン形式 | JWT (HS256) |
| トークン有効期限 | 環境別 (8-24 時間) |
| セッション管理 | ステートレス (JWT) |

### 通信セキュリティ

| 項目 | 実装 |
| --- | --- |
| HTTPS | Container Apps マネージド SSL / Let's Encrypt |
| CORS | 許可オリジン制限 (`BACKEND_CORS_ORIGINS`) |
| リクエストID | UUID 自動付与 (トレーシング用) |

### データ保護

| 項目 | 実装 |
| --- | --- |
| シークレット管理 | 環境変数 + Cloud Key Vault |
| DB 暗号化 | PostgreSQL TLS + Azure 保存時暗号化 |
| API キー | `.env` ファイル (Git 管理外) |

### 入力バリデーション

| 項目 | 実装 |
| --- | --- |
| リクエスト検証 | Pydantic スキーマ (自動 422 エラー) |
| SQL インジェクション | SQLAlchemy ORM (パラメータバインド) |
| XSS | React の自動エスケープ + CSP ヘッダー |

### エラーハンドリング

| 項目 | 実装 |
| --- | --- |
| 例外階層 | `AppError` 基底クラス + 派生クラス |
| 統一フォーマット | `{"error": {"code": "...", "message": "...", "details": {}}}` |
| ログ | structlog で構造化ログ出力 (本番は JSON) |
| 内部エラー | 詳細を隠蔽 (INTERNAL_ERROR のみ返却) |

### レート制限

| 項目 | 実装 |
| --- | --- |
| LLM API | Token bucket 方式 (設定可能 RPM) |
| ユーザー API | `api_usage_monthly` でカウント |
| プラン制限 | Free プランの日次制限 |

---

関連ドキュメント:

- [技術仕様書](specification.md) -- 詳細な技術仕様
- [API リファレンス](api-reference.md) -- エンドポイント仕様
- [デプロイガイド](deployment-guide.md) -- デプロイ構成
