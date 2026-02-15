# FluentEdge — エンタープライズ設計仕様書 v2.0

## AI-Powered Business English Accelerator

**バージョン**: 2.2
**更新日**: 2026-02-15
**ステータス**: レビュー待ち

---

## 目次

1. [プロダクト概要](#1-プロダクト概要)
2. [技術アーキテクチャ（Azure）](#2-技術アーキテクチャazure)
3. [コア機能詳細](#3-コア機能詳細)
4. [画面設計](#4-画面設計)
5. [データモデル](#5-データモデル)
6. [API設計](#6-api設計)
7. [LLMプロンプト設計](#7-llmプロンプト設計)
8. [脳科学ベースの学習設計原則（拡張版）](#8-脳科学ベースの学習設計原則拡張版)
9. [外部コンテンツ連携・コンテンツパイプライン](#9-外部コンテンツ連携コンテンツパイプライン)
10. [ビジネスコンテンツライブラリ](#10-ビジネスコンテンツライブラリ)
11. [コスト設計・料金プラン](#11-コスト設計料金プラン)
12. [非機能要件](#12-非機能要件)
13. [セキュリティ・コンプライアンス](#13-セキュリティコンプライアンス)
14. [監視・オブザーバビリティ](#14-監視オブザーバビリティ)
15. [GitHub リポジトリ・CI/CD](#15-github-リポジトリcicd)
16. [Infrastructure as Code（Bicep）](#16-infrastructure-as-codebicep)
17. [テスト戦略](#17-テスト戦略)
18. [開発フェーズ（改訂版）](#18-開発フェーズ改訂版)
19. [実装ガイド](#19-実装ガイド)

---

## 1. プロダクト概要

### 1.1 ミッション
ビジネスプロフェッショナルが、ネイティブスピーカーとの高速な会議・ディスカッションに対応できるリスニング力・スピーキング力を、脳科学に基づいたメソッドとAIの力で最短で獲得するためのトレーニングアプリ。

### 1.2 ターゲットユーザー
- Big4 / グローバル企業で働く日本人ビジネスパーソン
- TOEIC 700〜900程度だが、実践的なスピーキング・リスニングに課題がある
- 会議のファシリテーション、ディスカッション参加、ネイティブの速い英語への対応が必要
- 多忙なため、短時間で効率的に学習したい

### 1.3 解決する課題
| 課題 | アプリが提供する解決策 |
|------|----------------------|
| ネイティブの速い会話についていけない | 速度段階調整シャドーイング、リンキング・リダクション特化訓練 |
| 会議でファシリテーションができない | ビジネスシーン別ロールプレイ（会議進行、意見集約、反論対応） |
| ディスカッションで発言が遅れる | 瞬間英作文 + パターンプラクティスで反射速度を鍛える |
| 文法は分かるが自然な表現が出ない | AIがより自然でSophisticatedな表現をリアルタイム提案 |
| スラングや口語表現が分からない | カジュアル〜フォーマルのレジスター別トレーニング |

---

## 2. 技術アーキテクチャ（Azure）

### 2.1 全体構成図
```
┌─────────────────────────────────────────────────────────────────────┐
│                        Azure Front Door (CDN + WAF)                 │
│                     グローバルロードバランシング + DDoS防御           │
├─────────────────────────┬───────────────────────────────────────────┤
│    Frontend (Next.js)    │           Backend (FastAPI)               │
│    Azure Container Apps  │           Azure Container Apps            │
│    ┌───────────────┐     │     ┌───────────────────────────────┐    │
│    │ App Router     │     │     │ WebSocket Handler              │    │
│    │ React 19       │     │     │ REST API Routers               │    │
│    │ Zustand        │◄───►│     │ Service Layer                  │    │
│    │ Tailwind CSS   │     │     └──────┬──────┬──────┬──────────┘    │
│    │ shadcn/ui      │     │            │      │      │               │
│    └───────────────┘     │            ▼      ▼      ▼               │
├─────────────────────────┤     ┌──────┐┌────┐┌──────────────┐       │
│                          │     │Azure ││Azure││Azure         │       │
│   Azure API Management   │     │OpenAI││Speech│PostgreSQL    │       │
│   (Rate Limit + Gateway) │     │      ││Svc  ││Flexible Svr  │       │
│                          │     │      ││     ││+ pgvector    │       │
├─────────────────────────┤     │Realtime│Pron.││              │       │
│ Authentication            │     │API   ││Assess│└──────────────┘       │
│ Microsoft Entra ID        │     │GPT-5 ││ment ││                      │
│ (B2C / External ID)      │     │STT   ││     ││┌──────────────┐      │
│                          │     │TTS   ││     │││Azure Cache    │      │
│                          │     └──────┘└────┘││for Redis      │      │
│                          │                    │└──────────────┘      │
├──────────────────────────┴──────────────────────────────────────────┤
│                    Infrastructure Layer                               │
│  ┌─────────┐ ┌──────────────┐ ┌───────────┐ ┌────────────────────┐ │
│  │Key Vault│ │Container     │ │App        │ │Log Analytics       │ │
│  │(Secrets)│ │Registry (ACR)│ │Insights   │ │Workspace           │ │
│  └─────────┘ └──────────────┘ └───────────┘ └────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 技術スタック（Azure版）

| レイヤー | 技術 | Azureサービス | 選定理由 |
|---------|------|--------------|---------|
| **フロントエンド** | Next.js 15 + TypeScript + Tailwind CSS | Azure Container Apps | SSR/SSG対応、Dockerコンテナ化で柔軟なデプロイ |
| **UIコンポーネント** | shadcn/ui + Radix UI | — | アクセシブルで高品質なコンポーネント |
| **状態管理** | Zustand | — | 軽量で学習状態管理に最適 |
| **リアルタイム会話** | GPT Realtime API (WebRTC) | Azure OpenAI Service | STT+LLM+TTS統合、~100msレイテンシ |
| **音声入力 (STT)** | gpt-4o-transcribe | Azure OpenAI Service | 高精度、日本人英語対応 |
| **音声出力 (TTS)** | gpt-4o-mini-tts（スタイル制御） | Azure OpenAI Service | 自然な音声、トーン・速度制御 |
| **発音評価** | Pronunciation Assessment | Azure Speech Services | 音素レベルの発音スコアリング |
| **LLM（会話以外）** | Claude Opus 4.6 / Sonnet 4.5 / Haiku 4.5 | Azure AI Foundry (Marketplace) | フィードバック生成、カリキュラム最適化 |
| **バックエンド** | FastAPI (Python 3.11) | Azure Container Apps (Consumption) | Scale-to-zero、WebSocket対応 |
| **DB** | PostgreSQL 16 + pgvector | Azure Database for PostgreSQL Flexible Server | ベクトル検索対応、HA対応 |
| **キャッシュ** | Redis 7 | Azure Cache for Redis (Standard C1) | セッション管理、レート制限 |
| **認証** | Microsoft Entra External ID | Azure Entra ID | エンタープライズSSO、Google/Email対応 |
| **シークレット管理** | — | Azure Key Vault | Managed Identity経由でシークレットアクセス |
| **API Gateway** | — | Azure API Management (Basic v2) | レート制限、API バージョニング |
| **CDN / WAF** | — | Azure Front Door (Standard) | グローバルCDN、DDoS防御 |
| **監視** | OpenTelemetry | Azure Application Insights + Log Analytics | 分散トレーシング、カスタムメトリクス |
| **IaC** | Bicep | Azure Resource Manager | 宣言的インフラ定義、環境別パラメータ |
| **CI/CD** | GitHub Actions (OIDC認証) | Azure Container Registry | パスワードレス認証、ゼロダウンタイムデプロイ |
| **リージョン** | East US 2（プライマリ） | — | Realtime API + Claude 両方利用可能な唯一のリージョン |

### 2.3 AIモデル使い分け戦略

コスト最適化のため、処理の重さに応じてモデルを使い分ける。

| 処理 | モデル | 理由 |
|------|--------|------|
| **リアルタイム会話** | GPT Realtime API (gpt-realtime) | STT+LLM+TTSを統合、最低レイテンシ |
| **会話フィードバック生成** | Claude Haiku 4.5 | 低コスト、構造化JSON出力が得意 |
| **表現改善・添削** | Claude Sonnet 4.5 | 高品質な言語分析 |
| **瞬間英作文の採点** | Claude Haiku 4.5 | 高速・低コスト |
| **カリキュラム最適化** | Claude Opus 4.6 | 複雑な分析が必要 |
| **コンテンツ生成（バッチ）** | GPT-5（Batch API: 50%割引） | 大量生成タスクのコスト削減 |
| **発音評価** | Azure Speech Services Pronunciation Assessment | 音素レベルスコアリングの専用API |

### 2.4 リアルタイム会話アーキテクチャ

GPT Realtime APIを核とした低レイテンシ会話フロー:

```
ブラウザ (WebRTC)
    │
    ├── 音声ストリーム ────────────► Azure OpenAI Realtime API
    │                                │ (gpt-realtime / East US 2)
    │                                │
    │   ◄── AI音声レスポンス ────────┘
    │   ◄── 文字起こしテキスト ──────┘
    │
    ├── ユーザー発話テキスト ──────► FastAPI Backend (WebSocket)
    │                                │
    │                                ├── Claude Haiku 4.5 → フィードバックJSON
    │                                ├── Azure Speech → 発音スコア
    │                                └── PostgreSQL → 会話ログ保存
    │
    │   ◄── フィードバック表示 ──────┘
```

**接続仕様:**
- プロトコル: WebRTC（ブラウザ直結で~100msレイテンシ）
- 音声フォーマット: PCM 16-bit mono, 24kHz
- セッション上限: 30分（自動延長ロジック実装）
- VADモード: semantic_vad（AIベースの発話終了検出、割り込み防止）
- ボイス: nova（女性・ニュートラル）/ onyx（男性・プロフェッショナル）選択可

---

## 3. コア機能詳細

### 3.1 ダッシュボード（ホーム画面）
- 今日のトレーニングメニュー（AIが最適化）
- 学習ストリーク・進捗グラフ
- 弱点分析サマリー（発音、文法、語彙、リスニング速度別）
- 忘却曲線ベースの復習リマインダー
- 週次/月次レポート

### 3.2 AIフリートーク（メイン機能）

#### 概要
GPT Realtime APIを活用したリアルタイム音声英会話セッション。テキスト入力にも対応。

#### フロー
```
ユーザー音声入力 (WebRTC)
    ↓
GPT Realtime API（統合処理）
├── 音声認識（STT）
├── AI応答生成（LLM）
└── 音声合成（TTS） → 即座に音声再生
    ↓ 同時に（非同期バックグラウンド処理）
├── Claude Haiku 4.5 → 文法チェック・表現改善のフィードバックJSON生成
├── Azure Speech Services → 発音スコアリング
└── PostgreSQL → 会話ログ保存（復習用）
    ↓
フィードバックをサイドパネルに表示（遅延許容: ~2秒）
```

#### 会話モード
| モード | 説明 | MVP対象 |
|--------|------|---------|
| **Casual Chat** | 日常会話、スラング含む | Phase 1 |
| **Meeting Facilitation** | 会議進行ロールプレイ | Phase 2 |
| **Debate & Discussion** | テーマ別ディベート | Phase 2 |
| **Presentation Q&A** | プレゼン後の質疑応答 | Phase 3 |
| **Client Negotiation** | 交渉シーン | Phase 3 |
| **Small Talk** | ビジネスソーシャル | Phase 3 |

#### AIフィードバック表示（サイドパネル / 会話後レビュー）
- **Grammar Correction**: 文法エラーをハイライト＋修正案
- **Expression Upgrade**: より自然/Sophisticatedな言い換え提案
- **Register Awareness**: フォーマル度合いの適切さ評価
- **Filler Word Detection**: "um", "like", "you know" の使用頻度トラッキング
- **Response Time**: 発話までの反応時間を計測・改善トラッキング
- **Pronunciation Score**: Azure Speech Servicesによる音素レベルスコア

### 3.3 リスニングトレーニング

#### 3.3.1 スピード段階シャドーイング
```
[音声再生コントロール]
速度: 0.7x → 0.8x → 0.9x → 1.0x → 1.1x → 1.2x（ネイティブ速度超え）

ステップ:
1. まず1.0xで聞く（理解度チェック）
2. 0.7xでテキスト見ながらシャドーイング
3. 0.8x → 0.9x と段階的にスピードアップ
4. 1.0xでテキストなしシャドーイング
5. 1.1x〜1.2xでオーバースピードトレーニング
```

**脳科学根拠**: オーバースピードトレーニングにより、通常速度が「遅く」感じられるようになる（知覚速度の再キャリブレーション）

#### 3.3.2 もごもごイングリッシュ（リンキング＆リダクション特訓）
- ネイティブが実際に使う音声変化パターンをカテゴリ別に学習
  - **リンキング**: "pick it up" → "pi-ki-tup"
  - **リダクション**: "going to" → "gonna", "want to" → "wanna"
  - **フラッピング**: "water" → "wader", "better" → "bedder"
  - **子音脱落**: "last night" → "las' night"
  - **弱形**: "can" → /kən/, "have" → /əv/
- AIがユーザーの苦手パターンを分析し、集中練習を自動生成
- ディクテーション（聞き取り書き起こし）モード付き

#### 3.3.3 リスニングコンプリヘンション
- ビジネスシーン別の音声素材（AIが動的生成）
- 理解度クイズ（選択式 + 要約記述）
- 音声素材の難易度を自動調整

### 3.4 スピーキングドリル

#### 3.4.1 瞬間英作文（Flash Translation）
```
[日本語表示] → [制限時間カウントダウン: 3秒→2秒→1.5秒] → [ユーザー発話] → [AIチェック]

レベル設計:
Level 1: 単文（主語＋動詞＋目的語）
Level 2: 複文（接続詞、関係代名詞）
Level 3: ビジネス表現（"I'd like to propose...", "Having said that..."）
Level 4: 複雑な意見表明（仮定法、婉曲表現、段階的主張）
Level 5: ネイティブレベル（慣用句、比喩、修辞技法）
```

#### 3.4.2 パターンプラクティス（Sentence Pattern Drill）
- ビジネス必須パターン200+をカテゴリ別に収録
- AIがユーザーの使用パターンを分析し、不足パターンを重点的に出題

#### 3.4.3 発音トレーニング
- Azure Speech Services Pronunciation Assessment による音素レベル評価
  - 正確度（Accuracy）、流暢性（Fluency）、韻律（Prosody）、完全性（Completeness）
- 日本人が苦手な音素の集中練習（/r/ vs /l/, /θ/ vs /s/, /v/ vs /b/ 等）
- プロソディ（抑揚・リズム・ストレス）トレーニング

### 3.5 忘却曲線ベース復習システム（Spaced Repetition）

#### アルゴリズム設計
```python
# SM-2ベースの間隔反復アルゴリズム（カスタマイズ版）
class SpacedRepetition:
    def calculate_next_review(self, item, quality: int):
        """
        quality: 0-5 (ユーザーの正答度/流暢度)
        0: 完全に忘れた
        3: 思い出せたが遅い
        5: 即座に正確に回答
        """
        if quality < 3:
            item.interval = 1
            item.repetitions = 0
        else:
            if item.repetitions == 0:
                item.interval = 1
            elif item.repetitions == 1:
                item.interval = 3
            elif item.repetitions == 2:
                item.interval = 7
            else:
                item.interval = int(item.interval * item.ease_factor)
            item.repetitions += 1

        item.ease_factor = max(1.3,
            item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        item.next_review = datetime.now() + timedelta(days=item.interval)
        return item
```

### 3.6 アナリティクス & パーソナライゼーション

#### 追跡メトリクス
```typescript
interface UserAnalytics {
  // スピーキング
  averageResponseTime: number;       // 発話までの平均反応時間(秒)
  fillerWordFrequency: Record<string, number>;
  grammarAccuracy: number;           // 文法正確度 (%)
  expressionSophistication: string;  // CEFR レベル (B2/C1/C2)
  vocabularyRange: number;
  patternUsageDiversity: number;
  pronunciationScore: number;        // Azure Speech 発音スコア (0-100)

  // リスニング
  comprehensionBySpeed: Record<string, number>;
  weakSoundPatterns: string[];
  dictationAccuracy: number;

  // 学習習慣
  dailyStreak: number;
  totalPracticeMinutes: number;
  reviewCompletionRate: number;

  // 忘却曲線
  retentionRate: number;
  itemsDueForReview: number;
}
```

---

## 4. 画面設計

### 4.1 画面一覧
```
/                           → ダッシュボード（ホーム）
/talk                       → AIフリートーク（会話画面）
/talk/review/:sessionId     → 会話セッションレビュー
/listening                  → リスニングトレーニングメニュー
/listening/shadowing        → シャドーイング
/listening/mogomogo         → もごもごイングリッシュ
/listening/comprehension    → リスニングコンプリヘンション
/speaking                   → スピーキングドリルメニュー
/speaking/flash             → 瞬間英作文
/speaking/pattern           → パターンプラクティス
/speaking/pronunciation     → 発音トレーニング
/review                     → 復習（忘却曲線ベース）
/analytics                  → 学習アナリティクス
/settings                   → 設定
/subscription               → サブスクリプション管理
```

### 4.2 UIデザインガイドライン
- **テーマ**: ダークモード基調 + ライトモード切替
- **カラーパレット**:
  - Primary: #6366F1 (Indigo)
  - Accent: #22D3EE (Cyan)
  - Warning: #F59E0B (Amber)
  - Background Dark: #0F172A
  - Background Light: #F8FAFC
- **タイポグラフィ**:
  - 英語: "DM Sans" (見出し), "Source Sans 3" (本文)
  - 日本語: "Noto Sans JP"
- **モバイルファースト**: タッチ操作最適化、片手操作可能なナビゲーション
- **マイクボタン**: 画面下部中央に大きく配置（会話画面）

### 4.3 主要画面ワイヤーフレーム概要

#### ダッシュボード
```
┌─────────────────────────────┐
│  FluentEdge    [通知] [設定] │
├─────────────────────────────┤
│  Good evening, Go            │
│  Today's Focus: Meeting      │
│  Facilitation                │
├─────────────────────────────┤
│  Weekly Progress             │
│  ████████░░ 72%              │
│  Streak: 14 days             │
├─────────────────────────────┤
│  Today's Menu                │
│  ┌───────────────────────┐  │
│  │ 1. Review (12 items)  │  │
│  │ 2. Pattern Practice   │  │
│  │ 3. AI Talk: Meeting   │  │
│  │ 4. Shadowing (5 min)  │  │
│  └───────────────────────┘  │
├─────────────────────────────┤
│  Weak Points                 │
│  Linking sounds  ████░░ 60%  │
│  Response speed  █████░ 80%  │
│  Grammar         ██████ 95%  │
├─────────────────────────────┤
│  [Home] [Talk] [Listen]      │
│  [Drill] [Stats]             │
└─────────────────────────────┘
```

#### AIフリートーク画面
```
┌─────────────────────────────┐
│ ← Meeting Facilitation  設定 │
├─────────────────────────────┤
│                              │
│  AI: "Let's start today's   │
│  quarterly review. As the   │
│  facilitator, please open   │
│  the meeting."              │
│                    [再生]    │
│                              │
│  You: "Thank you everyone   │
│  for joining. Today we'll   │
│  cover three main topics..."│
│                              │
│  ┌─ Feedback ─────────────┐ │
│  │ Better: "I'd like to    │ │
│  │ walk us through three   │ │
│  │ key agenda items"       │ │
│  │ Grammar: OK             │ │
│  │ Response: 2.1s          │ │
│  │ Pronunciation: 82/100   │ │
│  └────────────────────────┘ │
│                              │
├─────────────────────────────┤
│  Hints: "Let me address     │
│  that..." / "That's a valid │
│  point..."                   │
├─────────────────────────────┤
│         [TAP TO SPEAK]       │
│  [Home] [Talk] [Listen]      │
│  [Drill] [Stats]             │
└─────────────────────────────┘
```

---

## 5. データモデル

### 5.1 主要テーブル
```sql
-- ユーザー
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    entra_id VARCHAR(255) UNIQUE,           -- Microsoft Entra External ID
    native_language VARCHAR(10) DEFAULT 'ja',
    target_level VARCHAR(10) DEFAULT 'C1',
    daily_goal_minutes INTEGER DEFAULT 15,
    subscription_plan VARCHAR(20) DEFAULT 'free',  -- free / standard / premium
    api_usage_monthly INTEGER DEFAULT 0,           -- 月間API使用量トラッキング
    api_usage_reset_at TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_users_entra_id ON users(entra_id);
CREATE INDEX idx_users_email ON users(email);

-- 会話セッション
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mode VARCHAR(50) NOT NULL,
    scenario_description TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    overall_score JSONB,
    api_tokens_used INTEGER DEFAULT 0,     -- コスト追跡
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX idx_sessions_started_at ON conversation_sessions(started_at);

-- 会話メッセージ
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    audio_blob_url TEXT,                    -- Azure Blob Storage URL
    feedback JSONB,
    pronunciation_score JSONB,             -- Azure Speech 発音スコア
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_messages_session_id ON conversation_messages(session_id);

-- 学習アイテム（忘却曲線管理）
CREATE TABLE review_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    source_session_id UUID REFERENCES conversation_sessions(id),
    ease_factor FLOAT DEFAULT 2.5,
    interval_days INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    next_review_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_reviewed_at TIMESTAMP WITH TIME ZONE,
    last_quality INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_review_items_user_next ON review_items(user_id, next_review_at);
CREATE INDEX idx_review_items_type ON review_items(item_type);

-- 学習統計（日次）
CREATE TABLE daily_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    practice_minutes INTEGER DEFAULT 0,
    sessions_completed INTEGER DEFAULT 0,
    reviews_completed INTEGER DEFAULT 0,
    new_expressions_learned INTEGER DEFAULT 0,
    grammar_accuracy FLOAT,
    avg_response_time_ms INTEGER,
    listening_speed_max FLOAT,
    pronunciation_avg_score FLOAT,
    weak_patterns JSONB,
    UNIQUE(user_id, date)
);
CREATE INDEX idx_daily_stats_user_date ON daily_stats(user_id, date);

-- 文型パターン習得状況
CREATE TABLE pattern_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pattern_id VARCHAR(100) NOT NULL,
    pattern_text TEXT NOT NULL,
    category VARCHAR(50),
    mastery_level INTEGER DEFAULT 0,
    times_practiced INTEGER DEFAULT 0,
    times_used_in_conversation INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, pattern_id)
);

-- 音声変化パターン習得
CREATE TABLE sound_pattern_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_detail TEXT NOT NULL,
    mastery_level INTEGER DEFAULT 0,
    times_practiced INTEGER DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0,
    last_practiced_at TIMESTAMP WITH TIME ZONE
);

-- API使用量ログ（コスト管理用）
CREATE TABLE api_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_provider VARCHAR(50) NOT NULL,     -- azure_openai / azure_speech / claude
    model_name VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    audio_seconds FLOAT DEFAULT 0,
    estimated_cost_usd FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_api_usage_user_date ON api_usage_log(user_id, created_at);
CREATE INDEX idx_api_usage_provider ON api_usage_log(api_provider, created_at);
```

---

## 6. API設計

### 6.1 主要エンドポイント
```
# ヘルスチェック
GET    /health                      → サービスヘルスチェック

# 認証 (Microsoft Entra External ID)
GET    /api/auth/login              → Entra ID ログインリダイレクト
GET    /api/auth/callback           → OAuth コールバック
POST   /api/auth/refresh            → トークンリフレッシュ
POST   /api/auth/logout             → ログアウト
GET    /api/auth/me                 → 現在のユーザー情報

# 会話セッション
POST   /api/talk/start              → 新しい会話セッション開始
POST   /api/talk/message            → テキストメッセージ送信
WS     /api/talk/realtime           → WebSocket（Realtime API プロキシ）
GET    /api/talk/sessions           → セッション一覧（ページネーション）
GET    /api/talk/sessions/:id       → セッション詳細（レビュー用）
GET    /api/talk/sessions/:id/feedback → セッション全体のフィードバック

# リスニング
POST   /api/listening/generate      → AI音声素材生成
POST   /api/listening/dictation     → ディクテーション回答提出
GET    /api/listening/mogomogo      → もごもごパターン取得

# スピーキングドリル
GET    /api/speaking/flash          → 瞬間英作文問題取得
POST   /api/speaking/flash/check    → 回答チェック
GET    /api/speaking/patterns       → パターンプラクティス取得
POST   /api/speaking/patterns/practice → パターン練習回答
POST   /api/speaking/pronunciation  → 発音評価（Azure Speech）

# 復習
GET    /api/review/due              → 復習待ちアイテム取得
POST   /api/review/complete         → 復習結果記録

# アナリティクス
GET    /api/analytics/dashboard     → ダッシュボードデータ
GET    /api/analytics/weekly        → 週次レポート
GET    /api/analytics/weakpoints    → 弱点分析

# カリキュラム
GET    /api/curriculum/today        → 今日のトレーニングメニュー
POST   /api/curriculum/generate     → AIカリキュラム再生成

# サブスクリプション
GET    /api/subscription/status     → 現在のプラン・使用量
GET    /api/subscription/usage      → API使用量詳細
```

### 6.2 WebSocket通信（リアルタイム会話用）
```typescript
// クライアント → サーバー
interface ClientMessage {
  type: 'audio_chunk' | 'text' | 'control';
  payload: {
    audio?: ArrayBuffer;
    text?: string;
    action?: 'start' | 'stop' | 'pause' | 'end_session';
  };
}

// サーバー → クライアント
interface ServerMessage {
  type: 'transcription' | 'response' | 'audio' | 'feedback' | 'hint' | 'pronunciation';
  payload: {
    text?: string;
    audio?: ArrayBuffer;
    feedback?: FeedbackData;
    hints?: string[];
    pronunciationScore?: PronunciationResult;
  };
}
```

### 6.3 レート制限（API Management ポリシー）

| プラン | リアルタイム会話 | その他API | 日次上限 |
|--------|----------------|----------|---------|
| Free | 5分/日 | 50リクエスト/時 | 15分/日の学習 |
| Standard | 30分/日 | 200リクエスト/時 | 60分/日の学習 |
| Premium | 無制限 | 500リクエスト/時 | 無制限 |

---

## 7. LLMプロンプト設計

### 7.1 会話トレーナープロンプト（GPT Realtime API用）

GPT Realtime APIのシステムプロンプトとして設定:

```markdown
# Role
You are a professional English conversation trainer for Japanese business professionals.

# Context
- User's current level: {user_level} (CEFR)
- Training mode: {mode} (e.g., meeting_facilitation)
- Scenario: {scenario_description}
- User's weak points: {weak_points}
- Patterns to encourage: {target_patterns}

# Instructions
1. Stay in character for the given scenario
2. Speak naturally at native speed with appropriate register
3. Challenge the user progressively
4. Keep responses concise (2-4 sentences typical in conversation)
5. Occasionally use linking sounds, reductions, and natural speech patterns
6. If the user struggles, offer a simpler rephrasing or hint

# Voice & Style
- Professional but approachable
- Use contractions naturally ("I'd", "we're", "doesn't")
- Vary sentence structure and vocabulary
```

### 7.2 フィードバック生成プロンプト（Claude Haiku 4.5用）

会話ターンごとに非同期で呼び出し:

```markdown
# Role
Analyze the user's English utterance and provide structured feedback.

# Input
- User's utterance: "{user_text}"
- Conversation context: {last_3_turns}
- User's level: {user_level}
- Scenario: {mode}

# Output (JSON)
{
  "grammar_errors": [
    {"original": "...", "corrected": "...", "rule": "...", "explanation_ja": "..."}
  ],
  "expression_upgrades": [
    {"original": "...", "upgraded": "...", "register": "formal|neutral|casual", "explanation_ja": "..."}
  ],
  "pronunciation_notes": ["..."],
  "positive_feedback": "what the user did well",
  "vocabulary_level": "B2|C1|C2",
  "formality_appropriate": true
}
```

### 7.3 瞬間英作文生成プロンプト（Claude Haiku 4.5用）
```markdown
Generate flash translation exercises. Level: {level}, Focus: {focus}, Weak patterns: {weak_patterns}.

Output as JSON array (10 exercises):
[
  {
    "japanese": "日本語の文",
    "english_target": "Expected English",
    "acceptable_alternatives": ["alt1", "alt2"],
    "key_pattern": "pattern being practiced",
    "difficulty": 1-5,
    "time_limit_seconds": 5,
    "hints": ["hint"]
  }
]

Rules: Business-relevant, include target pattern naturally, gradually increase complexity.
```

---

## 8. 脳科学ベースの学習設計原則（拡張版）

### 8.1 採用する学習理論とその実装

#### Tier 1: 基盤理論（Phase 1 から実装）
| 理論 | 実装 | 競合との差別化 |
|------|------|--------------|
| **FSRS間隔反復（SM-2の後継）** | 19パラメータの機械学習最適化アルゴリズム。SM-2比で復習負荷20-30%削減 | Anki以外で採用しているアプリはほぼ皆無 |
| **デシラブル・ディフィカルティ（Bjork）** | 制限時間付き瞬間英作文、セッション内スペーシング、インターリービング | 5つの具体的手法を体系的に実装 |
| **テスト効果（Retrieval Practice）** | 全復習アイテムで想起→発話を必須化。選択式を排除 | 音声認識による発話確認 |
| **プロダクション効果** | 全学習項目を声に出して確認（黙読の15-20%増の定着率） | 復習時もSTT必須 |
| **ジェネレーション効果** | AI提案の受動受信ではなく、ユーザー自身が文を生成する設計 | teach-backモード |
| **弁別的シーン可視化（デュアルコーディング改）** | 会話前に5秒間のAI動的生成シーン描写を提示。2025年研究に基づき、単なる視覚+聴覚の二重符号化ではなく**弁別性（distinctiveness）の最大化**を重視。毎回ユニークな視覚的コンテキスト（参加者の服装、会議室の特徴、天気など）をClaude Haikuで生成し、類似セッション間でも記憶痕跡が混同されない設計。復習時に同じシーンを再表示することで文脈依存記憶（context-dependent memory）を活用 | 静的画像表示ではなくAI動的生成による弁別的シーンは競合に例なし。2025年の知覚的弁別性研究（Frontiers in Psychology）に基づく |
| **覚醒時統合（Post-Session Reflection）** | セッション後90秒の静寂リフレクション画面。シータ波活動促進 | 実装コスト最小・効果最大 |

#### Tier 2: 認知最適化（Phase 2 から実装）
| 理論 | 実装 | 競合との差別化 |
|------|------|--------------|
| **リアルタイム認知負荷推定** | 行動シグナル（反応遅延、発話長、フィラー頻度、語彙レベル低下、日本語混入）から認知負荷を推定。高負荷時にAIが自動的に難易度調整 | **競合ゼロ。最大の差別化ポイント** |
| **CAFモデル（複雑性-正確性-流暢性）** | セッションごとに1つの認知フォーカスを宣言。Fluencyモード/Accuracyモード/Complexityモード | ワーキングメモリ制約に基づく科学的設計 |
| **音韻ループトレーニング** | 遅延シャドーイング（1-3秒待ってからリピート）+ 段階的文長伸長（4音節→20+音節） | 日本語話者のバッファ容量を英語用に再訓練 |
| **リズミックプライミング（神経同調）[実験的]** | シャドーイング前に英語のストレスリズムに合致したビートを再生。聴覚皮質のシータ帯域同調を促進。**注意: エビデンスは理論的根拠に基づくが、L2学習への直接効果の大規模RCTは未実施**。A/Bテストで効果検証を必須とする（下記8.5参照） | Web Audio APIで実装可能。実験的機能としてフィーチャーフラグで制御 |
| **ベイズ的知識モデリング** | 各学習項目についてBeta分布でP(知識あり)を推定。情報エントロピー最大（P=0.3-0.7）の項目を優先出題 | FSRSの「いつ」に加え「何を」を最適化 |

#### Tier 3: 情動・動機づけ（Phase 3 から実装）
| 理論 | 実装 | 競合との差別化 |
|------|------|--------------|
| **外国語不安（FLA）管理** | 不安指標（発話中断増、発話長減、日本語混入増）を検出→AIが支援モードに切替。Safe Spaceトグル | ターゲット層（日本人ビジネスパーソン）の最大障壁に直接対処 |
| **ドパミン最適化報酬システム** | 予測不可能な「ブレークスルー瞬間」通知（5セッションに1回）。進捗速度の表示（絶対値ではなく変化率） | 変動比率強化スケジュール |
| **睡眠前統合レビュー + TMR準備** | 就寝45分前にプッシュ通知→5分間のリスニングオンリー復習（テストなし、コルチゾール抑制）。各復習アイテムに**固有の環境音キュー**（チャイム音のピッチ変化）を紐付けて再生。将来のTMR（Targeted Memory Reactivation）ウェアラブル連携時に、NREM睡眠中に同じキュー音を再生して記憶再活性化を実現する基盤設計。2025年研究: 家庭用EEGヘッドバンドによる閉ループTMRで+8.6%精度向上が検証済み（Wiley, J Sleep Res, 2025） | 概日リズム研究に基づく最適タイミング + **TMRレディ設計は競合ゼロ**。Phase 4でウェアラブル連携時にキュー音データベースをそのまま活用可能 |
| **概日リズム活動最適化** | 起床後3時間: 高負荷タスク（会話、瞬間英作文）。昼食後: 受動的リスニング。夕方: 復習。就寝前: パッシブレビュー | 時間帯別のトレーニング種類推奨 |
| **自己決定理論（SDT）** | 自律性: セッション内容をAI推奨から選択。有能感: 成長速度の可視化。関連性: 将来的なソーシャル機能 | 3つの心理的欲求すべてに対応 |

#### Tier 4: 高度な音声・習得追跡（Phase 4 から実装）
| 理論 | 実装 | 競合との差別化 |
|------|------|--------------|
| **ミラーニューロン活性化** | 困難な音素（/r/, /l/, /θ/等）に対し、口の動きアニメーション + 舌位置図 + スローモーション比較を提供 | 視覚的調音情報による知覚補助 |
| **暗黙的→明示的学習シーケンス** | もごもごイングリッシュで先に30事例の純粋リスニング（暗黙的パターン抽出）→次に明示的説明 | 基底核と海馬の両方を活用 |
| **明示→手続き化パイプライン** | パターン習得を3段階追跡: Stage 1（規則理解）→ Stage 2（ドリル内での正確な産出）→ Stage 3（フリートーク内での自発的使用）。Stage 3のみを「習得」と定義 | 第二言語習得研究の正式な定義に基づく |
| **エラーベースvs無誤学習の使い分け** | 文法・会話: エラー許容→事後修正。新音素: 必ずモデル先行→模倣（運動プログラム固定防止）。定型表現: 最初は全文表示 | スキル種類別のエラーポリシー |
| **日本語話者特化音素エラー分類** | Azure Speech音素スコアをL1干渉パターンにマッピング（/r/-/l/混同, /θ/-/s/混同, /v/-/b/混同, 語末子音脱落, 子音連結の母音挿入） | 音素レベルの縦断的進捗追跡 |
| **身体化認知学習（Embodied Cognition）** | カメラ（MediaPipe Hand/Pose）を使ったジェスチャー連動語彙学習。ビジネスフレーズに意味的に対応するジェスチャーを定義し、フレーズ発話時にジェスチャーを同時実行。2025年fMRI研究で感覚運動訓練がL2音素処理を向上させることが確認（MIT Neurobiology of Language, 2025）。パターンプラクティスでも「体で覚える」モードを提供。運動プログラムと言語記憶の結合により定着率向上 | 語学アプリでジェスチャー検出を実装した例は皆無。身体化認知の最新L2研究を直接実装 |

### 8.2 FSRSアルゴリズム（SM-2の置き換え）

```python
# FSRS (Free Spaced Repetition Scheduler) — SM-2の後継
# https://github.com/open-spaced-repetition/fsrs4anki
class FSRS:
    """
    2つの記憶コンポーネントでモデリング:
    - Stability (S): 記憶が90%の確率で維持される期間（日数）
    - Difficulty (D): アイテム固有・ユーザー固有の難易度 (0-10)

    19個のMLパラメータで最適化（SM-2の5個の固定パラメータと対照的）
    """

    def review(self, card, rating: int, elapsed_days: int):
        """
        rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        """
        # 記憶の検索可能性を推定
        retrievability = (1 + elapsed_days / card.stability) ** -1

        # Stability を更新（成功時は増加、失敗時はリセット）
        if rating >= 2:  # 成功
            card.stability = self._update_stability_success(
                card.stability, card.difficulty, retrievability, rating
            )
        else:  # 失敗 (Again)
            card.stability = self._update_stability_fail(
                card.stability, card.difficulty, retrievability
            )

        # Difficulty を更新
        card.difficulty = self._update_difficulty(card.difficulty, rating)

        # 次回レビュー日を計算（desired_retention=0.9 で90%定着目標）
        card.interval = card.stability * (
            (1 / self.desired_retention) ** (1 / self.decay) - 1
        )
        card.next_review = datetime.now() + timedelta(days=card.interval)
        return card
```

**スキル種類別パラメータセット:**
- 語彙・表現: 標準パラメータ
- 文法パターン: 安定性の初期値を低めに設定（手続き化に時間がかかる）
- 発音: 運動記憶のため安定性の成長率を高く設定
- リスニングパターン: 知覚学習のため高頻度の短い復習

### 8.3 リアルタイム認知負荷推定エンジン

```python
class CognitiveLoadEstimator:
    """
    行動シグナルから認知負荷を0.0-1.0で推定。
    ハードウェア（EEG等）不要 — アプリ内の行動データのみで実現。
    """

    def estimate(self, turn: ConversationTurn, user_baseline: UserBaseline) -> float:
        signals = {
            # 反応遅延（ユーザーのベースライン比）
            "response_latency_ratio": turn.response_time_ms / user_baseline.avg_response_time_ms,
            # 発話長の減少
            "utterance_length_ratio": turn.word_count / user_baseline.avg_word_count,
            # フィラーワード頻度の増加
            "filler_rate": turn.filler_count / max(turn.word_count, 1),
            # 語彙の単純化（CEFR レベル低下）
            "vocab_simplification": user_baseline.avg_vocab_level - turn.vocab_level,
            # 自己修正率
            "self_correction_rate": turn.self_corrections / max(turn.sentence_count, 1),
            # 日本語コードスイッチング
            "code_switching": turn.japanese_insertions / max(turn.word_count, 1),
        }

        # 重み付き複合スコア (0.0=低負荷, 1.0=過負荷)
        weights = {
            "response_latency_ratio": 0.30,
            "utterance_length_ratio": -0.20,  # 短くなると負荷高
            "filler_rate": 0.15,
            "vocab_simplification": 0.15,
            "self_correction_rate": 0.10,
            "code_switching": 0.10,
        }
        load = sum(signals[k] * weights[k] for k in weights)
        return max(0.0, min(1.0, load))

    def adapt_difficulty(self, load: float, session_config: SessionConfig):
        """認知負荷に基づいてリアルタイムに難易度を調整"""
        if load > 0.7:  # 過負荷
            session_config.ai_speech_rate = "slow"
            session_config.ai_vocabulary_level = "B2"
            session_config.show_feedback_panel = False  # 外在負荷を削減
            session_config.question_complexity = "closed"
            session_config.show_hints = True
        elif load < 0.3:  # 余裕あり
            session_config.ai_speech_rate = "fast"
            session_config.ai_vocabulary_level = "C1+"
            session_config.show_feedback_panel = True
            session_config.question_complexity = "open_multi_part"
            session_config.show_hints = False
```

### 8.4 学習セッション設計（概日リズム対応）

```
時間帯別の推奨セッション構成:

【朝（起床後3時間以内）— 高負荷タスク推奨】
├── ウォームアップ（2分）: 前日の復習（音声産出必須）
├── 瞬間英作文 or パターンプラクティス（5分）
├── AIフリートーク — Complexity/Accuracyモード（7分）
├── リフレクション（90秒）: 静寂・メンタルリプレイ
└── 新規表現の登録

【昼（13:00-15:00）— 低負荷タスク推奨】
├── シャドーイング（リズミックプライミング付き）（5分）
├── もごもごイングリッシュ — 暗黙的リスニング（3分）
├── AIフリートーク — Fluencyモード（5分）
└── リフレクション（90秒）

【夕方（16:00-18:00）— 統合タスク推奨】
├── FSRS復習セッション（5分）
├── パターンプラクティス（5分）
├── リスニングコンプリヘンション（5分）
└── 今日の学習サマリー

【就寝前（就寝45分前）— パッシブレビューのみ】
├── 今日学んだ表現のリスニング（5分、テストなし）
└── 明日の予定確認（カレンダー連携）
```

### 8.5 実験的機能のA/Bテスト設計

エビデンスが限定的な脳科学手法は「実験的機能」として位置づけ、A/Bテストで効果を検証してから全ユーザーに展開する。

```python
class NeuroscienceABTest:
    """
    実験的な脳科学機能のA/Bテストフレームワーク。
    フィーチャーフラグで制御し、統計的有意性が確認されるまでテストを継続。
    """

    EXPERIMENTS = {
        "rhythmic_priming": {
            "description": "シャドーイング前のリズミックビート再生",
            "hypothesis": "ビート再生群はシャドーイング正確度が10%以上向上",
            "control": "ビートなしで通常シャドーイング開始",
            "treatment": "5秒間の英語ストレスリズムビート後にシャドーイング開始",
            "primary_metric": "shadowing_accuracy_score",
            "secondary_metrics": ["response_latency_ms", "user_satisfaction_rating"],
            "min_sample_size": 200,  # 各群100名以上
            "min_duration_days": 28,  # 最低4週間
            "significance_level": 0.05,
        },
        "embodied_gesture": {
            "description": "ジェスチャー連動語彙学習",
            "hypothesis": "ジェスチャー群は7日後のフレーズ想起率が15%以上向上",
            "control": "通常の音声+テキストのみの学習",
            "treatment": "ジェスチャー動作を伴うフレーズ学習",
            "primary_metric": "phrase_recall_rate_7d",
            "secondary_metrics": ["phrase_recall_rate_30d", "spontaneous_use_in_freetalk"],
            "min_sample_size": 160,
            "min_duration_days": 30,
            "significance_level": 0.05,
        },
        "tmr_audio_cues": {
            "description": "復習アイテムへの固有音キュー紐付け（TMR準備）",
            "hypothesis": "キュー音付き復習群はFSRS復習成功率が5%以上向上",
            "control": "キュー音なしの通常復習",
            "treatment": "各アイテムに固有チャイム音を紐付けた復習",
            "primary_metric": "fsrs_review_success_rate",
            "secondary_metrics": ["retention_rate_14d", "review_session_duration"],
            "min_sample_size": 200,
            "min_duration_days": 42,  # 忘却曲線の効果確認に6週間
            "significance_level": 0.05,
        },
        "distinctive_scene_generation": {
            "description": "AI動的生成による弁別的シーン可視化",
            "hypothesis": "弁別的シーン群は類似セッション間のフレーズ混同率が20%以上低減",
            "control": "カテゴリ別の固定ストック画像表示",
            "treatment": "Claude Haikuによるユニークなシーン描写+Unsplash動的検索",
            "primary_metric": "phrase_confusion_rate",
            "secondary_metrics": ["context_recall_accuracy", "session_engagement_time"],
            "min_sample_size": 160,
            "min_duration_days": 21,
            "significance_level": 0.05,
        },
    }

    def evaluate_result(self, experiment_id: str, control_data, treatment_data):
        """
        Welch's t-test + Bayesian posterior で判定。
        p < 0.05 かつ Bayes Factor > 3 で「効果あり」と判定。
        """
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(control_data, treatment_data, equal_var=False)
        effect_size = (treatment_data.mean() - control_data.mean()) / control_data.std()
        return {
            "p_value": p_value,
            "effect_size_cohens_d": effect_size,
            "recommendation": "deploy" if p_value < 0.05 and effect_size > 0.2 else "iterate_or_drop"
        }
```

**テスト結果に基づくアクション:**
| 結果 | アクション |
|------|----------|
| p < 0.05 かつ d > 0.5（大効果） | 全ユーザーに即座展開 |
| p < 0.05 かつ 0.2 < d < 0.5（小〜中効果） | 展開するが、パーソナライズ条件を追加検討 |
| p >= 0.05（有意差なし） | 機能を改善してイテレーション、または廃止 |
| ネガティブ効果（d < 0） | 即座に廃止 |

---

## 9. 外部コンテンツ連携・コンテンツパイプライン

### 9.1 コンテンツ連携アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                   外部コンテンツソース                         │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Guardian │ FMP      │ Tatoeba  │ Podcast  │ ユーザー       │
│ News API │ Earnings │ 文ペア   │ RSS      │ ドキュメント   │
│          │ Trans.   │          │          │ (PDF/PPTX)     │
│          │          │          │          │ カレンダー     │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴───────┬────────┘
     │          │          │          │             │
     ▼          ▼          ▼          ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│              コンテンツ処理パイプライン                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. テキスト抽出・正規化                                │   │
│  │ 2. Claude Haiku — CEFR難易度分類                      │   │
│  │ 3. Claude Haiku — ビジネス関連度スコアリング            │   │
│  │ 4. Oxford API — 語彙定義・IPA取得                     │   │
│  │ 5. Azure TTS — 音声素材生成（速度・声質制御）           │   │
│  │ 6. Claude Sonnet — 練習問題・ディスカッション質問自動生成 │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ PostgreSQL + Azure Blob Storage                       │   │
│  │ ・教材メタデータ、CEFR分類結果                          │   │
│  │ ・生成音声ファイル                                      │   │
│  │ ・FSRS復習アイテムへの自動登録                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 外部コンテンツAPI一覧

#### Phase 1（MVP）— 月額コスト: ~$100-280

| ソース | 用途 | コスト | ライセンス |
|--------|------|--------|-----------|
| **Tatoeba** (データインポート) | 瞬間英作文の文ペア（数十万件の日英対訳） | 無料 | CC BY 2.0（帰属表示必須、商用可） |
| **Oxford Dictionaries API** | 語彙定義、シソーラス、IPA発音記号 | $59-239/月 | 有料プラン=商用利用可 |
| **Strapi** (自己ホスト CMS) | フレーズバンク、シナリオ、文法ルール管理 | ~$20/月(Container App) | MIT License |
| **Unsplash API** | シーン可視化用の画像（会議室、オフィス等） | 無料 | Unsplash License（商用可、帰属表示必須） |
| **Podcast RSS feeds** | リスニング素材（BBC, HBR, Planet Money等） | 無料 | RSS公開=ストリーミング再生可 |
| **Azure TTS** (gpt-4o-mini-tts) | テキストからの音声素材生成 | ~$0.011/分 | Azure契約内 |

#### Phase 2 — 追加月額コスト: ~$500-600

| ソース | 用途 | コスト | ライセンス |
|--------|------|--------|-----------|
| **The Guardian Open Platform** | 全文ニュース記事（ディスカッション素材） | 無料（商用は申請） | 要商用申請 |
| **Financial Modeling Prep** | 決算説明会トランスクリプト（本物のCEO/CFOの英語） | $29/月 | 有料プラン=商用可 |
| **NewsAPI.org** | リアルタイムビジネストピックの取得 | $449/月 | Business plan=商用可 |
| **YouTube Data API v3** | シャドーイング動画ライブラリ | 無料 | 埋め込み再生可。DL/再配布禁止 |
| **MS Graph Calendar API** | ジャストインタイム会議準備（明日の英語会議を練習） | 無料 | Microsoft 365ライセンス前提 |
| **ドキュメントインポート (PDF/PPTX)** | ユーザーの仕事資料から専用語彙リスト自動生成 | ~$20/月(Document Intelligence) | — |
| **Forvo API** | ネイティブ発音録音（もごもごイングリッシュ用） | $2-22/月 | ストリーミング再生可 |

#### Phase 3-4 — 追加月額コスト: ~$200-400

| ソース | 用途 | コスト | ライセンス |
|--------|------|--------|-----------|
| **MS Teams Transcription** (MS Graph) | 実際の会議英語の分析・フィードバック | 無料 | 管理者同意必要 |
| **World Bank / OECD / IMF Data** | マクロ経済ディスカッション素材 | 無料 | CC BY 4.0 |
| **D-ID** (AI Avatar) | 視覚的会話パートナー | $16-67/月 | — |

### 9.3 キラーコンテンツ連携: ドキュメントインポート + カレンダー統合

**B2B最大の差別化機能**: ユーザーの実際の仕事に直結した学習

```
【ドキュメントインポートフロー】
ユーザーが英語プレゼン資料(PPTX)をアップロード
    ↓
PyPDF2/python-pptx でテキスト抽出
    ↓
Claude Sonnet で分析:
├── 専門用語の抽出 + 定義
├── 重要フレーズのCEFRレベル判定
├── 発表時に使えるフレーズの提案
└── Q&Aで想定される質問の生成
    ↓
自動生成:
├── カスタム語彙リスト → FSRS復習に登録
├── 瞬間英作文問題（プレゼン内容に特化）
├── Presentation Q&Aモードのシナリオ
└── 練習用TTS音声
```

```
【カレンダー統合フロー】
MS Graph Calendar API で明日の予定を取得
    ↓
英語会議を自動検出（参加者、タイトル、アジェンダ）
    ↓
プッシュ通知: "明日のBudget Review Meeting (London team) の準備をしましょう"
    ↓
ジャストインタイム学習セッション:
├── 会議テーマに関連する語彙・表現の復習
├── 会議ファシリテーションのパターンプラクティス
├── 想定Q&Aのロールプレイ
└── 参加者の国籍に応じたアクセント練習
```

### 9.4 CMS: Strapi によるコンテンツ管理

非エンジニアでもコンテンツを管理できるヘッドレスCMS。

**管理対象コンテンツタイプ:**

| コンテンツタイプ | フィールド | 用途 |
|----------------|----------|------|
| **Phrase Bank** | カテゴリ、レジスター、CEFRレベル、日本語訳、使用場面、例文対話、音声URL | 会話・パターンプラクティス |
| **Scenario Template** | GPT Realtime APIシステムプロンプト、キーフレーズ、評価基準、難易度 | AI会話モード |
| **Grammar Rule** | 日本語説明、例文、よくある間違い、関連パターン、クイズ | フィードバック・復習 |
| **Cultural Note** | ビジネスマナー、コミュニケーションスタイル差異、地域差、慣用句由来 | 文化的コンテキスト |
| **Sound Pattern** | パターン種別、IPA表記、練習文、音声例（Forvo/TTS） | もごもごイングリッシュ |
| **Flash Translation Set** | 日英文ペア、CEFRレベル、ビジネスコンテキスト、パターンタグ | 瞬間英作文 |

### 9.5 決算説明会トランスクリプト活用（FMP API連携）

**ターゲットユーザーにとって最もリアルな教材**:

```
FMP API から Apple/Google/Microsoft 等の決算説明会テキストを取得
    ↓
Claude Haiku でセグメント分割:
├── CEO/CFO プレゼンテーション部分
├── アナリスト質問部分
├── 経営陣回答部分
    ↓
学習コンテンツとして活用:
├── リスニング素材（TTS合成、速度調整可能）
├── ビジネス語彙抽出（revenue, margin, guidance, YoY等）
├── Presentation Q&Aモードのシナリオテンプレート
├── ディスカッション質問生成（"Apple's revenue guidance についてどう思いますか？"）
└── Financial English パターンプラクティス
```

### 9.6 追加APIエンドポイント

```
# コンテンツインポート
POST   /api/content/import/document    → PDF/PPTXアップロード・分析
GET    /api/content/import/:id/status  → インポート処理状態
GET    /api/content/import/:id/result  → 生成された学習素材

# カレンダー連携
GET    /api/calendar/upcoming          → 今後の英語会議一覧
POST   /api/calendar/prepare/:eventId  → 会議準備セッション生成

# ニュース・トピック
GET    /api/content/news/topics        → 今日のビジネストピック一覧
GET    /api/content/news/:id/material  → トピックから生成された学習素材

# ポッドキャスト
GET    /api/content/podcasts           → 推奨ポッドキャスト一覧
GET    /api/content/podcasts/:id/episodes → エピソード一覧

# CMS同期
POST   /api/content/cms/sync          → Strapi Webhook受信（コンテンツ更新通知）
```

### 9.7 追加データモデル

```sql
-- 外部コンテンツ素材
CREATE TABLE content_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,         -- guardian / fmp / tatoeba / user_upload / podcast
    source_id VARCHAR(255),              -- 外部ソースでのID
    title TEXT NOT NULL,
    content_text TEXT,
    content_url TEXT,                     -- 元記事/音声URL
    audio_blob_url TEXT,                 -- TTS生成音声のBlob URL
    cefr_level VARCHAR(5),               -- A2/B1/B2/C1/C2
    business_relevance_score FLOAT,      -- 0.0-1.0
    categories JSONB,                    -- ["finance", "management", "technology"]
    vocabulary JSONB,                    -- 抽出された語彙リスト
    metadata JSONB,                      -- ソース固有のメタデータ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_content_source ON content_materials(source);
CREATE INDEX idx_content_cefr ON content_materials(cefr_level);

-- ユーザーインポートドキュメント
CREATE TABLE user_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,      -- pdf / pptx / docx
    blob_url TEXT NOT NULL,
    processing_status VARCHAR(20) DEFAULT 'pending', -- pending / processing / completed / failed
    extracted_text TEXT,
    analysis_result JSONB,               -- 語彙分析、フレーズ抽出結果
    generated_materials JSONB,           -- 生成された学習素材のID一覧
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_user_docs_user ON user_documents(user_id);

-- カレンダーイベント連携
CREATE TABLE calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    external_event_id VARCHAR(255),      -- MS Graph Event ID
    title VARCHAR(500),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    participants JSONB,                  -- 参加者リスト
    detected_language VARCHAR(10),       -- 会議の予想言語
    preparation_session_id UUID REFERENCES conversation_sessions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_calendar_user ON calendar_events(user_id, scheduled_at);
```

---

## 10. ビジネスコンテンツライブラリ

### 9.1 シーン別フレーズバンク（AIが動的拡張）
```yaml
meeting_facilitation:
  opening:
    - "Let's get started. The purpose of today's meeting is to..."
    - "Before we dive in, let me walk you through the agenda."
    - "I'd like to make sure we cover three key items today."
  managing_discussion:
    - "That's a valid point. Let me build on that..."
    - "I want to make sure we hear from everyone."
    - "We're running short on time. Let me table that for our next session."
  handling_disagreement:
    - "I see where you're coming from, but let me offer an alternative perspective."
    - "Those are fair concerns. How about we look at the data first?"

negotiation:
  opening_position:
    - "Based on our analysis, we believe a fair starting point would be..."
  concession:
    - "We're willing to be flexible on [X] if you can accommodate [Y]."

casual_business:
  small_talk:
    - "How was your weekend? Did you get up to anything interesting?"
  idioms:
    - "Let's touch base on this later."
    - "We need to move the needle on this."
    - "That's a no-brainer."
```

---

## 10. コスト設計・料金プラン

### 10.1 APIコスト見積もり（ユーザーあたり月額）

#### リアルタイム会話コスト
| 項目 | 単価概算 | Free (5分/日) | Standard (30分/日) | Premium (無制限) |
|------|---------|--------------|-------------------|-----------------|
| GPT Realtime API (音声入力) | ~$0.06/分 | $9.00/月 | $54.00/月 | ~$108/月(60分想定) |
| GPT Realtime API (音声出力) | ~$0.12/分 | $18.00/月 | $108.00/月 | ~$216/月 |

#### フィードバック・ドリルコスト
| 項目 | 単価概算 | Free | Standard | Premium |
|------|---------|------|----------|---------|
| Claude Haiku (フィードバック) | ~$0.001/リクエスト | $0.30/月 | $1.50/月 | $3.00/月 |
| Claude Sonnet (表現改善) | ~$0.01/リクエスト | $0.50/月 | $3.00/月 | $6.00/月 |
| Azure Speech (発音評価) | ~$0.002/評価 | $0.20/月 | $1.00/月 | $2.00/月 |

#### ユーザーあたり月間APIコスト合計
| プラン | API コスト/ユーザー/月 |
|--------|---------------------|
| **Free** | ~$28 |
| **Standard** | ~$168 |
| **Premium** | ~$335 |

### 10.2 インフラコスト（月額）

| サービス | Dev環境 | 100ユーザー | 1,000ユーザー |
|---------|---------|------------|-------------|
| Azure Container Apps (Backend) | $0 (無料枠) | $40-80 | $200-400 |
| Azure Container Apps (Frontend) | $0 (無料枠) | $20-40 | $100-200 |
| PostgreSQL Flexible Server | $30 (Burstable B2ms) | $60 (GP D2s) | $200 (GP D4s + HA) |
| Azure Cache for Redis | $0 (dev) | $25 (Standard C1) | $50 (Standard C2) |
| Azure Key Vault | $2 | $5 | $10 |
| Application Insights | $0 (5GB無料) | $0-10 | $50-200 |
| API Management | $0 (Consumption) | $150 (Basic v2) | $300 (Standard v2) |
| Azure Front Door | $0 (dev不要) | $35 | $35 + データ転送 |
| Container Registry | $5 (Basic) | $5 | $20 (Standard) |
| Azure Blob Storage (音声) | $0 | $5 | $30 |
| **インフラ合計** | **~$37** | **~$405** | **~$1,245** |

### 10.3 料金プラン設計

| | Free | Standard | Premium |
|--|------|----------|---------|
| **月額料金** | ¥0 | ¥2,980 (~$20) | ¥9,800 (~$65) |
| AI会話 | 5分/日 | 30分/日 | 無制限 |
| 瞬間英作文 | 10問/日 | 50問/日 | 無制限 |
| シャドーイング | 3セッション/日 | 無制限 | 無制限 |
| 復習機能 | 基本 | フル | フル |
| 発音評価 | なし | あり | あり + 詳細分析 |
| 週次レポート | なし | あり | あり |
| AIカリキュラム最適化 | なし | 基本 | 高度 |

### 10.4 損益分岐分析

| シナリオ | ユーザー数 | 収益/月 | APIコスト/月 | インフラ/月 | 粗利 |
|---------|-----------|---------|-------------|-----------|------|
| 初期 | 100 (50 Free, 40 Std, 10 Prm) | ¥217,200 | $8,110 (~¥1.2M) | $405 (~¥60K) | **赤字** |
| 中期 | 500 (100 Free, 300 Std, 100 Prm) | ¥1,874,000 | $55,400 (~¥8.3M) | $800 (~¥120K) | **赤字** |
| 成熟期 | 2,000 (200 Free, 1200 Std, 600 Prm) | ¥9,456,000 | $221,600 (~¥33.2M) | $1,500 (~¥225K) | **赤字** |

**重大な問題**: 現在の価格設定ではGPT Realtime APIのコストが高すぎて損益が合わない。

### 10.5 コスト最適化戦略（必須）

| 戦略 | 効果 | 実装優先度 |
|------|------|-----------|
| **Provisioned Throughput (PTU) 予約** | Realtime APIを月額予約で30-60%コスト削減 | Phase 2 (ユーザー増加後) |
| **会話時間のハード制限** | Free: 5分/日、Standard: 30分/日を厳密に制御 | Phase 1 (MVP) |
| **フィードバックのバッチ化** | 毎ターンではなく3ターンごとにフィードバック生成 | Phase 1 |
| **音声なしモード推奨** | テキストのみ会話はRealtime API不要、通常LLM利用 | Phase 1 |
| **テキストモードでのClaude Haiku利用** | テキスト会話はHaiku ($0.25/MTok) で大幅コスト削減 | Phase 1 |
| **バッチAPIでのコンテンツ事前生成** | 瞬間英作文問題等を50%割引のBatch APIで事前生成 | Phase 1 |
| **レスポンスキャッシュ** | 類似の文法説明・表現改善をRedisキャッシュ | Phase 2 |
| **料金プランの見直し** | 音声会話Premiumは ¥14,800/月以上が必要 | Phase 2 |

### 10.6 改訂版料金プラン（コスト最適化後）

| | Free | Standard | Premium |
|--|------|----------|---------|
| **月額料金** | ¥0 | ¥4,980 (~$33) | ¥14,800 (~$99) |
| AI音声会話 | なし | 15分/日 | 60分/日 |
| AIテキスト会話 | 10回/日 | 30回/日 | 無制限 |
| 瞬間英作文 | 10問/日 | 無制限 | 無制限 |
| 発音評価 | なし | あり | あり |
| APIコスト/ユーザー/月 | ~$3 | ~$55 | ~$160 |
| **粗利率** | N/A (リード獲得) | ~40% | ~38% |

---

## 11. 非機能要件

### 11.1 パフォーマンス
| メトリクス | 目標値 | 測定方法 |
|-----------|--------|---------|
| 音声会話レイテンシ（Realtime API） | <200ms | WebRTC接続のRTT |
| テキスト会話レスポンス | <2秒 | API応答時間 |
| フィードバック表示 | <3秒（会話に遅延して可） | 非同期処理完了時間 |
| ページ読み込み（初回） | <3秒 | Lighthouse Performance |
| ページ読み込み（遷移） | <500ms | Next.js クライアントナビゲーション |
| WebSocket接続安定性 | 99.5%以上 | Application Insights |
| Lighthouse スコア | Performance >80, A11y >90 | CI自動計測 |

### 11.2 可用性・スケーラビリティ
| 要件 | 目標 | 実現方法 |
|------|------|---------|
| 稼働率 | 99.9% (月間ダウンタイム <44分) | Container Apps + PostgreSQL HA |
| 同時接続数 | 初期100、最大1,000 | Container Apps オートスケール |
| データ保持 | 会話テキスト: 無期限、音声: 90日後自動削除 | Azure Blob Lifecycle Policy |
| バックアップ | PostgreSQL: 日次自動 (35日保持) | Azure Flexible Server Backup |
| DR | RPO: 1時間、RTO: 4時間 | Geo-redundant backup |

### 11.3 アクセシビリティ
- テキストのみモード（音声が使えない環境用）
- フォントサイズ調整
- ハイコントラストモード
- WCAG 2.1 AA準拠

---

## 12. セキュリティ・コンプライアンス

### 12.1 認証・認可
| 要件 | 実装 |
|------|------|
| ユーザー認証 | Microsoft Entra External ID (Google / Email / Apple) |
| API認証 | JWT (Entra ID発行) + API Management検証 |
| サービス間認証 | Managed Identity (パスワードレス) |
| セッション管理 | Redis ベースセッション、30分タイムアウト |
| MFA | Enterprise プラン向けにオプション提供 |

### 12.2 データ保護
| 項目 | 対策 |
|------|------|
| 通信暗号化 | TLS 1.3 (Azure Front Door で終端) |
| データ暗号化 (at-rest) | Azure Storage Service Encryption (AES-256) |
| データベース暗号化 | PostgreSQL Transparent Data Encryption |
| シークレット管理 | Azure Key Vault (Managed Identity アクセス) |
| 音声データ | 90日後自動削除、Blob Lifecycle Policy |
| PII保護 | メールアドレス暗号化、ログからの個人情報マスキング |

### 12.3 ネットワークセキュリティ
| 項目 | 対策 |
|------|------|
| DDoS防御 | Azure Front Door Standard (L3/L4 DDoS Protection) |
| WAF | Azure Front Door Premium (将来的にアップグレード) |
| レート制限 | API Management ポリシー (プラン別) |
| ネットワーク分離 | Container Apps VNet統合 + Private Endpoints (Production) |
| DB接続 | Private Link経由のみ (Production) |

### 12.4 コンプライアンス
| 規制 | 対応 |
|------|------|
| 個人情報保護法 | ユーザーデータの利用目的明示、同意取得、削除権 |
| GDPR | データポータビリティ、忘れられる権利、DPO設置 |
| SOC2 Type II | 監査証跡、アクセス制御、変更管理 (将来対応) |
| ISO 27001 | Azure の認証を活用 |

### 12.5 セキュリティスキャン
| スキャン | ツール | 頻度 |
|---------|--------|------|
| 依存関係脆弱性 | Dependabot + pip-audit + npm audit | 毎PR + 週次 |
| SAST (静的解析) | CodeQL (GitHub Advanced Security) | 毎PR |
| コンテナ脆弱性 | Trivy | 毎デプロイ + 日次 |
| シークレット漏洩 | TruffleHog | 毎PR |
| ライセンス監査 | dependency-review-action | 毎PR |

---

## 13. 監視・オブザーバビリティ

### 13.1 監視スタック
```
┌─────────────────────────────────────────┐
│        Azure Monitor                     │
├──────────────┬──────────────────────────┤
│ Application  │ Log Analytics             │
│ Insights     │ Workspace                 │
│              │                           │
│ - 分散トレース│ - 構造化ログ集約          │
│ - ライブメトリクス│ - KQLクエリ             │
│ - 依存関係マップ│ - アラートルール         │
│ - カスタムイベント│ - ダッシュボード        │
├──────────────┴──────────────────────────┤
│ OpenTelemetry SDK                        │
│ (FastAPI + Next.js 両方に組み込み)         │
└─────────────────────────────────────────┘
```

### 13.2 カスタムメトリクス
```python
# FastAPIで追跡するカスタムメトリクス
custom_metrics = {
    # ビジネスメトリクス
    "conversation_sessions_started": Counter,        # 会話セッション開始数
    "conversation_sessions_completed": Counter,      # 完了数
    "conversation_duration_seconds": Histogram,      # セッション長
    "flash_translation_accuracy": Histogram,         # 瞬間英作文正答率
    "pronunciation_score_avg": Gauge,                # 平均発音スコア
    "daily_active_users": Gauge,                     # DAU
    "review_completion_rate": Gauge,                 # 復習完了率

    # APIコストメトリクス
    "api_cost_realtime_usd": Counter,                # Realtime APIコスト累計
    "api_cost_claude_usd": Counter,                  # Claudeコスト累計
    "api_cost_speech_usd": Counter,                  # Speech Servicesコスト累計
    "api_tokens_per_session": Histogram,             # セッションあたりトークン数

    # パフォーマンスメトリクス
    "realtime_api_latency_ms": Histogram,            # Realtime APIレイテンシ
    "feedback_generation_latency_ms": Histogram,     # フィードバック生成レイテンシ
    "websocket_connection_errors": Counter,          # WebSocket接続エラー
}
```

### 13.3 アラートルール
| アラート | 条件 | 重要度 | 通知先 |
|---------|------|--------|--------|
| APIエラー率 | >5% (5分間) | Critical | Slack + PagerDuty |
| レスポンス遅延 | P95 > 5秒 | Warning | Slack |
| WebSocket切断率 | >10% (10分間) | Critical | Slack + PagerDuty |
| DB接続プール枯渇 | >90% | Critical | Slack + PagerDuty |
| 日次APIコスト超過 | >$500/日 | Warning | Email + Slack |
| 月次APIコスト超過 | >$10,000/月 | Critical | Email + Slack + PagerDuty |
| ディスク使用率 | >80% | Warning | Slack |
| DAU急減 | 前日比-30% | Info | Slack |

---

## 14. GitHub リポジトリ・CI/CD

### 14.1 リポジトリ構成（モノレポ）
```
fluentedge/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # PRチェック (lint, test, build)
│   │   ├── deploy-dev.yml            # develop → dev環境 自動デプロイ
│   │   ├── deploy-staging.yml        # staging → ステージング 自動デプロイ
│   │   ├── deploy-production.yml     # 手動トリガー + 承認ゲート
│   │   ├── db-migration.yml          # DBマイグレーション（手動）
│   │   └── security-scan.yml         # 日次セキュリティスキャン
│   ├── actions/
│   │   └── setup-env/
│   │       └── action.yml            # 共通セットアップ（再利用可能）
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── pull_request_template.md
│
├── frontend/                          # Next.js 15 App Router
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── talk/
│   │   ├── listening/
│   │   ├── speaking/
│   │   ├── review/
│   │   ├── analytics/
│   │   └── settings/
│   ├── components/
│   │   ├── ui/                       # shadcn/ui
│   │   ├── chat/
│   │   ├── audio/
│   │   ├── drill/
│   │   └── analytics/
│   ├── lib/
│   │   ├── api.ts
│   │   ├── audio.ts
│   │   ├── websocket.ts
│   │   └── stores/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   └── package.json
│
├── backend/                           # FastAPI (Python 3.11)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── talk.py
│   │   │   ├── listening.py
│   │   │   ├── speaking.py
│   │   │   ├── review.py
│   │   │   ├── analytics.py
│   │   │   └── curriculum.py
│   │   ├── services/
│   │   │   ├── realtime_service.py   # GPT Realtime API wrapper
│   │   │   ├── claude_service.py     # Claude API (via Azure AI Foundry)
│   │   │   ├── speech_service.py     # Azure Speech Services
│   │   │   ├── spaced_repetition.py
│   │   │   ├── analytics_service.py
│   │   │   ├── cost_tracker.py       # APIコスト追跡
│   │   │   └── curriculum_service.py
│   │   ├── prompts/
│   │   │   ├── conversation.py
│   │   │   ├── flash_translation.py
│   │   │   ├── expression_upgrade.py
│   │   │   └── curriculum.py
│   │   ├── middleware/
│   │   │   ├── auth.py               # Entra ID JWT検証
│   │   │   ├── rate_limit.py
│   │   │   └── cost_guard.py         # 使用量制限ミドルウェア
│   │   └── websocket/
│   │       └── talk_handler.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── infra/                             # Infrastructure as Code (Bicep)
│   ├── modules/
│   │   ├── container-app.bicep
│   │   ├── container-app-environment.bicep
│   │   ├── container-registry.bicep
│   │   ├── key-vault.bicep
│   │   ├── postgresql.bicep
│   │   ├── redis.bicep
│   │   ├── api-management.bicep
│   │   ├── front-door.bicep
│   │   └── monitoring.bicep
│   ├── environments/
│   │   ├── dev.bicepparam
│   │   ├── staging.bicepparam
│   │   └── production.bicepparam
│   └── main.bicep
│
├── docker-compose.yml                 # ローカル開発用
├── Makefile
└── README.md
```

### 14.2 ブランチ戦略
```
main (protected) ──── 本番リリース (タグ付き: v1.0.0, v1.1.0)
  │
develop (protected) ── 統合ブランチ、dev環境に自動デプロイ
  │
feature/FE-123 ─────── 機能開発（developからブランチ、developへPR）
  │
hotfix/FE-456 ──────── 緊急修正（mainからブランチ、main+developへマージ）
```

### 14.3 ブランチ保護ルール

| ルール | main | develop |
|--------|------|---------|
| PRレビュー必須 | 2名 | 1名 |
| ステータスチェック必須 | frontend-test, backend-test, e2e-tests, codeql | frontend-test, backend-test |
| 最新ブランチ必須 | Yes | Yes |
| フォースプッシュ禁止 | Yes | Yes |
| 削除禁止 | Yes | Yes |
| CODEOWNERS レビュー | Yes | No |

### 14.4 CI/CDパイプライン概要

```
[PR作成]
    ↓
[CI Pipeline] ─────────────────────────────────────────
├── 変更検出 (paths-filter)
├── Frontend: ESLint → TypeScript → Vitest → Build
├── Backend: Ruff → mypy → pytest (PostgreSQL/Redis) → Alembic migration test
├── E2E: Playwright (frontend + backend 起動)
├── Security: CodeQL SAST → dependency-review → license check
└── Infra: Bicep lint → what-if dry run
    ↓ (全パス + レビュー承認)
[Merge to develop]
    ↓
[Deploy to Dev] ───────────────────────────────────────
├── Docker build → ACR push
├── Alembic migration (Container Apps Job)
└── Container Apps deploy (dev環境)
    ↓
[Merge to main]
    ↓
[Deploy to Staging] ───────────────────────────────────
├── Docker build → ACR push
├── Alembic migration
└── Container Apps deploy (staging環境)
    ↓
[Deploy to Production] (手動トリガー + 承認ゲート) ────
├── ステージングヘルスチェック
├── 承認者レビュー (GitHub Environment protection)
├── DB バックアップ
├── Alembic migration
├── Blue-Green deploy (0%トラフィック → ヘルスチェック → 100%切替)
├── スモークテスト (Playwright)
└── GitHub Release 作成
```

### 14.5 認証方式: OIDC (パスワードレス)

GitHub Actions → Azure の認証にOpenID Connect (OIDC)を使用。クライアントシークレット不要。

```yaml
# GitHub Actionsでの使用例
- name: Azure Login (OIDC)
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**GitHub Secretsに必要な値（環境ごと）:**
- `AZURE_CLIENT_ID` — Entra IDアプリ登録のクライアントID
- `AZURE_TENANT_ID` — Entra IDテナントID
- `AZURE_SUBSCRIPTION_ID` — AzureサブスクリプションID

※ クライアントシークレットは一切不要（OIDC Federated Credential）

---

## 15. Infrastructure as Code（Bicep）

### 15.1 メインテンプレート構成
```bicep
// infra/main.bicep
targetScope = 'resourceGroup'

@allowed(['dev', 'staging', 'production'])
param environment string
param location string = resourceGroup().location
param projectName string = 'fluentedge'

var envConfig = {
  dev: {
    containerCpu: '0.5'
    containerMemory: '1.0Gi'
    minReplicas: 0           // Scale-to-zero
    maxReplicas: 3
    pgSku: 'Standard_B2ms'
    pgTier: 'Burstable'
    pgStorageGB: 32
    pgHaMode: 'Disabled'
  }
  staging: {
    containerCpu: '1.0'
    containerMemory: '2.0Gi'
    minReplicas: 1
    maxReplicas: 5
    pgSku: 'Standard_D2s_v3'
    pgTier: 'GeneralPurpose'
    pgStorageGB: 64
    pgHaMode: 'Disabled'
  }
  production: {
    containerCpu: '2.0'
    containerMemory: '4.0Gi'
    minReplicas: 2
    maxReplicas: 20
    pgSku: 'Standard_D4s_v3'
    pgTier: 'GeneralPurpose'
    pgStorageGB: 256
    pgHaMode: 'ZoneRedundant'
  }
}

// Modules: ACR, Key Vault, PostgreSQL, Redis,
// Container Apps Environment, Backend App, Frontend App,
// API Management, Front Door, Monitoring
```

### 15.2 環境別パラメータ
```bicep
// infra/environments/dev.bicepparam
using '../main.bicep'
param environment = 'dev'
param location = 'eastus2'        // Realtime API + Claude 利用可能
param projectName = 'fluentedge'

// infra/environments/production.bicepparam
using '../main.bicep'
param environment = 'production'
param location = 'eastus2'
param projectName = 'fluentedge'
```

---

## 16. テスト戦略

### 16.1 テストピラミッド

| レイヤー | ツール | 対象 | カバレッジ目標 |
|---------|--------|------|--------------|
| **Unit** | pytest (backend), Vitest (frontend) | 個別関数・コンポーネント | 80%+ |
| **Integration** | pytest + PostgreSQL/Redis service containers | API エンドポイント、DB操作 | 主要フロー網羅 |
| **E2E** | Playwright | ユーザーフロー全体 | 主要5シナリオ |
| **Smoke** | Playwright (サブセット) | 本番デプロイ後の基本動作確認 | 認証・会話開始・ダッシュボード |

### 16.2 テスト対象の優先順位
1. **認証フロー** — ログイン/ログアウト/トークンリフレッシュ
2. **会話セッション** — 開始/メッセージ送受信/終了/保存
3. **忘却曲線アルゴリズム** — SM-2計算の正確性
4. **APIコスト追跡** — 使用量計算・制限の正確性
5. **瞬間英作文** — 問題生成・採点ロジック
6. **レート制限** — プラン別制限の動作

### 16.3 CIでのテスト実行

```yaml
# backendテスト: PostgreSQL + Redis service containers使用
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpassword
      POSTGRES_DB: testdb
  redis:
    image: redis:7-alpine

# フロー:
# 1. Alembic migration → テストDB構築
# 2. pytest --cov=app → カバレッジ計測
# 3. Codecov アップロード
```

---

## 17. 開発フェーズ（改訂版）

### Phase 0: 基盤構築（2週間）
- [x] GitHubリポジトリ初期化（モノレポ構成）
- [x] Bicep IaC でDev環境プロビジョニング
  - Container Apps, PostgreSQL, Redis, Key Vault, ACR
- [x] CI/CDパイプライン構築（ci.yml + deploy-dev.yml）
- [x] Docker開発環境（docker-compose.yml）
- [x] Backend骨格: FastAPI + Alembic + ヘルスチェック
- [x] Frontend骨格: Next.js 15 + Tailwind + shadcn/ui
- [x] 認証: Microsoft Entra External ID 基本設定

### Phase 1: MVP — テキスト会話（6週間）
- [x] DBスキーマ作成（Alembic migration）
- [x] Claude API連携（Azure AI Foundry経由）
  - テキストベースAIフリートーク（Casual Chat モードのみ）
  - Claude Haiku でフィードバック生成（非同期）
- [x] 会話セッションCRUD (開始/メッセージ/終了/履歴)
- [x] 瞬間英作文（テキスト入力版、レベル1-3）
- [x] 忘却曲線ベース復習システム（SM-2アルゴリズム）
- [x] 簡易ダッシュボード（学習履歴リスト + ストリーク表示）
- [x] APIコスト追跡 + 使用量制限ミドルウェア
- [x] 料金プラン（Free / Standard 区分のみ、決済は後）
- [x] E2Eテスト（認証 → 会話 → 復習 の基本フロー）

### Phase 2: 音声統合（6週間）
- [x] GPT Realtime API統合（WebRTC接続）
- [x] Azure Speech Services 発音評価統合
- [x] 音声付きAIフリートーク
- [x] シャドーイング機能（速度調整付きTTS再生）
- [x] 会話モード追加: Meeting Facilitation, Debate
- [x] パターンプラクティス機能
- [x] Staging環境構築 + デプロイパイプライン

### Phase 3: 学習最適化 + エンタープライズ（6週間）
- [x] もごもごイングリッシュ
- [x] アナリティクスダッシュボード（Recharts）
- [x] AIカリキュラム自動最適化
- [x] 週次/月次レポート
- [x] Production環境構築（HA, Private Endpoints）
- [x] Azure Front Door + API Management 設定
- [x] 本番デプロイパイプライン（Blue-Green + 承認ゲート）
- [x] 決済統合（Stripe）

### Phase 4: 高度な機能（4週間）
- [x] 発音トレーニング（詳細音素分析）
- [x] リスニングコンプリヘンション
- [x] 残りの会話モード実装
- [x] PWA対応（Service Worker, プッシュ通知）
- [x] Provisioned Throughput 最適化
- [x] 負荷テスト + パフォーマンスチューニング

**合計: 約24週間（6ヶ月）**

---

## 18. 実装ガイド

### 18.1 実装優先順位
1. **インフラ基盤 (Phase 0)** — Bicep + CI/CD を最初に整備
2. **バックエンドAPI骨格** — FastAPI + 認証 + DB
3. **Claude API連携（テキスト会話）** — MVP核心機能
4. **フロントエンドUI** — shadcn/ui + Tailwind CSS
5. **コスト管理基盤** — APIコスト追跡 + 使用量制限
6. **音声統合 (Phase 2)** — GPT Realtime API + Azure Speech
7. **アナリティクス + 最適化 (Phase 3)**

### 18.2 環境変数（Azure Key Vault管理）
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<Key Vault managed>
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime
AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT=gpt-4o-transcribe
AZURE_OPENAI_TTS_DEPLOYMENT=gpt-4o-mini-tts

# Claude (Azure AI Foundry Marketplace)
AZURE_AI_FOUNDRY_ENDPOINT=https://<endpoint>.services.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=<Key Vault managed>
CLAUDE_SONNET_MODEL=claude-sonnet-4-5-20250929
CLAUDE_HAIKU_MODEL=claude-haiku-4-5-20251001
CLAUDE_OPUS_MODEL=claude-opus-4-6

# Azure Speech Services
AZURE_SPEECH_KEY=<Key Vault managed>
AZURE_SPEECH_REGION=eastus2

# Database
DATABASE_URL=<Key Vault managed>
REDIS_URL=<Key Vault managed>

# Auth
AZURE_ENTRA_CLIENT_ID=<app registration>
AZURE_ENTRA_TENANT_ID=<tenant>
NEXTAUTH_SECRET=<Key Vault managed>

# Application
ENVIRONMENT=dev|staging|production
LOG_LEVEL=INFO
```

### 18.3 重要な実装ノート

1. **GPT Realtime API (WebRTC)**
   - ブラウザから直接Azure OpenAIに接続（バックエンド経由不要）
   - バックエンドはセッショントークン発行のみを担当
   - セッション上限30分 → 25分で警告、自動延長ロジック実装
   - semantic_vad モードでAIベースの発話終了検出を使用

2. **フィードバック生成の分離**
   - 会話応答はRealtime APIが即座に返す
   - フィードバック（文法・表現改善）はClaude Haikuで非同期生成（~2秒遅延許容）
   - フィードバックはWebSocket経由でフロントに push

3. **コスト管理**
   - 全APIコールを `api_usage_log` テーブルに記録
   - `cost_guard.py` ミドルウェアがプラン別使用量を検証
   - Redis に当日使用量をキャッシュ（高速チェック）
   - 月次リセットは `api_usage_reset_at` フィールドで管理

4. **モバイル対応**
   - iOS Safariの音声入力制限: WebRTCは対応、MediaRecorderはpolyfill検討
   - AudioContextの初期化はユーザーインタラクション後（ブラウザポリシー）
   - タッチ操作最適化: マイクボタンは最低44x44px

5. **エラーハンドリング**
   - Realtime API接続断: 自動再接続（exponential backoff, max 3回）
   - ネットワーク断時: 会話データローカル保存（IndexedDB） + 再接続時同期
   - API制限到達時: ユーザーにプランアップグレード案内表示

---

*本仕様書はエンタープライズレベルのAI英会話トレーニングサービスとして設計されています。Phase 0（基盤構築）から順序立てて実装してください。*
