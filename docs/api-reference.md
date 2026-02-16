# FluentEdge AI API リファレンス

FluentEdge AI バックエンド API の全エンドポイント仕様書です。
12 機能・50 近いエンドポイントを網羅しています。

- **ベース URL (開発)**: `http://localhost:8000`
- **ベース URL (本番)**: `https://api.fluentedge.ai`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 目次

1. [認証方式](#認証方式)
2. [共通仕様](#共通仕様)
3. [Health -- ヘルスチェック](#health----ヘルスチェック)
4. [Auth -- 認証](#auth----認証)
5. [Talk -- AI 会話練習](#talk----ai-会話練習)
6. [Talk Realtime -- リアルタイム音声](#talk-realtime----リアルタイム音声)
7. [Speaking Flash -- 瞬間英作文](#speaking-flash----瞬間英作文)
8. [Speaking Pattern -- パターン練習](#speaking-pattern----パターン練習)
9. [Speaking Pronunciation -- 発音練習](#speaking-pronunciation----発音練習)
10. [Listening -- シャドーイング・TTS](#listening----シャドーイングtts)
11. [Listening Mogomogo -- モゴモゴ英語](#listening-mogomogo----モゴモゴ英語)
12. [Listening Comprehension -- 理解度テスト](#listening-comprehension----理解度テスト)
13. [Review -- FSRS 復習](#review----fsrs-復習)
14. [Analytics -- 統計・分析](#analytics----統計分析)
15. [Subscription -- サブスクリプション](#subscription----サブスクリプション)
16. [エラーレスポンス形式](#エラーレスポンス形式)

---

## 認証方式

FluentEdge API は **Bearer JWT** 認証を使用します。

### フロー

```text
1. POST /api/auth/register または POST /api/auth/login
   -> access_token を取得

2. 認証が必要なエンドポイントにヘッダーを付与:
   Authorization: Bearer <access_token>

3. トークン期限切れ時は再ログインが必要
```

### JWT ペイロード

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `sub` | string | ユーザー ID (UUID) |
| `exp` | number | 有効期限 (Unix timestamp) |
| `iat` | number | 発行日時 (Unix timestamp) |

### トークン有効期限

| 環境 | 有効期限 |
| --- | --- |
| dev | 24 時間 |
| staging | 12 時間 |
| production | 8 時間 |

---

## 共通仕様

### リクエストヘッダー

| ヘッダー | 値 | 必須 |
| --- | --- | --- |
| `Content-Type` | `application/json` | POST リクエスト時 |
| `Authorization` | `Bearer <token>` | 認証必須エンドポイント |

### 共通ステータスコード

| HTTP | 説明 |
| --- | --- |
| `200` | 成功 |
| `201` | リソース作成成功 |
| `400` | リクエスト不正 |
| `401` | 認証エラー |
| `403` | 認可エラー |
| `404` | リソース未検出 |
| `409` | 競合 (重複登録等) |
| `422` | バリデーションエラー |
| `429` | レート制限超過 |
| `500` | 内部サーバーエラー |
| `502` | LLM プロバイダーエラー |
| `504` | LLM タイムアウト |

---

## Health -- ヘルスチェック

### `GET /health`

サービスの稼働状態を確認します。認証不要。

**レスポンス** `200 OK`:

```json
{"status": "healthy", "service": "fluentedge-api"}
```

---

## Auth -- 認証

### `POST /api/auth/register`

新規ユーザー登録。認証不要。

**リクエスト**:

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `email` | EmailStr | Yes | 有効なメール形式 | メールアドレス |
| `password` | string | Yes | 8-128 文字 | パスワード |
| `name` | string | Yes | 1-255 文字 | 表示名 |

**レスポンス** `201 Created`:

```json
{"access_token": "eyJhbGci...", "token_type": "bearer"}
```

**エラー**: `409` メールアドレス重複、`422` バリデーションエラー

---

### `POST /api/auth/login`

ログイン。認証不要。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `email` | EmailStr | Yes | メールアドレス |
| `password` | string | Yes | パスワード |

**レスポンス** `200 OK`:

```json
{"access_token": "eyJhbGci...", "token_type": "bearer"}
```

**エラー**: `401` 認証失敗

---

### `GET /api/auth/me`

現在のログインユーザー情報を取得。認証必須。

**レスポンス** `200 OK`:

```json
{
  "id": "550b9f46-...",
  "email": "user@example.com",
  "name": "田中太郎",
  "target_level": "C1",
  "subscription_plan": "free",
  "daily_goal_minutes": 15,
  "native_language": "ja",
  "created_at": "2026-02-14T10:30:00Z"
}
```

---

## Talk -- AI 会話練習

### `POST /api/talk/start`

新しい会話セッションを開始。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `mode` | string | Yes | `meeting`, `presentation`, `negotiation`, `small_talk`, `interview` |
| `scenario_description` | string | No | カスタムシナリオの説明 |

**レスポンス** `200 OK`:

```json
{
  "id": "a1b2c3d4-...",
  "mode": "meeting",
  "scenario_description": "Weekly team standup",
  "started_at": "2026-02-14T10:30:00Z",
  "ended_at": null,
  "duration_seconds": null,
  "overall_score": null,
  "messages": [
    {
      "id": "b2c3d4e5-...",
      "role": "assistant",
      "content": "Good morning! Let's get started with our weekly standup.",
      "feedback": null,
      "created_at": "2026-02-14T10:30:01Z"
    }
  ]
}
```

---

### `POST /api/talk/message`

メッセージ送信。AI 応答とフィードバックを取得。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `session_id` | UUID | Yes | 対象セッション ID |
| `content` | string | Yes | メッセージ本文 |

**レスポンス** `200 OK`:

```json
{
  "id": "c3d4e5f6-...",
  "role": "assistant",
  "content": "That's great to hear! How many story points have you completed?",
  "feedback": {
    "grammar_errors": [
      {"original": "...", "corrected": "...", "explanation": "..."}
    ],
    "expression_upgrades": [
      {"original": "...", "upgraded": "...", "context": "..."}
    ],
    "pronunciation_notes": [],
    "positive_feedback": "Good use of present perfect continuous!",
    "vocabulary_level": "B2"
  },
  "created_at": "2026-02-14T10:30:15Z"
}
```

**エラー**: `404` セッション未検出

---

### `GET /api/talk/sessions`

セッション一覧を取得。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `offset` | int | 0 | スキップ数 |
| `limit` | int | 20 | 取得数 (1-100) |

**レスポンス** `200 OK`: セッション配列

---

### `GET /api/talk/sessions/{session_id}`

セッション詳細 (全メッセージ含む) を取得。認証必須。

**エラー**: `404` セッション未検出

---

## Talk Realtime -- リアルタイム音声

### `POST /api/talk/realtime/start`

リアルタイム音声セッションを開始。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `mode` | string | Yes | 会話モード |
| `voice_settings` | object | No | 音声設定 (速度、声種等) |

**レスポンス** `200 OK`: セッション ID と WebSocket 接続情報

---

### `WS /api/talk/realtime/ws/{session_id}`

WebSocket 音声ストリーム。バイナリ (音声チャンク) でリアルタイム通信。

---

## Speaking Flash -- 瞬間英作文

### `GET /api/speaking/flash`

フラッシュ翻訳エクササイズを動的生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `count` | int | 5 | 問題数 (1-20) |
| `focus` | string | null | 文法フォーカス |

**レスポンス** `200 OK`:

```json
[
  {
    "exercise_id": "flash_20260214_001",
    "japanese": "もし明日雨が降ったら、会議はオンラインで行いましょう。",
    "english_target": "If it rains tomorrow, let's hold the meeting online.",
    "acceptable_alternatives": ["If it rains tomorrow, let's have the meeting online."],
    "key_pattern": "first conditional",
    "difficulty": "B2",
    "time_limit_seconds": 15,
    "hints": ["条件節には現在形を使います"]
  }
]
```

---

### `POST /api/speaking/flash/check`

回答を評価。スコア 0.7 未満は自動的に復習登録。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `exercise_id` | string | Yes | エクササイズ ID |
| `user_answer` | string | Yes | ユーザー回答 |
| `target` | string | Yes | 正解英文 |

**レスポンス** `200 OK`:

```json
{
  "is_correct": false,
  "score": 0.6,
  "corrected": "If it rains tomorrow, let's hold the meeting online.",
  "explanation": "条件節では未来のことでも現在形を使います。",
  "review_item_created": true
}
```

---

## Speaking Pattern -- パターン練習

### `GET /api/speaking/pattern/categories`

パターンカテゴリ一覧を取得。認証必須。

**レスポンス** `200 OK`: カテゴリ配列 (meetings, presentations, negotiations 等)

---

### `GET /api/speaking/pattern/exercises`

パターン練習問題を取得。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `category` | string | Yes | カテゴリ ID |
| `count` | int | No | 問題数 |

---

### `POST /api/speaking/pattern/check`

パターン回答を評価。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `pattern_id` | string | Yes | パターン ID |
| `user_answer` | string | Yes | ユーザー回答 |
| `target` | string | Yes | 模範回答 |

---

### `GET /api/speaking/pattern/progress`

パターン習熟度の進捗を取得。認証必須。

**レスポンス** `200 OK`: カテゴリ別の習熟ステージ (understood → drilling → acquired)、正答率、練習回数

---

## Speaking Pronunciation -- 発音練習

### `GET /api/speaking/pronunciation/phonemes`

日本語話者向けの発音問題一覧。認証必須。

**レスポンス** `200 OK`: 音素リスト (L/R, TH, V/B 等の問題パターン)

---

### `GET /api/speaking/pronunciation/exercises`

発音練習問題を生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `phoneme` | string | No | 対象音素 |
| `count` | int | No | 問題数 |

---

### `POST /api/speaking/pronunciation/evaluate`

発音を評価 (Azure Speech Services 連携)。認証必須。

**リクエスト** (`multipart/form-data`):

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `audio` | file | Yes | 音声ファイル |
| `target_phoneme` | string | Yes | 対象音素 |
| `reference_text` | string | Yes | 参照テキスト |

---

### `GET /api/speaking/pronunciation/prosody/exercises`

プロソディ (韻律) 練習問題を取得。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `pattern` | string | No | 韻律パターン |
| `count` | int | No | 問題数 |

**レスポンス** `200 OK`: イントネーション・ストレス・リズムの練習問題

---

### `GET /api/speaking/pronunciation/progress`

音素別の発音進捗データを取得。認証必須。

**レスポンス** `200 OK`: 各音素の正答率、練習回数、習熟度

---

## Listening -- シャドーイング・TTS

### `GET /api/listening/shadowing/material`

シャドーイング素材を生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `level` | string | No | 難易度 (A2-C2) |
| `topic` | string | No | トピック |
| `speed` | float | No | 速度 (0.5-2.0) |

---

### `POST /api/listening/shadowing/evaluate`

シャドーイング音声を評価。認証必須。

**リクエスト** (`multipart/form-data`):

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `audio` | file | Yes | 音声ファイル |
| `reference_text` | string | Yes | 参照テキスト |
| `speed` | float | No | 再生速度 |

---

### `GET /api/listening/shadowing/history`

シャドーイング練習履歴を取得。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `offset` | int | 0 | スキップ数 |
| `limit` | int | 20 | 取得数 |

---

### `POST /api/listening/tts`

テキストを音声に変換 (TTS)。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `text` | string | Yes | 変換テキスト |
| `voice` | string | No | 声種 |
| `speed` | float | No | 速度 |

**レスポンス** `200 OK`: 音声データ (Base64)

---

## Listening Mogomogo -- モゴモゴ英語

### `GET /api/listening/mogomogo/patterns`

モゴモゴ英語の音声変化パターン一覧を取得。認証必須。

**レスポンス** `200 OK`: リンキング、リダクション等のパターン種別一覧

---

### `GET /api/listening/mogomogo/exercises`

モゴモゴ英語練習問題を生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `pattern_types` | string | No | パターン種別 (カンマ区切り) |
| `count` | int | No | 問題数 |

---

### `POST /api/listening/mogomogo/dictation/check`

ディクテーション回答を評価。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `exercise_id` | string | Yes | エクササイズ ID |
| `user_text` | string | Yes | ユーザーの書き取りテキスト |
| `original_text` | string | Yes | 元のテキスト |

---

### `GET /api/listening/mogomogo/progress`

モゴモゴ英語の学習進捗を取得。認証必須。

---

## Listening Comprehension -- 理解度テスト

### `GET /api/listening/comprehension/material`

リスニング理解度テスト用の素材を生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `topic` | string | No | トピック |
| `difficulty` | string | No | 難易度 |
| `duration_minutes` | int | No | 所要時間 (分) |

---

### `GET /api/listening/comprehension/material/questions`

素材に基づく質問を生成。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `text` | string | Yes | 素材テキスト |
| `count` | int | No | 質問数 |

---

### `POST /api/listening/comprehension/answer`

理解度テスト回答を送信・評価。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `question_id` | string | Yes | 質問 ID |
| `selected_answer` | string | Yes | 選択した回答 |

---

### `POST /api/listening/comprehension/summary`

要約を評価。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `material_id` | string | Yes | 素材 ID |
| `summary_text` | string | Yes | ユーザーの要約テキスト |

---

## Review -- FSRS 復習

### `GET /api/review/due`

今日の復習対象アイテムを取得。認証必須。

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `limit` | int | 20 | 取得数 (1-100) |

**レスポンス** `200 OK`:

```json
[
  {
    "id": "e5f6a7b8-...",
    "item_type": "flash_translation",
    "content": {
      "exercise_id": "flash_20260214_001",
      "target": "If it rains tomorrow, let's hold the meeting online.",
      "user_answer": "If it will rain tomorrow...",
      "corrected": "If it rains tomorrow...",
      "explanation": "条件節では現在形を使います。"
    },
    "next_review_at": "2026-02-15T10:30:00Z",
    "ease_factor": 2.5,
    "interval_days": 1,
    "repetitions": 0,
    "stability": 1.0,
    "difficulty": 0.3
  }
]
```

---

### `POST /api/review/complete`

復習結果を記録。FSRS アルゴリズムで次回復習日を計算。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `item_id` | UUID | Yes | 有効な ID | 復習アイテム ID |
| `rating` | int | Yes | 1-4 | 自己評価 |

**レーティング**:

| 値 | ラベル | 説明 |
| --- | --- | --- |
| 1 | Again | 完全に忘れていた |
| 2 | Hard | 思い出せたが困難 |
| 3 | Good | 適度な努力で想起 |
| 4 | Easy | 即座に想起 |

**レスポンス** `200 OK`:

```json
{
  "next_review_at": "2026-02-18T10:30:00Z",
  "new_interval_days": 4,
  "new_ease_factor": 2.6
}
```

**エラー**: `404` アイテム未検出

---

## Analytics -- 統計・分析

### `GET /api/analytics/dashboard`

ダッシュボード統計データを取得。認証必須。

**レスポンス** `200 OK`:

```json
{
  "streak_days": 12,
  "total_practice_minutes": 450,
  "total_sessions": 35,
  "total_reviews_completed": 128,
  "total_expressions_learned": 42,
  "avg_grammar_accuracy": 0.82,
  "avg_pronunciation_score": null,
  "recent_daily_stats": [
    {
      "date": "2026-02-14",
      "practice_minutes": 25,
      "sessions_completed": 2,
      "reviews_completed": 8,
      "new_expressions_learned": 3,
      "grammar_accuracy": 0.85,
      "pronunciation_avg_score": null
    }
  ],
  "pending_reviews": 5
}
```

---

### `GET /api/analytics/advanced/skills`

スキル別の詳細分析データを取得。認証必須。

**レスポンス** `200 OK`:

```json
{
  "skills": [
    {"skill": "grammar", "score": 0.82, "trend": "improving"},
    {"skill": "vocabulary", "score": 0.75, "trend": "stable"},
    {"skill": "pronunciation", "score": 0.68, "trend": "improving"},
    {"skill": "listening", "score": 0.71, "trend": "declining"},
    {"skill": "fluency", "score": 0.79, "trend": "improving"}
  ]
}
```

---

### `GET /api/analytics/advanced/weekly-report`

週次レポートを生成。認証必須。

**レスポンス** `200 OK`: 今週の学習サマリー、スキル変化、おすすめアクション

---

### `GET /api/analytics/advanced/monthly-report`

月次レポートを生成。認証必須。

**レスポンス** `200 OK`: 月間の学習統計、目標達成度、スキル成長グラフデータ

---

### `GET /api/analytics/advanced/pronunciation-progress`

発音の音素別進捗データを取得。認証必須。

**レスポンス** `200 OK`: 各音素 (L/R, TH, V/B 等) の正答率・練習回数

---

### `GET /api/analytics/advanced/recommendations`

AI による学習レコメンデーションを取得。認証必須。

**レスポンス** `200 OK`:

```json
{
  "recommendations": [
    {
      "type": "focus_skill",
      "title": "リスニング強化",
      "description": "リスニングスコアが低下傾向です。シャドーイングを増やしましょう。",
      "priority": "high"
    }
  ]
}
```

---

### `GET /api/analytics/advanced/daily-menu`

今日の最適化された学習メニューを取得。認証必須。

**レスポンス** `200 OK`: ユーザーの弱点・進捗に基づく推奨学習項目リスト

---

### `GET /api/analytics/advanced/focus-areas`

ベイジアン知識モデルに基づくフォーカスエリアを取得。認証必須。

**レスポンス** `200 OK`: 重点学習すべきスキル・パターンの一覧

---

## Subscription -- サブスクリプション

### `GET /api/subscription/plans`

利用可能なプラン一覧を取得。認証必須。

**レスポンス** `200 OK`:

```json
[
  {"id": "free", "name": "Free", "price_monthly": 0, "features": ["..."]},
  {"id": "standard", "name": "Standard", "price_monthly": 980, "features": ["..."]},
  {"id": "premium", "name": "Premium", "price_monthly": 1980, "features": ["..."]}
]
```

---

### `GET /api/subscription/current`

現在のサブスクリプション情報を取得。認証必須。

**レスポンス** `200 OK`:

```json
{
  "plan": "standard",
  "status": "active",
  "current_period_start": "2026-02-01T00:00:00Z",
  "current_period_end": "2026-03-01T00:00:00Z",
  "cancel_at_period_end": false
}
```

---

### `POST /api/subscription/checkout`

Stripe チェックアウトセッションを作成。認証必須。

**リクエスト**:

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `plan` | string | Yes | プラン ID (`standard`, `premium`) |

**レスポンス** `200 OK`:

```json
{"checkout_url": "https://checkout.stripe.com/..."}
```

---

### `POST /api/subscription/cancel`

サブスクリプションを解約 (期間終了時に停止)。認証必須。

**レスポンス** `200 OK`:

```json
{"status": "cancelled", "cancel_at_period_end": true}
```

---

### `POST /api/subscription/webhook`

Stripe Webhook。認証不要 (Stripe 署名で検証)。

Stripe から以下のイベントを処理:
- `checkout.session.completed` -- 決済完了
- `customer.subscription.updated` -- プラン変更
- `customer.subscription.deleted` -- 解約完了
- `invoice.payment_failed` -- 決済失敗

---

## エラーレスポンス形式

### AppError 統一フォーマット

全エンドポイントのエラーは以下の統一フォーマットで返されます:

```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "認証に失敗しました",
    "details": {}
  }
}
```

### エラーコード一覧

| code | HTTP | 説明 |
| --- | --- | --- |
| `AUTHENTICATION_ERROR` | 401 | 認証失敗 |
| `AUTHORIZATION_ERROR` | 403 | 権限不足 |
| `NOT_FOUND` | 404 | リソース未検出 |
| `VALIDATION_ERROR` | 422 | バリデーション失敗 |
| `RATE_LIMIT_ERROR` | 429 | レート制限超過 |
| `INTERNAL_ERROR` | 500 | 内部サーバーエラー |
| `LLM_PROVIDER_ERROR` | 502 | LLM プロバイダーエラー |
| `LLM_TIMEOUT` | 504 | LLM タイムアウト |
| `LLM_RATE_LIMIT` | 429 | LLM レート制限 |
| `EXTERNAL_SERVICE_ERROR` | 502 | 外部サービスエラー (Stripe, Azure Speech 等) |

### バリデーションエラーの詳細形式 (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "リクエストのバリデーションに失敗しました",
    "details": {
      "errors": [
        {
          "type": "string_too_short",
          "loc": ["body", "password"],
          "msg": "String should have at least 8 characters",
          "input": "short",
          "ctx": {"min_length": 8}
        }
      ]
    }
  }
}
```

---

## エンドポイント一覧 (サマリー)

| メソッド | パス | 認証 | 説明 |
| --- | --- | --- | --- |
| `GET` | `/health` | No | ヘルスチェック |
| `POST` | `/api/auth/register` | No | ユーザー登録 |
| `POST` | `/api/auth/login` | No | ログイン |
| `GET` | `/api/auth/me` | Yes | ユーザー情報取得 |
| `POST` | `/api/talk/start` | Yes | 会話セッション開始 |
| `POST` | `/api/talk/message` | Yes | メッセージ送信 |
| `GET` | `/api/talk/sessions` | Yes | セッション一覧 |
| `GET` | `/api/talk/sessions/{id}` | Yes | セッション詳細 |
| `POST` | `/api/talk/realtime/start` | Yes | リアルタイム音声開始 |
| `WS` | `/api/talk/realtime/ws/{id}` | Yes | WebSocket 音声 |
| `GET` | `/api/speaking/flash` | Yes | 瞬間英作文取得 |
| `POST` | `/api/speaking/flash/check` | Yes | 回答チェック |
| `GET` | `/api/speaking/pattern/categories` | Yes | パターンカテゴリ |
| `GET` | `/api/speaking/pattern/exercises` | Yes | パターン問題 |
| `POST` | `/api/speaking/pattern/check` | Yes | パターン評価 |
| `GET` | `/api/speaking/pattern/progress` | Yes | パターン習熟度 |
| `GET` | `/api/speaking/pronunciation/phonemes` | Yes | 音素一覧 |
| `GET` | `/api/speaking/pronunciation/exercises` | Yes | 発音問題 |
| `POST` | `/api/speaking/pronunciation/evaluate` | Yes | 発音評価 |
| `GET` | `/api/speaking/pronunciation/prosody/exercises` | Yes | プロソディ問題 |
| `GET` | `/api/speaking/pronunciation/progress` | Yes | 発音進捗 |
| `GET` | `/api/listening/shadowing/material` | Yes | シャドーイング素材 |
| `POST` | `/api/listening/shadowing/evaluate` | Yes | シャドーイング評価 |
| `GET` | `/api/listening/shadowing/history` | Yes | シャドーイング履歴 |
| `POST` | `/api/listening/tts` | Yes | テキスト音声変換 |
| `GET` | `/api/listening/mogomogo/patterns` | Yes | モゴモゴパターン一覧 |
| `GET` | `/api/listening/mogomogo/exercises` | Yes | モゴモゴ問題生成 |
| `POST` | `/api/listening/mogomogo/dictation/check` | Yes | ディクテーション評価 |
| `GET` | `/api/listening/mogomogo/progress` | Yes | モゴモゴ進捗 |
| `GET` | `/api/listening/comprehension/material` | Yes | 理解度テスト素材 |
| `GET` | `/api/listening/comprehension/material/questions` | Yes | 理解度質問生成 |
| `POST` | `/api/listening/comprehension/answer` | Yes | 理解度回答 |
| `POST` | `/api/listening/comprehension/summary` | Yes | 要約評価 |
| `GET` | `/api/review/due` | Yes | 復習対象取得 |
| `POST` | `/api/review/complete` | Yes | 復習完了 |
| `GET` | `/api/analytics/dashboard` | Yes | ダッシュボード統計 |
| `GET` | `/api/analytics/advanced/skills` | Yes | スキル分析 |
| `GET` | `/api/analytics/advanced/weekly-report` | Yes | 週次レポート |
| `GET` | `/api/analytics/advanced/monthly-report` | Yes | 月次レポート |
| `GET` | `/api/analytics/advanced/pronunciation-progress` | Yes | 発音進捗分析 |
| `GET` | `/api/analytics/advanced/recommendations` | Yes | 学習レコメンド |
| `GET` | `/api/analytics/advanced/daily-menu` | Yes | デイリーメニュー |
| `GET` | `/api/analytics/advanced/focus-areas` | Yes | フォーカスエリア |
| `GET` | `/api/subscription/plans` | Yes | プラン一覧 |
| `GET` | `/api/subscription/current` | Yes | 現在のプラン |
| `POST` | `/api/subscription/checkout` | Yes | チェックアウト |
| `POST` | `/api/subscription/cancel` | Yes | 解約 |
| `POST` | `/api/subscription/webhook` | No | Stripe Webhook |

---

関連ドキュメント:

- [セットアップガイド](setup-guide.md) -- ローカル環境構築
- [アーキテクチャ設計書](architecture.md) -- システム構成
- [技術仕様書](specification.md) -- 詳細仕様
