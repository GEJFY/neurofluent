# 運用マニュアル

FluentEdge AI の 4 つの MVP 機能の使い方と、管理者向けの運用操作をまとめたドキュメントです。

---

## 目次

1. [機能概要](#機能概要)
2. [AI Free Talk (AI 自由会話)](#ai-free-talk-ai-自由会話)
3. [Flash Translation (瞬間英作文)](#flash-translation-瞬間英作文)
4. [Spaced Review (FSRS 間隔反復復習)](#spaced-review-fsrs-間隔反復復習)
5. [Dashboard (ダッシュボード)](#dashboard-ダッシュボード)
6. [管理者向け操作](#管理者向け操作)
7. [パフォーマンスチューニング](#パフォーマンスチューニング)

---

## 機能概要

FluentEdge AI は、AI を活用した 4 つのコア機能でビジネス英語の習得を加速します。

| # | 機能名 | 説明 | 使用 AI モデル |
| --- | --- | --- | --- |
| 1 | **AI Free Talk** | Claude とのテキストベース自由会話 + リアルタイムフィードバック | Claude Sonnet 4.5 |
| 2 | **Flash Translation** | 日本語 → 英語の瞬間翻訳ドリル + AI 採点 | Claude Haiku 4.5 |
| 3 | **Spaced Review** | 忘却曲線に基づく FSRS 間隔反復学習 | -- (アルゴリズムのみ) |
| 4 | **Dashboard** | 学習統計・ストリーク・進捗の可視化 | -- |

### 推奨学習フロー

```
1. ログイン → ダッシュボードで本日の復習状況を確認
2. 復習がある場合 → Spaced Review で復習アイテムを消化
3. AI Free Talk でシーン別の会話練習 (10〜15 分)
4. Flash Translation で瞬間英作文トレーニング (5〜10 問)
5. 間違えた表現は自動的に復習スケジュールに登録
6. ダッシュボードで学習の進捗を確認
```

---

## AI Free Talk (AI 自由会話)

### 概要

Claude Sonnet 4.5 と英語でテキストベースの会話を行う機能です。ビジネスシーンに特化した 5 つのモードを用意しており、ユーザーが送信したメッセージに対してリアルタイムで文法・表現のフィードバックが返されます。

### 会話モード

| モード | 内容 | 想定シーン |
| --- | --- | --- |
| `meeting` | 会議での発言・議論 | チームミーティング、報告会議 |
| `presentation` | プレゼンテーション練習 | 社内発表、クライアント向け提案 |
| `negotiation` | 交渉・折衝 | 契約交渉、条件調整 |
| `small_talk` | 雑談・アイスブレイク | ランチ、出張先での雑談 |
| `interview` | 面接練習 | 英語面接、海外転職 |

### 使い方

#### ステップ 1: セッション開始

1. サイドバーまたはボトムナビから「Talk」を選択
2. 会話モードを選択 (例: `meeting`)
3. 必要に応じてシナリオの詳細を入力 (例: "Quarterly budget review with department heads")
4. 「開始」ボタンをクリック
5. AI が最初の挨拶・シーン設定メッセージを送信

#### ステップ 2: 会話

1. テキスト入力欄にメッセージを英語で入力して送信
2. AI の応答が表示される
3. 送信したメッセージに対するフィードバックパネルが表示される

#### ステップ 3: フィードバックの確認

フィードバックには以下の 5 つの要素が含まれます:

| 要素 | 内容 |
| --- | --- |
| **文法エラー (grammar_errors)** | 誤り箇所・修正案・解説のリスト |
| **表現アップグレード (expression_upgrades)** | より自然な言い回しの提案 |
| **発音ノート (pronunciation_notes)** | テキストベースの発音ヒント |
| **ポジティブフィードバック (positive_feedback)** | 良かった点のコメント |
| **語彙レベル (vocabulary_level)** | 使用語彙の CEFR レベル推定 (A2〜C2) |

#### ステップ 4: セッション履歴

- 過去のセッション一覧から、以前の会話を振り返り可能
- セッション詳細ページで全メッセージとフィードバックを確認

### 効果的な使い方のヒント

- 1 セッション **10〜15 分**を目安に集中して取り組む
- フィードバックで指摘された表現を、次のメッセージで意識的に使ってみる
- 同じモードを繰り返す前に、別のモードも試してバランスよく練習する
- シナリオ説明を具体的に書くと、より実践的な会話が展開される
- 毎日の学習ルーティンに組み込むと、上達が早い

---

## Flash Translation (瞬間英作文)

### 概要

日本語の文を見て、制限時間内に英語に翻訳するドリル形式のエクササイズです。Claude Haiku 4.5 が問題を動的に生成し、ユーザーの回答を AI が採点・解説します。スコアが低い回答は自動的に復習スケジュールに登録されます。

### 仕組み

```
1. ユーザーのレベルと弱点パターンに基づいて問題を生成
2. 日本語の文を表示 → 制限時間内 (デフォルト 15 秒) に英訳を入力
3. AI が回答を評価 → スコア (0.0〜1.0) と解説を返す
4. スコア 0.7 未満 → 自動的に復習アイテムとして登録
```

### 使い方

#### ステップ 1: エクササイズの開始

1. メニューから「Flash」を選択
2. エクササイズがカード形式で複数枚表示される
3. デフォルトは 5 問 (1〜20 問で指定可能)
4. 特定のフォーカス (文法パターン) を指定することも可能

#### ステップ 2: 回答

1. 日本語の文を読む
2. 制限時間内に英語の翻訳を入力
3. 「チェック」ボタンで回答を送信

#### ステップ 3: 結果の確認

| 項目 | 説明 |
| --- | --- |
| **正解/不正解** | 正誤の判定 |
| **スコア** | 0.0〜1.0 の採点 (意味・文法・自然さの総合評価) |
| **修正文** | AI による模範解答・修正案 |
| **解説** | なぜその答えが正しい/間違っているかの説明 |
| **復習登録** | スコア 0.7 未満の場合、自動的に復習スケジュールに追加 |

### 出題の難易度

ユーザーのプロフィール設定 (`target_level`) に応じて問題が生成されます。

| レベル | 内容例 |
| --- | --- |
| A2 | 基本的な日常表現 ("この会議は 3 時に始まります") |
| B1 | ビジネス基礎 ("先日のメールの件について確認したいのですが") |
| B2 | ビジネス応用 ("この提案は検討に値すると思いますが、いくつか懸念点があります") |
| C1 | 高度なビジネス ("市場環境の変化を踏まえて、戦略の見直しを提案させていただきます") |

### 弱点パターンの分析

直近 7 日間の学習統計 (`daily_stats`) から弱点パターンを自動抽出し、重点的に出題します。例:

- 仮定法の間違いが多い → 仮定法の問題を増加
- 受動態の正答率が低い → 受動態の問題を優先出題
- 関係代名詞の使い分けが弱い → 関係代名詞の問題を追加

---

## Spaced Review (FSRS 間隔反復復習)

### 概要

FSRS (Free Spaced Repetition Scheduler) アルゴリズムを採用した間隔反復学習システムです。忘却曲線に基づいて最適なタイミングで復習アイテムを提示し、効率的な長期記憶の定着を図ります。

### FSRS アルゴリズムについて

- **19 個の重みパラメータ**で忘却曲線をモデル化
- ユーザーの回答パターンに応じて、**安定度 (stability)** と**難易度 (difficulty)** を更新
- **次回復習タイミング**を自動計算
- 従来の SM-2 アルゴリズムと比較して、より精度の高い復習スケジューリングを実現

### 使い方

#### ステップ 1: 復習対象の確認

1. メニューから「Review」を選択
2. 今日の復習対象アイテムが一覧表示される
3. ダッシュボードにも未復習件数が表示される

#### ステップ 2: 復習の実施

1. カード形式で復習アイテムが表示される
2. アイテムの内容 (問題文、正解、前回の間違い) を確認
3. 自分で回答を思い出す
4. カードをめくって正解を確認

#### ステップ 3: セルフレーティング

思い出せた度合いを 4 段階で自己評価します:

| レーティング | 意味 | 次回復習への影響 |
| --- | --- | --- |
| **1 - Again** | 完全に忘れていた | 短い間隔で再度出題 (約 1 日) |
| **2 - Hard** | 思い出せたが困難だった | やや短い間隔 (元の約 1.2 倍) |
| **3 - Good** | 適度な努力で思い出せた | 標準的な間隔 (元の約 2.5 倍) |
| **4 - Easy** | 即座に思い出せた | 長い間隔 (元の 3.5 倍以上) |

#### ステップ 4: 結果の確認

レーティング送信後、以下が表示されます:

- **次回復習日**: 次にこのアイテムが復習対象になる日
- **新しい間隔**: 次回までの間隔 (日数)
- **新しい ease factor**: 難易度に応じた調整値

全ての復習が完了すると「本日の復習完了」メッセージが表示されます。

### 復習アイテムの自動登録

以下の場合に復習アイテムが自動的に作成されます:

- **瞬間英作文**: スコア 0.7 未満の回答
- 登録される内容: 問題文、正解、ユーザーの回答、修正文、解説

### 復習のベストプラクティス

- **毎日の復習を欠かさない**: 溜めるとアイテムが増えて負荷が高くなる
- **正直にレーティングする**: 自分に甘くすると長期記憶に定着しにくい
- **朝一番に復習する**: 記憶の定着には朝の復習が効果的

---

## Dashboard (ダッシュボード)

### 概要

ユーザーの学習進捗を可視化するダッシュボードです。ログイン後のホーム画面として表示されます。

### 表示項目

| 項目 | 説明 |
| --- | --- |
| **連続学習日数 (ストリーク)** | 今日を含む連続で学習した日数 |
| **累計学習時間** | これまでの総学習時間 (分単位) |
| **総セッション数** | AI Free Talk の実施回数 |
| **総復習完了数** | Spaced Review で完了した復習の累計数 |
| **学習済み表現数** | 新たに学んだ表現・語彙の累計数 |
| **平均文法正答率** | 文法の正確さの平均スコア |
| **平均発音スコア** | 発音評価の平均スコア (将来機能) |
| **直近 7 日間の日次統計** | 日ごとの学習時間、セッション数、復習数 |
| **未復習アイテム数** | 本日復習が必要なアイテムの件数 |

### ストリーク計算のロジック

- 今日を起点に、過去に遡って連続で学習 (practice_minutes > 0) した日数をカウント
- 今日まだ学習していない場合は、昨日を起点にカウント
- 1 日でも空白があるとストリークはリセットされる

### 日次統計の内訳

直近 7 日間の日次統計には以下の項目が含まれます:

| 項目 | 説明 |
| --- | --- |
| `date` | 日付 |
| `practice_minutes` | その日の学習時間 (分) |
| `sessions_completed` | 完了したセッション数 |
| `reviews_completed` | 完了した復習数 |
| `new_expressions_learned` | 新たに学んだ表現数 |
| `grammar_accuracy` | 文法正答率 |
| `pronunciation_avg_score` | 発音平均スコア |

### 学習目標の目安

- 毎日 **最低 15 分**の学習を目標に設定
- ストリークを維持することで学習習慣が定着
- 復習アイテムは**溜めずに毎日消化**するのが効果的
- 週末にまとめて学習するより、毎日少しずつの方が記憶定着率が高い

---

## 管理者向け操作

### データベースバックアップ

#### ローカル環境

```bash
# PostgreSQL のダンプを取得
docker compose exec postgres pg_dump -U fluentedge fluentedge > backup_$(date +%Y%m%d).sql

# ダンプからリストア
docker compose exec -T postgres psql -U fluentedge fluentedge < backup_20260214.sql
```

#### Azure 環境

Azure Database for PostgreSQL Flexible Server の自動バックアップが有効です (デフォルト 7 日間保持)。

```bash
# バックアップ状況を確認
az postgres flexible-server backup list \
  --resource-group fluentedge-dev-rg \
  --name fluentedge-dev-pg

# ポイントインタイムリストア
az postgres flexible-server restore \
  --resource-group fluentedge-dev-rg \
  --name fluentedge-dev-pg-restored \
  --source-server fluentedge-dev-pg \
  --restore-time "2026-02-14T10:00:00Z"
```

### ログの確認

#### ローカル環境

```bash
# バックエンドのログ (uvicorn)
# → ターミナルに直接出力される

# PostgreSQL のログ
docker compose logs -f postgres

# Redis のログ
docker compose logs -f redis

# 全サービスのログを追跡
docker compose logs -f
```

#### Azure 環境

```bash
# Container Apps のログをリアルタイム表示
az containerapp logs show \
  --name fluentedge-dev-backend \
  --resource-group fluentedge-dev-rg \
  --follow

# Log Analytics でクエリ (KQL)
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where ContainerName_s == 'fluentedge-backend' | order by TimeGenerated desc | take 100"
```

### モニタリング

#### ヘルスチェック

```bash
curl http://localhost:8000/health
# 期待レスポンス: {"status":"healthy","service":"fluentedge-api"}
```

#### データベース状態の確認

```bash
# アクティブ接続数
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'fluentedge';"

# テーブルサイズ一覧
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# レコード数確認
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT schemaname, tablename, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"
```

#### Redis 状態の確認

```bash
# メモリ使用量
docker compose exec redis redis-cli info memory

# キースペース情報
docker compose exec redis redis-cli info keyspace

# 全キー数
docker compose exec redis redis-cli dbsize
```

### ユーザー管理

現時点では管理画面は未実装です。データベースに直接アクセスしてユーザー情報を管理します。

```bash
# ユーザー一覧
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT id, email, name, target_level, created_at FROM users ORDER BY created_at DESC;"

# ユーザー数
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT count(*) FROM users;"

# 特定ユーザーの学習統計
docker compose exec postgres psql -U fluentedge -d fluentedge \
  -c "SELECT date, practice_minutes, sessions_completed, reviews_completed FROM daily_stats WHERE user_id = '<user-uuid>' ORDER BY date DESC LIMIT 7;"
```

---

## パフォーマンスチューニング

### バックエンド

#### Uvicorn ワーカー数の調整

本番環境ではマルチワーカーで起動することを推奨します。

```bash
# CPU コア数 * 2 + 1 が目安
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### データベース接続プールの調整

`database.py` の `create_async_engine` パラメータを調整します。

| パラメータ | 開発環境 | 本番環境 |
| --- | --- | --- |
| `pool_size` | 5 | 20 |
| `max_overflow` | 10 | 30 |
| `pool_timeout` | 30 | 30 |
| `pool_recycle` | 1800 | 1800 |

### データベース

#### インデックスの追加

頻繁にクエリされるカラムにインデックスを追加することでレスポンス時間を改善できます。

```sql
-- 復習アイテムの検索高速化
CREATE INDEX idx_review_items_user_next_review
ON review_items (user_id, next_review_at);

-- 会話セッションの検索高速化
CREATE INDEX idx_conversation_sessions_user_started
ON conversation_sessions (user_id, started_at DESC);

-- 日次統計の検索高速化
CREATE INDEX idx_daily_stats_user_date
ON daily_stats (user_id, date DESC);
```

### Redis キャッシュ戦略

| データ | TTL | 用途 |
| --- | --- | --- |
| セッションデータ | 24 時間 | JWT トークン検証のキャッシュ |
| エクササイズ結果 | 1 時間 | 瞬間英作文の一時保存 |
| ダッシュボード統計 | 5 分 | 頻繁なクエリの軽減 |

### フロントエンド

#### ビルド最適化

```bash
# 本番ビルド
npm run build

# バンドルサイズの分析
ANALYZE=true npm run build
```

#### 画像・アセットの最適化

- Next.js の `Image` コンポーネントで自動最適化
- 静的アセットには CDN (Azure CDN または Cloudflare) の利用を推奨

### Claude API 呼び出しの最適化

| 設定 | 推奨値 | 理由 |
| --- | --- | --- |
| 会話の `max_tokens` | 512 | 応答の長さを適切に制限 |
| フィードバックの `max_tokens` | 1024 | 詳細なフィードバックに十分なトークン数 |
| 瞬間英作文の問題生成 | バッチ 5〜10 問 | API 呼び出し回数を削減 |
| 会話履歴の送信 | 直近 6 メッセージ | コンテキストウィンドウとコストのバランス |

### コスト最適化のポイント

1. **Claude Haiku の活用**: スコアリング等の軽量タスクは Haiku で処理 (Sonnet の約 1/10 コスト)
2. **会話履歴の圧縮**: 長い会話は直近 N ターンのみ Claude API に送信
3. **Redis キャッシュ**: 頻出のフラッシュ翻訳問題をキャッシュ
4. **dev 環境のゼロスケール**: 未使用時はレプリカを 0 にして料金削減

---

その他の運用に関する質問は、[セットアップガイド](setup-guide.md)、[API リファレンス](api-reference.md)、[デプロイメントガイド](deployment-guide.md) も参照してください。
