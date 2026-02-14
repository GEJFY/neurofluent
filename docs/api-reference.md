# API リファレンス

FluentEdge AI バックエンド API の全エンドポイント仕様書です。

- **ベース URL (開発)**: `http://localhost:8000`
- **ベース URL (本番)**: `https://api.fluentedge.ai`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 目次

1. [認証フロー](#認証フロー)
2. [共通仕様](#共通仕様)
3. [Health -- ヘルスチェック](#health----ヘルスチェック)
4. [Auth -- 認証 API](#auth----認証-api)
5. [Talk -- 会話練習 API](#talk----会話練習-api)
6. [Speaking -- 瞬間英作文 API](#speaking----瞬間英作文-api)
7. [Review -- 復習 API](#review----復習-api)
8. [Analytics -- 統計 API](#analytics----統計-api)
9. [型定義テーブル](#型定義テーブル)
10. [WebSocket / SSE (将来計画)](#websocket--sse-将来計画)

---

## 認証フロー

FluentEdge API は **Bearer JWT** 認証を使用します。

### フロー概要

```text
1. POST /api/auth/register  →  ユーザー登録  →  access_token を取得
   または
   POST /api/auth/login     →  ログイン      →  access_token を取得

2. 認証が必要なエンドポイントには Bearer トークンを付与:
   Authorization: Bearer <access_token>

3. トークンの有効期限が切れたら再ログインが必要
```

### 認証ヘッダー

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### JWT ペイロード

```json
{
  "sub": "ユーザー UUID",
  "exp": 1700000000,
  "iat": 1699913600
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `sub` | string | ユーザー ID (UUID) |
| `exp` | number | 有効期限 (Unix timestamp) |
| `iat` | number | 発行日時 (Unix timestamp) |

### トークンの有効期限 (環境別)

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
| `Authorization` | `Bearer <token>` | 認証が必要なエンドポイント |

### エラーレスポンス形式

全 API エンドポイントは、エラー時に以下の統一フォーマットでレスポンスを返します:

```json
{
  "detail": "エラーメッセージ"
}
```

### バリデーションエラーの詳細形式 (422)

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

### 共通エラーコード

| HTTP ステータス | コード | 説明 | 発生条件 |
| --- | --- | --- | --- |
| `400` | Bad Request | リクエスト不正 | バリデーションエラー、不正な JSON |
| `401` | Unauthorized | 認証エラー | トークン未送信、トークン失効 |
| `404` | Not Found | リソース未発見 | 指定された ID のリソースが存在しない |
| `409` | Conflict | 競合 | メールアドレスの重複登録 |
| `422` | Unprocessable Entity | バリデーションエラー | Pydantic バリデーション失敗 |
| `429` | Too Many Requests | レート制限超過 | API 使用量上限到達 |
| `500` | Internal Server Error | サーバーエラー | 予期しないエラー |

---

## Health -- ヘルスチェック

### `GET /health`

サービスの稼働状態を確認するエンドポイントです。

**認証**: 不要

**レスポンス**: `200 OK`

```json
{
  "status": "healthy",
  "service": "fluentedge-api"
}
```

**curl**:

```bash
curl http://localhost:8000/health
```

---

## Auth -- 認証 API

### `POST /api/auth/register`

新規ユーザーを登録し、JWT アクセストークンを発行します。

**認証**: 不要

**リクエストボディ**:

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "田中太郎"
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `email` | EmailStr | Yes | 有効なメールアドレス形式 | メールアドレス |
| `password` | string | Yes | 8〜128 文字 | パスワード |
| `name` | string | Yes | 1〜255 文字 | 表示名 |

**レスポンス**: `201 Created`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `409` | メールアドレスが既に登録済み | `{"detail": "このメールアドレスは既に登録されています"}` |
| `422` | バリデーションエラー | バリデーション詳細 (パスワード短すぎ等) |

**curl**:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "田中太郎"
  }'
```

---

### `POST /api/auth/login`

メールアドレスとパスワードで認証し、JWT アクセストークンを発行します。

**認証**: 不要

**リクエストボディ**:

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `email` | EmailStr | Yes | メールアドレス |
| `password` | string | Yes | パスワード |

**レスポンス**: `200 OK`

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `401` | メールアドレスまたはパスワードが不正 | `{"detail": "メールアドレスまたはパスワードが正しくありません"}` |

**curl**:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

---

### `GET /api/auth/me`

現在のログインユーザー情報を取得します。

**認証**: 必須 (Bearer JWT)

**レスポンス**: `200 OK`

```json
{
  "id": "550b9f46-1234-5678-9abc-1234567890ab",
  "email": "user@example.com",
  "name": "田中太郎",
  "target_level": "C1",
  "subscription_plan": "free",
  "daily_goal_minutes": 15,
  "native_language": "ja",
  "created_at": "2026-02-14T10:30:00Z"
}
```

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `401` | トークンが無効または期限切れ | `{"detail": "認証に失敗しました"}` |

**curl**:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Talk -- 会話練習 API

### `POST /api/talk/start`

新しい会話セッションを開始し、AI の初回メッセージを生成します。

**認証**: 必須 (Bearer JWT)

**リクエストボディ**:

```json
{
  "mode": "meeting",
  "scenario_description": "Weekly team standup meeting to discuss project progress"
}
```

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `mode` | string | Yes | 会話モード: `meeting`, `presentation`, `negotiation`, `small_talk`, `interview` |
| `scenario_description` | string / null | No | カスタムシナリオの詳細説明 |

**レスポンス**: `200 OK`

```json
{
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "mode": "meeting",
  "scenario_description": "Weekly team standup meeting to discuss project progress",
  "started_at": "2026-02-14T10:30:00Z",
  "ended_at": null,
  "duration_seconds": null,
  "overall_score": null,
  "messages": [
    {
      "id": "b2c3d4e5-6789-0abc-def1-234567890abc",
      "role": "assistant",
      "content": "Good morning! Let's get started with our weekly standup. Could you give us an update on your current project?",
      "feedback": null,
      "created_at": "2026-02-14T10:30:01Z"
    }
  ]
}
```

**curl**:

```bash
curl -X POST http://localhost:8000/api/talk/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "mode": "meeting",
    "scenario_description": "Weekly team standup meeting"
  }'
```

---

### `POST /api/talk/message`

ユーザーメッセージを送信し、AI の応答とリアルタイムフィードバックを取得します。

**認証**: 必須 (Bearer JWT)

**リクエストボディ**:

```json
{
  "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "content": "I have been working on the new feature since last week. The progress is going smooth."
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `session_id` | UUID | Yes | 有効なセッション ID | 対象の会話セッション |
| `content` | string | Yes | 1 文字以上 | ユーザーのメッセージ本文 |

**レスポンス**: `200 OK`

```json
{
  "id": "c3d4e5f6-7890-abcd-ef12-34567890abcd",
  "role": "assistant",
  "content": "That's great to hear! How many story points have you completed so far?",
  "feedback": {
    "grammar_errors": [
      {
        "original": "The progress is going smooth",
        "corrected": "The progress is going smoothly",
        "explanation": "'smooth' は形容詞です。動詞 'going' を修飾するには副詞 'smoothly' を使います。"
      }
    ],
    "expression_upgrades": [
      {
        "original": "I have been working on the new feature",
        "upgraded": "I've been making progress on the new feature",
        "context": "ビジネスミーティングでは、進捗を強調する表現がより適切です。"
      }
    ],
    "pronunciation_notes": [],
    "positive_feedback": "時制の使い方 (現在完了進行形) が正確で、自然な会話の流れになっています。",
    "vocabulary_level": "B2"
  },
  "created_at": "2026-02-14T10:30:15Z"
}
```

**フィードバック (feedback) の構造**:

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `grammar_errors` | array | 文法エラーのリスト (`original`, `corrected`, `explanation`) |
| `expression_upgrades` | array | より自然な表現への改善提案 (`original`, `upgraded`, `context`) |
| `pronunciation_notes` | array of string | 発音に関するメモ |
| `positive_feedback` | string | 良かった点のフィードバック |
| `vocabulary_level` | string | 使用語彙の推定 CEFR レベル (`A2`, `B1`, `B2`, `C1`, `C2`) |

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `404` | セッションが見つからない | `{"detail": "セッションが見つかりません"}` |

**curl**:

```bash
curl -X POST http://localhost:8000/api/talk/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "content": "I have been working on the new feature since last week."
  }'
```

---

### `GET /api/talk/sessions`

ユーザーの会話セッション一覧を取得します (ページネーション対応)。

**認証**: 必須 (Bearer JWT)

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `offset` | int | 0 | >= 0 | スキップするレコード数 |
| `limit` | int | 20 | 1〜100 | 取得するレコード数 |

**レスポンス**: `200 OK`

```json
[
  {
    "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "mode": "meeting",
    "started_at": "2026-02-14T10:30:00Z",
    "duration_seconds": 1200
  },
  {
    "id": "b2c3d4e5-6789-0abc-def1-234567890abc",
    "mode": "small_talk",
    "started_at": "2026-02-13T09:00:00Z",
    "duration_seconds": 600
  }
]
```

**curl**:

```bash
curl "http://localhost:8000/api/talk/sessions?offset=0&limit=10" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### `GET /api/talk/sessions/{session_id}`

特定のセッション詳細 (全メッセージ含む) を取得します。

**認証**: 必須 (Bearer JWT)

**パスパラメータ**:

| パラメータ | 型 | 説明 |
| --- | --- | --- |
| `session_id` | UUID | 取得するセッションの ID |

**レスポンス**: `200 OK`

```json
{
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "mode": "meeting",
  "scenario_description": "Weekly team standup meeting",
  "started_at": "2026-02-14T10:30:00Z",
  "ended_at": "2026-02-14T10:50:00Z",
  "duration_seconds": 1200,
  "overall_score": {
    "grammar": 0.85,
    "fluency": 0.78,
    "vocabulary": 0.90,
    "overall": 0.84
  },
  "messages": [
    {
      "id": "b2c3d4e5-6789-0abc-def1-234567890abc",
      "role": "assistant",
      "content": "Good morning! Let's get started with our weekly standup.",
      "feedback": null,
      "created_at": "2026-02-14T10:30:01Z"
    },
    {
      "id": "c3d4e5f6-7890-abcd-ef12-34567890abcd",
      "role": "user",
      "content": "I have been working on the new feature.",
      "feedback": {
        "grammar_errors": [],
        "expression_upgrades": [],
        "pronunciation_notes": [],
        "positive_feedback": "Good use of present perfect continuous!",
        "vocabulary_level": "B2"
      },
      "created_at": "2026-02-14T10:30:15Z"
    }
  ]
}
```

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `404` | セッションが見つからない | `{"detail": "セッションが見つかりません"}` |

**curl**:

```bash
curl "http://localhost:8000/api/talk/sessions/a1b2c3d4-5678-90ab-cdef-1234567890ab" \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Speaking -- 瞬間英作文 API

### `GET /api/speaking/flash`

ユーザーのレベルと弱点に基づいてフラッシュ翻訳エクササイズを動的生成します。

**認証**: 必須 (Bearer JWT)

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `count` | int | 5 | 1〜20 | 生成するエクササイズ数 |
| `focus` | string / null | null | -- | フォーカスする文法・表現カテゴリ |

**レスポンス**: `200 OK`

```json
[
  {
    "exercise_id": "flash_20260214_001",
    "japanese": "もし明日雨が降ったら、会議はオンラインで行いましょう。",
    "english_target": "If it rains tomorrow, let's hold the meeting online.",
    "acceptable_alternatives": [
      "If it rains tomorrow, let's have the meeting online.",
      "Should it rain tomorrow, let's conduct the meeting online."
    ],
    "key_pattern": "first conditional (if + present simple, let's + infinitive)",
    "difficulty": "B2",
    "time_limit_seconds": 15,
    "hints": [
      "条件節には未来形ではなく現在形を使います",
      "\"let's\" を使って提案を表現します"
    ]
  },
  {
    "exercise_id": "flash_20260214_002",
    "japanese": "そのプロジェクトにもっと時間を費やしていたら、結果は違っていたでしょう。",
    "english_target": "If we had spent more time on the project, the results would have been different.",
    "acceptable_alternatives": [
      "Had we spent more time on the project, the results would have been different."
    ],
    "key_pattern": "third conditional (if + past perfect, would have + past participle)",
    "difficulty": "C1",
    "time_limit_seconds": 20,
    "hints": [
      "過去の仮定には過去完了形を使います",
      "帰結節には would have + 過去分詞"
    ]
  }
]
```

**レスポンスフィールド**:

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `exercise_id` | string | エクササイズの一意識別子 |
| `japanese` | string | 翻訳元の日本語文 |
| `english_target` | string | 目標となる英訳 |
| `acceptable_alternatives` | array of string | 許容される代替英訳 |
| `key_pattern` | string | 注目する文法・表現パターン |
| `difficulty` | string | 難易度レベル (`A2`, `B1`, `B2`, `C1`, `C2`) |
| `time_limit_seconds` | int | 制限時間 (秒) |
| `hints` | array of string | ヒントのリスト |

**curl**:

```bash
# デフォルト (5 問)
curl "http://localhost:8000/api/speaking/flash" \
  -H "Authorization: Bearer <TOKEN>"

# 問題数指定
curl "http://localhost:8000/api/speaking/flash?count=10" \
  -H "Authorization: Bearer <TOKEN>"

# フォーカス指定
curl "http://localhost:8000/api/speaking/flash?count=5&focus=conditionals" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### `POST /api/speaking/flash/check`

ユーザーの回答を評価し、スコアとフィードバックを返します。スコアが 0.7 未満の場合、自動的に復習アイテムが作成されます。

**認証**: 必須 (Bearer JWT)

**リクエストボディ**:

```json
{
  "exercise_id": "flash_20260214_001",
  "user_answer": "If it will rain tomorrow, let's do the meeting online.",
  "target": "If it rains tomorrow, let's hold the meeting online."
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `exercise_id` | string | Yes | -- | 対象エクササイズの ID |
| `user_answer` | string | Yes | 1 文字以上 | ユーザーの回答 |
| `target` | string | Yes | 1 文字以上 | 正解の英文 |

**レスポンス**: `200 OK`

```json
{
  "is_correct": false,
  "score": 0.6,
  "corrected": "If it rains tomorrow, let's hold the meeting online.",
  "explanation": "条件節 (if 節) で未来のことを表す場合でも、現在形を使います。'will rain' ではなく 'rains' が正しい形です。また、'do the meeting' よりも 'hold the meeting' の方がビジネス英語として自然です。",
  "review_item_created": true
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `is_correct` | bool | 正解かどうか |
| `score` | float | 正答スコア (0.0〜1.0) |
| `corrected` | string | 修正後の正しい英文 |
| `explanation` | string | 解説・フィードバック |
| `review_item_created` | bool | 復習アイテムが作成されたか (score < 0.7 で true) |

**curl**:

```bash
curl -X POST http://localhost:8000/api/speaking/flash/check \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "exercise_id": "flash_20260214_001",
    "user_answer": "If it will rain tomorrow, let us do the meeting online.",
    "target": "If it rains tomorrow, let'\''s hold the meeting online."
  }'
```

---

## Review -- 復習 API

### `GET /api/review/due`

今日の復習対象アイテムを取得します。`next_review_at` が現在時刻以前のアイテムと、まだ一度も復習されていないアイテムが返されます。

**認証**: 必須 (Bearer JWT)

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `limit` | int | 20 | 1〜100 | 取得するアイテム数 |

**レスポンス**: `200 OK`

```json
[
  {
    "id": "e5f6a7b8-9012-cdef-0123-456789abcdef",
    "item_type": "flash_translation",
    "content": {
      "exercise_id": "flash_20260214_001",
      "target": "If it rains tomorrow, let's hold the meeting online.",
      "user_answer": "If it will rain tomorrow, let's do the meeting online.",
      "corrected": "If it rains tomorrow, let's hold the meeting online.",
      "explanation": "条件節では未来のことでも現在形を使います。"
    },
    "next_review_at": "2026-02-15T10:30:00Z",
    "ease_factor": 2.5,
    "interval_days": 1,
    "repetitions": 0
  }
]
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | 復習アイテムの一意識別子 |
| `item_type` | string | アイテムの種類 (`flash_translation`, `grammar_error`, `expression`) |
| `content` | object | アイテムの内容 (種類によって構造が異なる) |
| `next_review_at` | datetime / null | 次回復習予定日時 |
| `ease_factor` | float | 容易さ係数 (初期値 2.5) |
| `interval_days` | int | 現在の復習間隔 (日数) |
| `repetitions` | int | 復習回数 |

**curl**:

```bash
curl "http://localhost:8000/api/review/due?limit=20" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### `POST /api/review/complete`

復習結果を記録し、FSRS アルゴリズムで次回復習日を計算します。

**認証**: 必須 (Bearer JWT)

**リクエストボディ**:

```json
{
  "item_id": "e5f6a7b8-9012-cdef-0123-456789abcdef",
  "rating": 3
}
```

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `item_id` | UUID | Yes | 有効な復習アイテム ID | 対象の復習アイテム |
| `rating` | int | Yes | 1〜4 | ユーザーの自己評価 |

**レーティングの意味**:

| 値 | ラベル | 説明 | FSRS への影響 |
| --- | --- | --- | --- |
| 1 | Again (もう一度) | 完全に忘れていた | 安定度大幅低下、短間隔で再復習 |
| 2 | Hard (難しい) | 思い出せたが困難だった | 安定度微増、ペナルティ係数適用 |
| 3 | Good (良い) | 適度な努力で思い出せた | 安定度標準増加 |
| 4 | Easy (簡単) | 即座に思い出せた | 安定度大幅増加、ボーナス係数適用 |

**レスポンス**: `200 OK`

```json
{
  "next_review_at": "2026-02-18T10:30:00Z",
  "new_interval_days": 4,
  "new_ease_factor": 2.6
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `next_review_at` | datetime | 次回の復習予定日時 |
| `new_interval_days` | int | 新しい復習間隔 (日数) |
| `new_ease_factor` | float | 更新後の容易さ係数 |

**エラーレスポンス**:

| ステータス | 条件 | レスポンス |
| --- | --- | --- |
| `404` | 復習アイテムが見つからない | `{"detail": "復習アイテムが見つかりません"}` |

**curl**:

```bash
curl -X POST http://localhost:8000/api/review/complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "item_id": "e5f6a7b8-9012-cdef-0123-456789abcdef",
    "rating": 3
  }'
```

---

## Analytics -- 統計 API

### `GET /api/analytics/dashboard`

ユーザーの学習ダッシュボードデータを取得します。

**認証**: 必須 (Bearer JWT)

**レスポンス**: `200 OK`

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
    },
    {
      "date": "2026-02-13",
      "practice_minutes": 30,
      "sessions_completed": 3,
      "reviews_completed": 12,
      "new_expressions_learned": 5,
      "grammar_accuracy": 0.80,
      "pronunciation_avg_score": null
    }
  ],
  "pending_reviews": 5
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `streak_days` | int | 連続学習日数 (今日を含む) |
| `total_practice_minutes` | int | 累計学習時間 (分) |
| `total_sessions` | int | 累計セッション数 |
| `total_reviews_completed` | int | 累計復習完了数 |
| `total_expressions_learned` | int | 累計学習表現数 |
| `avg_grammar_accuracy` | float / null | 平均文法正確性 (0.0〜1.0) |
| `avg_pronunciation_score` | float / null | 平均発音スコア (0.0〜1.0、将来機能) |
| `recent_daily_stats` | array | 直近 7 日間の日次統計 |
| `pending_reviews` | int | 未復習アイテム数 |

**日次統計 (recent_daily_stats) の構造**:

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `date` | string | 日付 (YYYY-MM-DD) |
| `practice_minutes` | int | その日の学習時間 (分) |
| `sessions_completed` | int | 完了したセッション数 |
| `reviews_completed` | int | 完了した復習数 |
| `new_expressions_learned` | int | 新しく学習した表現数 |
| `grammar_accuracy` | float / null | その日の文法正確性 |
| `pronunciation_avg_score` | float / null | その日の平均発音スコア |

**curl**:

```bash
curl http://localhost:8000/api/analytics/dashboard \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 型定義テーブル

### リクエスト型

#### UserCreate

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `email` | EmailStr | Yes | 有効なメールアドレス形式 | メールアドレス |
| `password` | string | Yes | min: 8, max: 128 | パスワード |
| `name` | string | Yes | min: 1, max: 255 | 表示名 |

#### UserLogin

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `email` | EmailStr | Yes | メールアドレス |
| `password` | string | Yes | パスワード |

#### TalkStartRequest

| フィールド | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `mode` | string | Yes | 会話モード (`meeting`, `presentation`, `negotiation`, `small_talk`, `interview`) |
| `scenario_description` | string / null | No | カスタムシナリオの説明 |

#### TalkMessageRequest

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `session_id` | UUID | Yes | 有効なセッション ID | 対象セッション |
| `content` | string | Yes | min: 1 | メッセージ本文 |

#### FlashCheckRequest

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `exercise_id` | string | Yes | -- | エクササイズ ID |
| `user_answer` | string | Yes | min: 1 | ユーザーの回答 |
| `target` | string | Yes | min: 1 | 正解の英文 |

#### ReviewCompleteRequest

| フィールド | 型 | 必須 | 制約 | 説明 |
| --- | --- | --- | --- | --- |
| `item_id` | UUID | Yes | 有効な復習アイテム ID | 対象アイテム |
| `rating` | int | Yes | 1〜4 | 自己評価 (1=Again, 2=Hard, 3=Good, 4=Easy) |

### レスポンス型

#### Token

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `access_token` | string | JWT アクセストークン |
| `token_type` | string | トークンタイプ (常に `"bearer"`) |

#### UserResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | ユーザー ID |
| `email` | string | メールアドレス |
| `name` | string | 表示名 |
| `target_level` | string | 目標 CEFR レベル (デフォルト: `"C1"`) |
| `subscription_plan` | string | プラン (`"free"`, `"pro"`, `"enterprise"`) |
| `daily_goal_minutes` | int | 日次目標学習時間 (分、デフォルト: 15) |
| `native_language` | string | 母国語 (デフォルト: `"ja"`) |
| `created_at` | datetime | アカウント作成日時 |

#### SessionResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | セッション ID |
| `mode` | string | 会話モード |
| `scenario_description` | string / null | シナリオ説明 |
| `started_at` | datetime | セッション開始日時 |
| `ended_at` | datetime / null | セッション終了日時 |
| `duration_seconds` | int / null | セッション時間 (秒) |
| `overall_score` | object / null | 総合スコア |
| `messages` | array of TalkMessageResponse | メッセージ一覧 |

#### SessionListResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | セッション ID |
| `mode` | string | 会話モード |
| `started_at` | datetime | セッション開始日時 |
| `duration_seconds` | int / null | セッション時間 (秒) |

#### TalkMessageResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | メッセージ ID |
| `role` | string | 送信者 (`"user"` または `"assistant"`) |
| `content` | string | メッセージ本文 |
| `feedback` | FeedbackData / null | フィードバック (ユーザーメッセージの場合のみ) |
| `created_at` | datetime | 送信日時 |

#### FeedbackData

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `grammar_errors` | array of object | 文法エラー (`original`, `corrected`, `explanation`) |
| `expression_upgrades` | array of object | 表現改善提案 (`original`, `upgraded`, `context`) |
| `pronunciation_notes` | array of string | 発音メモ |
| `positive_feedback` | string | ポジティブフィードバック |
| `vocabulary_level` | string | CEFR 語彙レベル推定 |

#### FlashExercise

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `exercise_id` | string | エクササイズ ID |
| `japanese` | string | 日本語文 |
| `english_target` | string | 目標英訳 |
| `acceptable_alternatives` | array of string | 許容される代替回答 |
| `key_pattern` | string | 注目パターン |
| `difficulty` | string | 難易度 (CEFR) |
| `time_limit_seconds` | int | 制限時間 (秒、デフォルト: 15) |
| `hints` | array of string | ヒントリスト |

#### FlashCheckResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `is_correct` | bool | 正解かどうか |
| `score` | float | 正答スコア (0.0〜1.0) |
| `corrected` | string | 修正後の英文 |
| `explanation` | string | 解説 |
| `review_item_created` | bool | 復習アイテム作成有無 |

#### ReviewItemResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | アイテム ID |
| `item_type` | string | アイテム種類 |
| `content` | object | アイテム内容 |
| `next_review_at` | datetime / null | 次回復習日時 |
| `ease_factor` | float | 容易さ係数 |
| `interval_days` | int | 復習間隔 (日) |
| `repetitions` | int | 復習回数 |

#### ReviewCompleteResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `next_review_at` | datetime | 次回復習日時 |
| `new_interval_days` | int | 新しい復習間隔 (日) |
| `new_ease_factor` | float | 新しい容易さ係数 |

#### DashboardResponse

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `streak_days` | int | 連続学習日数 |
| `total_practice_minutes` | int | 累計学習時間 (分) |
| `total_sessions` | int | 累計セッション数 |
| `total_reviews_completed` | int | 累計復習完了数 |
| `total_expressions_learned` | int | 累計学習表現数 |
| `avg_grammar_accuracy` | float / null | 平均文法正確性 |
| `avg_pronunciation_score` | float / null | 平均発音スコア |
| `recent_daily_stats` | array of object | 直近 7 日間の日次統計 |
| `pending_reviews` | int | 未復習アイテム数 |

---

## WebSocket / SSE (将来計画)

現在の API は全て REST (リクエスト/レスポンス) 方式です。今後のバージョンで以下のリアルタイム通信を導入予定です。

### 計画中の機能

| 機能 | 方式 | 説明 |
| --- | --- | --- |
| ストリーミング AI 応答 | SSE (Server-Sent Events) | AI の応答をトークン単位でリアルタイム配信 |
| 音声認識 | WebSocket | リアルタイム音声入力の処理 |
| 発音評価 | WebSocket | Azure Speech Services との連携 |
| リアルタイム通知 | SSE | 復習リマインダーなどのプッシュ通知 |

### 予定エンドポイント (ドラフト)

```text
# SSE: AI 応答ストリーミング
GET /api/talk/message/stream
  Headers: Authorization: Bearer <token>
  Query: session_id=<uuid>&content=<message>
  Response: text/event-stream

# WebSocket: 音声セッション
WS /api/talk/voice
  Headers: Authorization: Bearer <token>
  Message format: binary (audio chunks)
```

> これらのエンドポイントは開発中であり、API 仕様は変更される可能性があります。
