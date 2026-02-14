# FluentEdge 外部コンテンツソース & API 調査レポート

**調査日**: 2026-02-14
**対象**: AI英会話トレーニングアプリ「FluentEdge」に統合可能な外部コンテンツソースとAPI
**注意**: 本レポートはClaude Opus 4.6の訓練データ（2025年5月まで）に基づく。契約前に各サービスの最新情報を公式サイトで必ず確認すること。

---

## 目次

1. [News & Business Content APIs](#1-news--business-content-apis)
2. [Speech & Audio Content Sources](#2-speech--audio-content-sources)
3. [Language Learning Content APIs](#3-language-learning-content-apis)
4. [Real-time Data Sources for Dynamic Content](#4-real-time-data-sources-for-dynamic-content)
5. [User-Generated / Enterprise Content Integration](#5-user-generated--enterprise-content-integration)
6. [Content Management System (CMS) for Admin](#6-content-management-system-cms-for-admin)
7. [Multimedia Content](#7-multimedia-content)
8. [FluentEdge統合優先度マトリクス](#8-fluentedge統合優先度マトリクス)
9. [ライセンス・法的考慮事項まとめ](#9-ライセンス法的考慮事項まとめ)

---

## 1. News & Business Content APIs

### 1.1 NewsAPI.org

| 項目 | 詳細 |
|------|------|
| **URL** | https://newsapi.org/ |
| **概要** | 150,000+のニュースソースを集約。BBC, CNN, Reuters, Bloomberg等の記事メタデータ・スニペットを取得可能 |
| **無料枠** | Developer: 100リクエスト/日、1ヶ月前までの記事、開発用のみ（商用不可） |
| **有料プラン** | Business: $449/月（250,000リクエスト/月、リアルタイム記事、商用利用可）、Enterprise: 要相談 |
| **レート制限** | Developer: 100リクエスト/24時間、Business: ~500リクエスト/時（目安） |
| **ライセンス** | 無料プランは非商用のみ。商用利用はBusinessプラン以上が必須。記事の全文は提供せず、タイトル・概要・URL・画像のみ。全文取得にはソース元のスクレイピングが必要（各サイトのToS確認が必要） |
| **統合難易度** | Easy — RESTful JSON API、SDKあり（Python, JS） |
| **FluentEdge価値** | ★★★★☆ — 最新のビジネスニュース見出し・概要をリスニング・ディスカッションのトピック素材として活用。「今日のニュースについてディスカッション」機能に最適。ただし全文が取れないため、AI生成コンテンツと組み合わせる必要あり |

### 1.2 New York Times APIs

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.nytimes.com/ |
| **概要** | Article Search, Top Stories, Most Popular, Books, Movie Reviews等の複数API提供 |
| **無料枠** | 全API無料（APIキー登録制）、500リクエスト/日、5リクエスト/分 |
| **有料プラン** | なし（無料APIのみ） |
| **レート制限** | 500リクエスト/日、5リクエスト/分 |
| **ライセンス** | 記事メタデータ・スニペットのみ提供。全文表示には NYT のサブスクリプション+リダイレクトが必要。商用利用の場合、NYTのAPI利用規約に準拠。「NYT APIを利用しています」旨の表示義務あり。コンテンツの再配布・キャッシュに制限あり |
| **統合難易度** | Easy — シンプルなREST API、レスポンスはJSON |
| **FluentEdge価値** | ★★★★☆ — ビジネス・テクノロジー・経済記事の高品質な見出し・概要を取得可能。ディスカッション素材として優れる。トピックの多様性も魅力 |

### 1.3 The Guardian Open Platform

| 項目 | 詳細 |
|------|------|
| **URL** | https://open-platform.theguardian.com/ |
| **概要** | The Guardianの全記事にアクセスできるオープンAPI。全文取得可能（開発者キー） |
| **無料枠** | Developer: 12リクエスト/分、全文取得可（非商用）。Internal: 商用利用可、ガーディアンのコンテンツをアプリ内表示可能（ただし事前承認制） |
| **有料プラン** | 基本無料。大規模商用利用はPartnership契約が必要（要問い合わせ） |
| **レート制限** | Developer: 12リクエスト/分、1日上限なし |
| **ライセンス** | Developer Tierは非商用のみ。Commercial利用はApproval必要。記事全文取得が可能な点が他ニュースAPIとの大きな差別化ポイント。Creative Commons的なオープン方針 |
| **統合難易度** | Easy — RESTful API、JSON/XML対応 |
| **FluentEdge価値** | ★★★★★ — **全文が取得できるため最も価値が高い**。リスニング素材のテキスト源、リーディング教材、ディスカッションネタとして直接利用可能。英国英語のため、アメリカ英語との比較学習にも使える |

### 1.4 Reuters / Bloomberg API

| 項目 | 詳細 |
|------|------|
| **URL** | Reuters: https://www.reutersagency.com/en/platforms/api/ , Bloomberg: エンタープライズのみ |
| **概要** | プレミアムニュースフィード。金融・ビジネスニュースに特化 |
| **無料枠** | なし |
| **有料プラン** | Reuters: Connect APIは年間数万ドル〜（エンタープライズ契約）。Bloomberg: Bloomberg Terminal契約（月額$2,000+）が前提、API利用は追加料金 |
| **レート制限** | 契約内容による |
| **ライセンス** | 厳格なエンタープライズライセンス。再配布は原則不可。アプリ内での表示にも個別契約が必要 |
| **統合難易度** | Hard — 高額な契約、厳格なライセンス管理 |
| **FluentEdge価値** | ★★☆☆☆ — コンテンツの質は最高だが、コスト対効果が見合わない。初期フェーズでは不要。**代替として NewsAPI や Guardian API で十分** |

### 1.5 Financial Times API

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.ft.com/ |
| **概要** | FTコンテンツのAPI。ヘッドライン、メタデータ、一部の記事内容 |
| **無料枠** | なし（FT企業ライセンスが前提） |
| **有料プラン** | FTのContent APIは法人向けライセンスのみ。年間数万ポンド〜 |
| **レート制限** | 契約依存 |
| **ライセンス** | 極めて厳格。教育目的でも商用アプリ内利用には特別契約が必要 |
| **統合難易度** | Hard |
| **FluentEdge価値** | ★★☆☆☆ — ビジネス英語としては最高品質だがコスト対効果で現実的でない |

### 1.6 TED Talks

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.ted.com/talks （公式APIは2023年頃に非推奨化） |
| **概要** | TEDトーク動画の字幕・メタデータ |
| **無料枠** | 公式APIはdeprecated。しかし以下の代替手段がある: (1) TED.comのRSSフィード（無料）、(2) ted2srt.org等のコミュニティプロジェクト、(3) YouTubeのTED公式チャンネルからYouTube Data API経由 |
| **有料プラン** | TEDとの直接パートナーシップ契約（TEd@Work: 法人向け学習プラットフォーム、年間契約） |
| **レート制限** | RSS: なし。YouTube経由: YouTube APIの制限に準拠 |
| **ライセンス** | TEDトークはCreative Commons BY-NC-ND 4.0。非商用・改変不可で利用可能。字幕テキストの教育目的利用はグレーゾーン。TEDと教育パートナーシップ契約を結ぶのが安全 |
| **統合難易度** | Medium — 公式APIがないため、YouTube API + スクレイピングの組み合わせが必要 |
| **FluentEdge価値** | ★★★★★ — **リスニング・シャドーイング素材として極めて高価値**。高品質な英語スピーチ、多様なトピック（テクノロジー、ビジネス、科学）、字幕データが教材化に最適。オーバースピードトレーニングの素材として理想的 |

### 1.7 YouTube Data API v3

| 項目 | 詳細 |
|------|------|
| **URL** | https://developers.google.com/youtube/v3 |
| **概要** | YouTube動画のメタデータ、字幕、チャンネル情報を取得 |
| **無料枠** | 10,000ユニット/日（無料のGoogleアカウントで取得可能）。検索=100ユニット、動画詳細=1ユニット、字幕リスト=50ユニット |
| **有料プラン** | 基本無料。クォータ増加はGoogleへの申請（無料の場合が多いが審査あり） |
| **レート制限** | 10,000ユニット/日（デフォルト）。字幕取得は youtube-dl / yt-dlp 等の別ツールが必要な場合あり |
| **ライセンス** | YouTube APIサービス利用規約に準拠。動画の埋め込み表示は許可。ダウンロード・再配布は禁止。字幕データの取得・テキスト化はグレーゾーン（YouTube公式の字幕APIではcaption.download権限が必要でOAuth認証が必須） |
| **統合難易度** | Medium — API自体は簡単だが、字幕テキスト取得にはOAuth + 権限管理が必要 |
| **FluentEdge価値** | ★★★★★ — **最大のコンテンツ源**。ビジネス英語チャンネル（Harvard Business Review, Bloomberg, CNBC, TED等）の膨大な無料動画にアクセス可能。埋め込み再生でシャドーイング素材に。字幕付き動画を速度調整して練習 |

### 1.8 Podcast RSS Feeds（ビジネス英語系）

| 項目 | 詳細 |
|------|------|
| **URL** | 各ポッドキャストのRSSフィード（一例: HBR IdeaCast, The Economist Podcasts, Freakonomics Radio, Planet Money） |
| **概要** | RSSフィードから音声ファイルURL、エピソードタイトル、概要（show notes）を取得 |
| **無料枠** | RSS解析自体は無料。音声ファイルも公開URLから取得可能 |
| **有料プラン** | なし（ただし音声ファイルの再配布は各ポッドキャストのライセンスによる） |
| **レート制限** | 技術的制限なし（常識的なポーリング間隔を守る） |
| **ライセンス** | **重要**: ポッドキャスト音声の「再生」は通常許可されている（公開RSSフィードであるため）が、「再配布」「改変」「アプリ内ホスティング」は各コンテンツオーナーの許諾が必要。リンク・埋め込み再生は通常OK。ダウンロードしてサーバーにキャッシュするのは問題になる可能性あり |
| **統合難易度** | Easy — RSS解析はfeedparserライブラリ等で簡単 |
| **FluentEdge価値** | ★★★★★ — **リスニング素材として最高クラス**。実際のビジネス会話・ディスカッションを素材にできる。以下が特に有用: |

**推奨ポッドキャスト一覧（ビジネス英語学習向け）:**

| ポッドキャスト | 内容 | 難易度 | RSS |
|-------------|------|--------|-----|
| **HBR IdeaCast** | ハーバード・ビジネスレビュー公式。経営・リーダーシップ | C1 | https://feeds.harvardbusiness.org/harvardbusiness/ideacast |
| **The Economist Podcasts** | 世界経済・政治の分析 | C1-C2 | 複数フィード（Babbage, Money Talks等） |
| **Planet Money (NPR)** | 経済をわかりやすく解説 | B2-C1 | https://feeds.npr.org/510289/podcast.xml |
| **Freakonomics Radio** | 経済学の視点で社会分析 | C1 | https://feeds.simplecast.com/Y8lFbOT4 |
| **Business Wars** | 企業間競争のストーリー | B2-C1 | Wondery配信 |
| **How I Built This (NPR)** | 起業家インタビュー | B2-C1 | https://feeds.npr.org/510313/podcast.xml |
| **Masters of Scale** | Reid Hoffmanによるスケーリング論 | C1 | https://rss.art19.com/masters-of-scale |
| **TED Radio Hour** | TEDトークの深掘り | B2-C1 | https://feeds.npr.org/510298/podcast.xml |
| **BBC Global News Podcast** | BBC世界ニュース日次 | C1 | https://podcasts.files.bbci.co.uk/p02nq0gn.rss |
| **6 Minute English (BBC)** | BBC公式英語学習ポッドキャスト | B1-B2 | https://podcasts.files.bbci.co.uk/p02pc9tn.rss |
| **All Ears English** | 英語学習に特化 | B2 | https://www.allearsenglish.com/feed/podcast/ |
| **Business English Pod** | ビジネス英語シーン別 | B2-C1 | 有料サブスクリプション |

---

## 2. Speech & Audio Content Sources

### 2.1 LibriVox / LibriSpeech

| 項目 | 詳細 |
|------|------|
| **URL** | LibriVox: https://librivox.org/ , LibriSpeech: https://www.openslr.org/12 |
| **概要** | LibriVox: ボランティアによるパブリックドメイン書籍の朗読。LibriSpeech: LibriVoxから派生した音声認識研究用データセット（約1,000時間） |
| **無料枠** | 完全無料（パブリックドメイン） |
| **有料プラン** | なし |
| **レート制限** | なし（ダウンロード可） |
| **ライセンス** | **パブリックドメイン (CC0)**。商用利用、改変、再配布すべて自由。FluentEdge内でホスティング・速度変更して再生可能 |
| **統合難易度** | Medium — 大量の音声ファイルのホスティング・管理が必要。Azure Blob Storageにアップロードして管理 |
| **FluentEdge価値** | ★★★☆☆ — 音声品質にばらつきがある（ボランティア朗読のため）。シャドーイング素材としては使えるが、ビジネス英語に特化したコンテンツは少ない。古典文学が中心。**LibriSpeechは発音評価のベンチマーク用途には有用** |

### 2.2 NPR API

| 項目 | 詳細 |
|------|------|
| **URL** | https://dev.npr.org/ （NPR One API） |
| **概要** | NPRのニュース・番組音声ストリーム。NPR OneアプリのバックエンドAPI |
| **無料枠** | NPR Developer APIは申請制。非営利・教育目的では無料の場合あり |
| **有料プラン** | 商用利用はNPRとのパートナーシップ契約が必要 |
| **レート制限** | 申請内容に依存 |
| **ライセンス** | NPRコンテンツの利用は厳格。アプリ内再生にはパートナーシップが必要。ただしNPRのポッドキャストRSSフィードは公開されており、そちら経由でのリンク再生は許容される |
| **統合難易度** | Hard — パートナーシップ申請プロセスが煩雑 |
| **FluentEdge価値** | ★★★☆☆ — 高品質な英語音声だが、ポッドキャストRSS経由の方が実用的。NPR API直接統合はコスト対効果が低い |

### 2.3 BBC Sounds / BBC Radio

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.bbc.co.uk/sounds |
| **概要** | BBCのラジオ番組・ポッドキャスト |
| **無料枠** | BBCポッドキャストのRSSフィードは無料公開。BBC Soundsアプリ自体はUK IPアドレス限定 |
| **有料プラン** | BBC APIは基本的に外部開発者に公開されていない（BBCのパートナーのみ） |
| **レート制限** | RSSフィード: なし |
| **ライセンス** | BBCコンテンツの再配布は禁止。RSSフィードへのリンク・ストリーミング再生は通常許容。アプリ内に音声を保存・キャッシュするのは権利的に問題 |
| **統合難易度** | Easy（RSS経由） / Hard（API直接） |
| **FluentEdge価値** | ★★★★☆ — 英国英語の高品質なリスニング素材。ニュース英語、ビジネス関連番組が豊富。RSS経由でエピソードリスト表示→外部プレイヤーで再生の形が現実的 |

### 2.4 Spotify Web API / Spotify for Podcasters

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.spotify.com/documentation/web-api |
| **概要** | Spotifyのポッドキャスト・音楽メタデータ検索、エピソード情報取得 |
| **無料枠** | 無料（OAuth認証必要）。ポッドキャストのメタデータ（タイトル、概要、エピソード一覧等）を取得可能 |
| **有料プラン** | 基本無料 |
| **レート制限** | Rolling 30秒ウィンドウで概ね数百リクエスト（公式ドキュメントでは明示せず、429で制限） |
| **ライセンス** | **重要**: Spotify Web APIでは音声ストリームの直接取得は不可。メタデータのみ。音声再生にはSpotify SDKの埋め込みプレイヤーが必要で、Spotifyのプレミアムアカウントが前提の機能もある。ポッドキャストの30秒プレビューは取得可能 |
| **統合難易度** | Medium — OAuth 2.0フロー、SDKの組み込みが必要 |
| **FluentEdge価値** | ★★★☆☆ — ポッドキャスト検索・推薦には使えるが、音声の速度変更やシャドーイング素材としての加工はできない。「おすすめポッドキャスト」表示と外部再生への誘導に限定 |

### 2.5 Apple Podcasts API (Apple Podcast Search API)

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/ |
| **概要** | iTunes/Apple Podcastsのカタログ検索API |
| **無料枠** | 完全無料。認証不要 |
| **有料プラン** | なし |
| **レート制限** | 約20リクエスト/分（非公式だが実測値） |
| **ライセンス** | メタデータの検索・表示のみ。Apple Podcasts Connectのアフィリエイトプログラムあり |
| **統合難易度** | Easy — 認証不要のシンプルなREST API |
| **FluentEdge価値** | ★★★☆☆ — ポッドキャスト検索・カタログ表示に便利。実際の音声アクセスはRSSフィード経由が必要 |

### 2.6 Audiobook APIs

| 項目 | 詳細 |
|------|------|
| **Audible** | 公式APIは一般開発者に非公開。Amazonアフィリエイト経由でメタデータのみ。音声ストリームへのアクセスは不可 |
| **Google Play Books** | 一般向けAPIなし。Google Books APIは書籍メタデータのみ（音声なし） |
| **Storytel API** | 法人パートナーシップのみ |
| **統合難易度** | Hard — いずれも音声へのプログラマティックアクセスが極めて困難 |
| **FluentEdge価値** | ★☆☆☆☆ — **非推奨**。オーディオブックAPIは実質的にクローズド。LibriVox（パブリックドメイン）を代替として使用すべき |

### 2.7 音声合成による教材生成（推奨アプローチ）

| 項目 | 詳細 |
|------|------|
| **アプローチ** | テキスト素材（Guardian API、ポッドキャスト書き起こし等）を取得し、Azure OpenAI TTS（gpt-4o-mini-tts）で音声化する |
| **メリット** | (1) 速度・声質の完全制御、(2) ライセンス問題の回避（テキストを変換するため）、(3) 品質の均一性、(4) 日本人が苦手な発音パターンを含む素材を意図的に作成可能 |
| **コスト** | gpt-4o-mini-tts: ~$0.015/1K chars。1分の音声 ≈ 150語 ≈ 750文字 → ~$0.011/分 |
| **FluentEdge価値** | ★★★★★ — **最も現実的で制御可能なアプローチ**。FluentEdgeの仕様書で既にTTSを使用予定のため、コンテンツパイプラインとして自然に統合可能 |

---

## 3. Language Learning Content APIs

### 3.1 Oxford Dictionaries API

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.oxfordlanguages.com/ |
| **概要** | Oxford English Dictionaryのデータ。定義、発音記号（IPA）、例文、語源、シソーラス、頻度データ |
| **無料枠** | Prototype Plan: 月1,000リクエスト（非商用、3ヶ月限定トライアル） |
| **有料プラン** | Research: $59/月（50,000リクエスト）、Startup: $239/月（500,000リクエスト）、Professional: カスタム。英語データのみならEssential枠もあり（より安価） |
| **レート制限** | プランに応じたリクエスト/月 + 60リクエスト/分（全プラン共通） |
| **ライセンス** | 辞書データの表示は許可。キャッシュには制限（24時間以内等）。大量コピーや再配布は禁止 |
| **統合難易度** | Easy — RESTful API、JSON。`/entries`, `/thesaurus`, `/sentences` エンドポイント |
| **FluentEdge価値** | ★★★★★ — **語彙学習の核心機能**。単語の正確な定義、IPA発音記号、用例、シソーラス（類義語での表現力拡張）がすべて取得可能。「Expression Upgrade」機能でシソーラスデータを活用できる。ビジネス英語の語彙レベル判定にも有用 |

### 3.2 Cambridge Dictionary API

| 項目 | 詳細 |
|------|------|
| **URL** | https://dictionary.cambridge.org/ja/licence/api.html |
| **概要** | Cambridge Dictionary のデータ。イギリス英語・アメリカ英語の両方の発音記号、CEFRレベル付き定義、例文 |
| **無料枠** | なし（ライセンス契約必要） |
| **有料プラン** | 法人ライセンス（年間契約、要問い合わせ。年間数千ポンド〜） |
| **レート制限** | 契約依存 |
| **ライセンス** | 厳格なライセンス。教育用アプリ向けの特別パートナーシップが存在する可能性あり |
| **統合難易度** | Medium — ライセンス取得のプロセスが不透明 |
| **FluentEdge価値** | ★★★★★ — **CEFRレベルが付いている点が最大の差別化ポイント**。FluentEdgeの「expressionSophistication: CEFR レベル (B2/C1/C2)」機能に直結。ただしOxford APIの方がアクセスしやすい |

### 3.3 Wordnik API

| 項目 | 詳細 |
|------|------|
| **URL** | https://developer.wordnik.com/ |
| **概要** | 複数辞書ソースからの定義、例文（実際の用例）、発音（音声ファイル含む）、関連語、頻度データ |
| **無料枠** | 月15,000リクエスト（APIキー無料取得） |
| **有料プラン** | なし（オープンソースプロジェクト。寄付ベース） |
| **レート制限** | 15,000リクエスト/月（無料）、100リクエスト/時 |
| **ライセンス** | 非営利プロジェクト。商用利用は事前に確認推奨（利用規約はリベラルだが明示されていない部分あり） |
| **統合難易度** | Easy — REST API、JSON |
| **FluentEdge価値** | ★★★☆☆ — Oxford APIがある場合は補助的。ただし実際の用例文（Webコーパスから抽出）が豊富な点は差別化。Oxford APIと併用でカバレッジ拡大 |

### 3.4 Tatoeba

| 項目 | 詳細 |
|------|------|
| **URL** | https://tatoeba.org/ , API: https://tatoeba.org/ja/downloads |
| **概要** | 多言語の例文ペアデータベース。ボランティアが作成。日英ペア文が豊富 |
| **無料枠** | 完全無料。全データダウンロード可能 |
| **有料プラン** | なし |
| **レート制限** | なし（データダンプをダウンロードして自前DBに格納推奨） |
| **ライセンス** | **CC BY 2.0 FR**。商用利用可、改変可。帰属表示が必要 |
| **統合難易度** | Medium — API（レート制限あり）よりデータダンプ一括取り込みが推奨。約1,000万文。日英ペアだけでも数十万文 |
| **FluentEdge価値** | ★★★★★ — **瞬間英作文の素材として最適**。日本語→英語の対訳ペアが大量に存在。FluentEdgeの「Flash Translation」機能に直結。CEFR難易度分類はないため、AI（Claude Haiku）で事前に難易度分類が必要 |

### 3.5 CEFR-Rated Content / EFLレベル判定

| 項目 | 詳細 |
|------|------|
| **English Profile (Cambridge)** | https://www.englishprofile.org/ — CEFRレベル別の語彙・文法リスト（English Vocabulary Profile, English Grammar Profile）。研究目的では無料アクセス可。API非公開。データをライセンス取得してインポートする形 |
| **CEFR Checker (AI-based)** | 独自実装推奨。テキストのCEFRレベル判定はClaude/GPTで実装可能。English Vocabulary ProfileのデータをPGに格納し、テキスト内の語彙レベルを集計してCEFRレベルを推定 |
| **EF SET (EF Standard English Test)** | https://www.efset.org/ — EF Education First のCEFR準拠テスト。API は公開されていないが、テスト問題の形式は参考になる |
| **FluentEdge価値** | ★★★★☆ — FluentEdgeの目標レベル設定・進捗管理に不可欠。English Vocabulary Profileのデータ取り込み + AIレベル判定の組み合わせが最も現実的 |

### 3.6 Business English Corpora

| 項目 | 詳細 |
|------|------|
| **COCA (Corpus of Contemporary American English)** | https://www.english-corpora.org/coca/ — 10億語以上の大規模英語コーパス。Academic, Newspaper, Magazine, Fiction, Spoken等のジャンル別検索。無料アカウントで100クエリ/日。API (有料): $95/年〜（Academic）。商用API: 要問い合わせ |
| **BNC (British National Corpus)** | https://www.english-corpora.org/bnc/ — 1億語のイギリス英語コーパス。COCAと同じプラットフォームでアクセス |
| **BAWE (British Academic Written English)** | 学術英語コーパス。無料で学術利用可 |
| **統合難易度** | Hard — API自体がシンプルでなく、データの前処理・整形が必要 |
| **FluentEdge価値** | ★★★☆☆ — 直接APIとして統合するよりも、**データを事前にエクスポートしてFluentEdgeの語彙・表現データベースの基盤として活用**する方が有用。ビジネス英語の頻出表現パターン抽出、コロケーション分析に活用 |

### 3.7 Forvo API（発音音声データベース）

| 項目 | 詳細 |
|------|------|
| **URL** | https://forvo.com/api/ |
| **概要** | ネイティブスピーカーによる世界最大の発音音声データベース。単語・フレーズの実際の発音音声を取得 |
| **無料枠** | なし |
| **有料プラン** | $2/月（500リクエスト/日）〜 $22/月（10,000リクエスト/日） |
| **レート制限** | プラン依存 |
| **ライセンス** | API経由のストリーミング再生は許可。音声ファイルのダウンロード・保存・再配布は禁止 |
| **統合難易度** | Easy — REST API |
| **FluentEdge価値** | ★★★★☆ — 発音トレーニング機能の補完として価値が高い。Azure Speech Services TTSは合成音声だが、Forvoは「本物のネイティブの発音」を提供。リアルな音声変化（リンキング・リダクション等）の学習に有効 |

---

## 4. Real-time Data Sources for Dynamic Content

### 4.1 Stock Market / Financial Data APIs

#### 4.1.1 Alpha Vantage

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.alphavantage.co/ |
| **概要** | 株価、為替、暗号資産のリアルタイム・過去データ |
| **無料枠** | 25リクエスト/日（2024年末に無料枠を大幅縮小） |
| **有料プラン** | $49.99/月（75リクエスト/分、無制限/日）〜 |
| **レート制限** | 無料: 25リクエスト/日。有料: 75リクエスト/分 |
| **ライセンス** | データの表示は許可。再配布・保存して別のAPIとして提供するのは禁止 |
| **統合難易度** | Easy — REST API、JSON/CSV |
| **FluentEdge価値** | ★★★☆☆ — ファイナンス系ディスカッション素材生成用。「今日のApple株価について議論しましょう」のようなリアルタイムコンテンツ生成が可能。ただし実装優先度は低い |

#### 4.1.2 Yahoo Finance API（非公式）/ yfinance

| 項目 | 詳細 |
|------|------|
| **URL** | https://github.com/ranaroussi/yfinance （Pythonライブラリ） |
| **概要** | Yahoo Financeからのデータスクレイピングライブラリ |
| **無料枠** | 無料（非公式） |
| **ライセンス** | **非公式API。ToS違反の可能性あり**。商用利用には不向き。Alpha Vantageまたは以下のFinancial Modeling Prepを推奨 |
| **FluentEdge価値** | ★★☆☆☆ — 開発・テスト用途のみ |

#### 4.1.3 Financial Modeling Prep (FMP)

| 項目 | 詳細 |
|------|------|
| **URL** | https://financialmodelingprep.com/ |
| **概要** | 株価、財務諸表、決算カレンダー、SEC提出書類、ニュースフィード |
| **無料枠** | 250リクエスト/日、5年分の過去データ |
| **有料プラン** | Starter: $14/月（300リクエスト/分）、Professional: $29/月、Enterprise: $99/月 |
| **レート制限** | プランに応じて300〜無制限リクエスト/分 |
| **ライセンス** | 商用利用可（有料プラン）。データ表示は許可。再配布禁止 |
| **統合難易度** | Easy — REST API |
| **FluentEdge価値** | ★★★★☆ — **決算書・財務データを使ったビジネスディスカッション素材に有用**。「AppleのQ4決算について議論しましょう」のような現実的なシナリオ構築が可能 |

### 4.2 Company Earnings Transcripts APIs

#### 4.2.1 Financial Modeling Prep - Earnings Transcripts

| 項目 | 詳細 |
|------|------|
| **URL** | https://financialmodelingprep.com/api/v3/earning_call_transcript/ |
| **概要** | 主要企業の決算説明会の文字起こし全文 |
| **無料枠** | 250リクエスト/日の中で利用可能 |
| **有料プラン** | Professional ($29/月) 以上で過去全データアクセス |
| **ライセンス** | 決算説明会の内容自体はSEC提出により公開情報。APIの利用規約に準拠 |
| **統合難易度** | Easy |
| **FluentEdge価値** | ★★★★★ — **最高価値のコンテンツソースの一つ**。CEOやCFOの実際のスピーチ・質疑応答が取得でき、以下に活用可能: (1) リスニング素材のテキストソース（TTSで音声化）、(2) ビジネス英語の実例（フォーマルな報告、数字の読み方、質疑応答パターン）、(3) ディスカッション練習のトピック。Big4やグローバル企業で働くユーザーにとって直接的に業務に関連する |

#### 4.2.2 SEC EDGAR API

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.sec.gov/edgar/sec-api-documentation |
| **概要** | SEC（米証券取引委員会）の全提出書類データ。10-K、10-Q、8-K等 |
| **無料枠** | 完全無料（政府公開データ） |
| **有料プラン** | なし |
| **レート制限** | 10リクエスト/秒（User-Agent設定必須） |
| **ライセンス** | **パブリックドメイン**。商用利用完全自由 |
| **統合難易度** | Medium — XMLファイルの解析が必要 |
| **FluentEdge価値** | ★★★☆☆ — 生データは複雑すぎるが、Annual Report のMD&A（Management Discussion & Analysis）セクションは優れたビジネス英語のソース |

### 4.3 Conference/Event Schedule APIs

| 項目 | 詳細 |
|------|------|
| **Eventbrite API** | https://www.eventbrite.com/platform/api — イベント検索・詳細取得。無料（OAuth認証）。ビジネスカンファレンス・セミナーの情報を取得して「このカンファレンスに参加する準備をしましょう」的な学習コンテンツ生成に利用可能。統合: Easy |
| **PredictHQ** | https://www.predicthq.com/ — イベント予測API。有料（$200/月〜）。産業カンファレンス・展示会データ。統合: Medium |
| **FluentEdge価値** | ★★☆☆☆ — 付加価値機能としてはあり得るが、優先度は低い。Phase 4以降で検討 |

### 4.4 Industry Reports APIs

| 項目 | 詳細 |
|------|------|
| **World Bank Open Data API** | https://data.worldbank.org/api — 経済指標、開発データ。完全無料、レート制限緩い。統合: Easy。価値: ★★★☆☆ — マクロ経済トピックのディスカッション素材 |
| **OECD Data API** | https://data.oecd.org/ — 先進国の経済・社会統計。無料。統合: Medium。価値: ★★★☆☆ |
| **IMF Data API** | https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service — 国際通貨基金のデータ。無料。統合: Medium |
| **Statista API** | https://www.statista.com/ — プレミアム統計データベース。法人契約（年間$5,000+）。統合: Medium |
| **FluentEdge価値** | ★★★☆☆ — 「データを使ったプレゼンテーション練習」機能に活用可能。「日本のGDP成長率についてプレゼンしてください」のようなシナリオ生成 |

---

## 5. User-Generated / Enterprise Content Integration

### 5.1 Document Import（PDF、PowerPoint）

| 技術 | 詳細 |
|------|------|
| **PyPDF2 / pdfplumber** | Pythonライブラリ。PDFからテキスト抽出。無料・MIT License。統合: Easy |
| **python-pptx** | PowerPointファイルの読み込み・テキスト抽出。無料・MIT License。統合: Easy |
| **Azure AI Document Intelligence (旧 Form Recognizer)** | https://azure.microsoft.com/en-us/products/ai-services/ai-document-intelligence — OCR + 構造化データ抽出。Free: 500ページ/月。S0: $1.50/1,000ページ。統合: Medium |
| **FluentEdge実装案** | ユーザーが自社の英語プレゼン資料・レポートをアップロード → テキスト抽出 → Claude Sonnetで語彙分析・難易度評価 → カスタム学習コンテンツ（専門用語リスト、瞬間英作文問題、ディスカッションテーマ）を自動生成 |
| **FluentEdge価値** | ★★★★★ — **エンタープライズ差別化の最大の武器**。B2B向けPremiumプランのキラー機能。「来週のプレゼン資料を事前にアップロードして練習する」ユースケースは、Big4/グローバル企業ユーザーにとって圧倒的な価値がある |

### 5.2 Slack Integration

| 項目 | 詳細 |
|------|------|
| **URL** | https://api.slack.com/ |
| **概要** | Slackワークスペースのメッセージ読み取り・分析 |
| **無料枠** | Slack APIは無料（Slackのサブスクリプション自体は別） |
| **実装方法** | Slack App としてインストール → `conversations.history` API でメッセージ取得 → Claude Haikuで英語品質分析 → フィードバック提供 |
| **ライセンス** | Slack APIの利用規約に準拠。ユーザーの明示的な同意が必須。データの保存・転送には厳格なプライバシー要件 |
| **統合難易度** | Medium — OAuth 2.0、Event Subscriptions、Socket Mode等の理解が必要 |
| **FluentEdge価値** | ★★★★☆ — 「実際の業務コミュニケーションを分析して改善」は魅力的だが、プライバシー・セキュリティの懸念が大きい。Phase 4以降で慎重に検討。ユーザー個人のメッセージのみを対象とし、他者のメッセージは解析しない設計が必須 |

### 5.3 Microsoft Teams Integration

| 項目 | 詳細 |
|------|------|
| **URL** | https://learn.microsoft.com/en-us/graph/teams-concept-overview |
| **概要** | Microsoft Graph API経由でTeamsのメッセージ・チャット・会議データにアクセス |
| **無料枠** | Microsoft Graph APIは無料（Microsoft 365ライセンスが前提） |
| **実装方法** | Microsoft Entra ID（FluentEdgeで既に使用）で認証 → Graph APIでTeamsメッセージ取得 → 分析 |
| **ライセンス** | Microsoft 365の管理者承認が必要。Teams APIの利用規約に準拠。企業のIT部門の承認プロセスが必要 |
| **統合難易度** | Medium — Microsoft Graph APIの権限スコープ管理、管理者同意フローの実装 |
| **FluentEdge価値** | ★★★★★ — **FluentEdgeが既にMicrosoft Entra IDを使用しているため、親和性が最高**。Big4等のターゲット企業は基本的にMicrosoft 365を使用。Teams会議の文字起こしデータ（Meeting Transcription API）を分析して、実際の会議での英語使用状況をフィードバックできる。**Phase 3以降のキラー機能候補** |

### 5.4 Email Analysis

| 項目 | 詳細 |
|------|------|
| **Microsoft Graph (Outlook)** | メールメッセージの読み取りAPIあり。ユーザー同意必須。統合: Medium |
| **Gmail API** | https://developers.google.com/gmail/api — メール本文取得可能。OAuth認証。統合: Medium |
| **実装案** | ユーザーが特定のメールを選択（または転送）→ テキスト抽出 → Claude Sonnetで分析 → 文法・表現改善のフィードバック + ビジネスメール作成パターン学習 |
| **プライバシー考慮** | メール内容は極めてセンシティブ。オプトイン方式、データの一時的な処理のみ（保存しない）、エンドツーエンド暗号化の検討が必須 |
| **FluentEdge価値** | ★★★★☆ — ビジネスメールの改善は高いニーズがあるが、プライバシーリスクが大きい。メール全体の分析よりも、「メール作成アシスタント」として特定のメールの添削・改善提案を行う形が安全 |

### 5.5 Calendar Integration

| 項目 | 詳細 |
|------|------|
| **Microsoft Graph (Calendar)** | 予定の取得、会議参加者情報、会議タイトル |
| **Google Calendar API** | https://developers.google.com/calendar |
| **実装案** | 英語の会議が近づくと通知 → 会議のアジェンダ・参加者情報から事前練習素材を自動生成（例: 「明日のBudget Review Meetingに向けて、予算関連の表現を練習しましょう」） |
| **統合難易度** | Easy — Microsoft Graph / Google Calendar APIともにシンプル |
| **FluentEdge価値** | ★★★★★ — **「ジャストインタイム学習」の実現**。明日の会議に直接役立つ練習を今日行えるのは、多忙なビジネスパーソンにとって最大の価値。テーマ設定が自動化されるため、「何を練習すべきか」の意思決定不要。**Phase 2-3で実装推奨** |

### 5.6 Custom Vocabulary Lists from Work Documents

| 項目 | 詳細 |
|------|------|
| **実装方法** | (1) ドキュメントアップロード → テキスト抽出 → (2) Claude Haikuで専門用語・業界用語を抽出 → (3) Oxford Dictionary APIで定義・発音取得 → (4) pgvectorで類似語のクラスタリング → (5) 忘却曲線システム（SM-2）に登録 |
| **技術スタック** | PyPDF2/pdfplumber + python-pptx + Claude Haiku + Oxford API + pgvector |
| **統合難易度** | Medium — パイプラインの構築が必要だが、個々の技術はシンプル |
| **FluentEdge価値** | ★★★★★ — ユーザーの実際の業務文書から語彙リストを自動生成するのは強力な差別化。企業導入時の提案材料としても有効 |

---

## 6. Content Management System (CMS) for Admin

### 6.1 Headless CMS 比較

#### 6.1.1 Strapi

| 項目 | 詳細 |
|------|------|
| **URL** | https://strapi.io/ |
| **概要** | オープンソースのHeadless CMS。Node.js製。セルフホスト可能 |
| **無料枠** | Community Edition: 完全無料（セルフホスト）。制限なし |
| **有料プラン** | Strapi Cloud: $29/月（Pro）、$99/月（Team）、Enterprise: カスタム。セルフホストならずっと無料 |
| **管理すべきコンテンツ** | フレーズバンク、シナリオテンプレート、文法ルール、文化ノート、CEFRレベル定義、パターンプラクティスのマスターデータ |
| **特徴** | (1) 完全カスタマイズ可能なContent Type、(2) REST + GraphQL API自動生成、(3) Media Library、(4) i18n（日本語管理画面対応）、(5) Webhook（コンテンツ更新時にFluentEdge DBを同期） |
| **統合難易度** | Medium — セルフホストの場合はDocker + Node.jsの運用が必要。Azure Container Appsに配置可能 |
| **FluentEdge価値** | ★★★★★ — **最も推奨**。セルフホスト無料、完全カスタマイズ可能、FluentEdgeのAzure環境にContainer Appとしてデプロイ可能。日本語管理画面でコンテンツチームが非エンジニアでも運用可能 |

#### 6.1.2 Sanity

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.sanity.io/ |
| **概要** | クラウドホステッドのHeadless CMS。リアルタイムコラボレーション。GROQ（独自クエリ言語） |
| **無料枠** | Free: 3ユーザー、10K APIリクエスト/月、500MB Assets、10GB Bandwidth |
| **有料プラン** | Growth: $15/ユーザー/月。Business: $99/ユーザー/月。Enterprise: カスタム |
| **特徴** | (1) Sanity Studio（カスタマイズ可能な管理画面）、(2) リアルタイムコラボ、(3) Portable Text（構造化リッチテキスト）、(4) CDN配信、(5) A/Bテストに対応しやすい構造 |
| **統合難易度** | Easy — クラウドホステッドのため運用不要。APIは使いやすい |
| **FluentEdge価値** | ★★★★☆ — Strapiより運用が楽。ただしコストが高く、ベンダーロックインの懸念。A/Bテスト機能は学習コンテンツの最適化に有用 |

#### 6.1.3 Contentful

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.contentful.com/ |
| **概要** | エンタープライズ向けHeadless CMS。最も成熟したプラットフォーム |
| **無料枠** | Community: 5ユーザー、25,000レコード、2ロケール |
| **有料プラン** | Team: $300/月。Enterprise: カスタム（年間$50,000+） |
| **特徴** | (1) Content Modeling GUI、(2) CDN配信（Fastly）、(3) 豊富なSDK、(4) Webhooks、(5) Content Preview API、(6) 多言語対応、(7) Rich Text Field |
| **統合難易度** | Easy — SDK・ドキュメントが充実 |
| **FluentEdge価値** | ★★★☆☆ — 機能は最も充実だがコストが高い。FluentEdgeの初期フェーズでは過剰。将来的にエンタープライズ顧客が増えた場合は検討 |

#### 6.1.4 比較まとめ

| | Strapi | Sanity | Contentful |
|---|--------|--------|------------|
| **初期コスト** | 無料（セルフホスト） | 無料枠あり | 無料枠あり |
| **ランニングコスト（100ユーザー規模）** | ~$20/月（Container App） | ~$45/月 | $300/月 |
| **カスタマイズ性** | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| **運用負荷** | ★★★☆☆（セルフホスト） | ★★★★★（マネージド） | ★★★★★（マネージド） |
| **A/Bテスト** | プラグイン必要 | 構造で対応 | ネイティブ対応 |
| **推奨** | **Phase 1〜** | Phase 2〜 | Phase 4以降 |

### 6.2 CMS管理対象コンテンツの設計

```yaml
# CMSで管理すべきコンテンツタイプ

phrase_bank:
  fields:
    - phrase_en: string (required)
    - phrase_ja: string
    - category: enum [meeting, negotiation, presentation, small_talk, email]
    - subcategory: string
    - register: enum [formal, neutral, casual]
    - cefr_level: enum [B1, B2, C1, C2]
    - usage_notes_ja: richtext
    - example_dialogue: text
    - audio_url: media (TTS生成後に登録)
    - tags: string[]
    - is_published: boolean

scenario_template:
  fields:
    - title_en: string (required)
    - title_ja: string
    - mode: enum [casual_chat, meeting, debate, presentation_qa, negotiation, small_talk]
    - difficulty: enum [beginner, intermediate, advanced]
    - cefr_target: enum [B2, C1, C2]
    - system_prompt: richtext (GPT Realtime API用)
    - context_description_ja: richtext
    - key_phrases: relation → phrase_bank (many)
    - expected_patterns: string[]
    - evaluation_criteria: json
    - is_published: boolean

grammar_rule:
  fields:
    - rule_name_en: string
    - rule_name_ja: string
    - explanation_ja: richtext
    - examples: json [{en: string, ja: string, note: string}]
    - common_mistakes_ja: richtext
    - cefr_level: enum [B1, B2, C1, C2]
    - related_patterns: relation → phrase_bank (many)
    - quiz_questions: json

cultural_note:
  fields:
    - title_en: string
    - title_ja: string
    - category: enum [business_etiquette, communication_style, regional_difference, idiom_origin]
    - content_ja: richtext
    - content_en: richtext
    - applicable_scenarios: relation → scenario_template (many)
    - difficulty: enum [basic, intermediate, advanced]

sound_pattern:
  fields:
    - pattern_type: enum [linking, reduction, flapping, elision, weak_form]
    - pattern_name_en: string
    - pattern_name_ja: string
    - ipa_notation: string
    - examples: json [{written: string, spoken: string, audio_url: string}]
    - explanation_ja: richtext
    - difficulty: integer (1-5)
    - practice_sentences: json [{text: string, audio_url: string}]
```

### 6.3 コンテンツバージョニング & A/Bテスト

| 機能 | 実装方針 |
|------|---------|
| **バージョニング** | Strapi内蔵のDraft/Published機能 + Git風のバージョン管理（Strapiのcontent-versioning plugin） |
| **A/Bテスト** | PostgreSQLのcontent_variantsテーブル + Redis でユーザー割り当てをキャッシュ。CMSのWebhookで新バリアント登録時にFluentEdge DBに同期。分析はApplication Insights Custom Eventsで |
| **コンテンツ配信** | CMS → Webhook → FastAPI → PostgreSQL → Redis Cache → Frontend。CDNキャッシュ（Azure Front Door）で静的コンテンツを高速配信 |

---

## 7. Multimedia Content

### 7.1 Unsplash API

| 項目 | 詳細 |
|------|------|
| **URL** | https://unsplash.com/developers |
| **概要** | 400万枚以上の高品質フリー写真 |
| **無料枠** | Demo: 50リクエスト/時。Production: 5,000リクエスト/時（申請制、無料） |
| **有料プラン** | なし（完全無料） |
| **レート制限** | Demo: 50リクエスト/時、Production: 5,000リクエスト/時 |
| **ライセンス** | **Unsplashライセンス（非常にリベラル）**。商用利用可、改変可、帰属表示推奨（必須ではない）。API利用時はUnsplashへの帰属表示が必須（"Photo by [Photographer] on Unsplash"） |
| **統合難易度** | Easy — REST API、JSON。SDKあり |
| **FluentEdge価値** | ★★★★☆ — シナリオのビジュアル素材として有用。会議室、オフィス、プレゼンテーション等の写真で学習シーンの臨場感を演出。ロールプレイのコンテキスト画像として使用 |

### 7.2 Pexels API

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.pexels.com/api/ |
| **概要** | 高品質のフリー写真・動画 |
| **無料枠** | 200リクエスト/時（APIキー無料） |
| **有料プラン** | なし（完全無料） |
| **レート制限** | 200リクエスト/時 |
| **ライセンス** | Pexelsライセンス。商用利用可。帰属表示推奨。API利用時はPexelsへのクレジット表示必須 |
| **統合難易度** | Easy |
| **FluentEdge価値** | ★★★★☆ — Unsplashの代替/補完。ビデオコンテンツも利用可能な点が差別化 |

### 7.3 Video Generation APIs

#### 7.3.1 Synthesia

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.synthesia.io/api |
| **概要** | AIアバターによる動画生成。テキストから「人が話している動画」を自動生成 |
| **無料枠** | 無料トライアル（3分のビデオ、透かし入り） |
| **有料プラン** | Starter: $22/月（10分/月）、Creator: $67/月（30分/月）、Enterprise: カスタム。API利用はEnterprise以上 |
| **レート制限** | APIは非同期。動画生成に数分〜十数分 |
| **ライセンス** | 生成動画の商用利用可（有料プラン） |
| **統合難易度** | Medium — 非同期API、Webhook通知 |
| **FluentEdge価値** | ★★★★☆ — **会議シナリオの動画化に高い価値**。AIアバターが会議のシーンを演じ、ユーザーがファシリテーターとして参加する形。ただしコストが高く、Phase 4以降の差別化機能として検討 |

#### 7.3.2 HeyGen

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.heygen.com/ |
| **概要** | Synthesiaの競合。AIアバター動画生成 |
| **無料枠** | 3本の動画（透かし入り） |
| **有料プラン** | Creator: $24/月。Business: $72/月。Enterprise: カスタム（API付き） |
| **ライセンス** | 商用利用可（有料プラン） |
| **統合難易度** | Medium |
| **FluentEdge価値** | ★★★☆☆ — Synthesiaの代替。インタラクティブ会話機能（Interactive Avatar）がFluentEdgeの会話練習と親和性あり |

#### 7.3.3 D-ID

| 項目 | 詳細 |
|------|------|
| **URL** | https://www.d-id.com/ |
| **概要** | 写真1枚からリアルタイムにアバターが話す動画を生成。Streaming APIあり |
| **無料枠** | 5分の無料トライアル |
| **有料プラン** | Lite: $4.70/月（10分/月）、Pro: $16/月（15分/月）、Enterprise: カスタム |
| **レート制限** | Streaming APIはリアルタイム |
| **ライセンス** | 商用利用可 |
| **統合難易度** | Medium — Streaming APIでリアルタイム会話可能 |
| **FluentEdge価値** | ★★★★☆ — **リアルタイムの「顔が見える」AI会話パートナー**。GPT Realtime APIの音声と組み合わせて、会議シミュレーションに使える。ただしレイテンシとコストのバランスが課題 |

### 7.4 Giphy API

| 項目 | 詳細 |
|------|------|
| **URL** | https://developers.giphy.com/ |
| **概要** | GIF・ステッカーの検索・表示 |
| **無料枠** | Beta API Key: 無制限（ただし42検索/時 + 1000検索/日）。Production: 申請制（無料）、レート制限緩和 |
| **有料プラン** | なし（無料） |
| **レート制限** | Beta: 42リクエスト/時。Production: 1,000リクエスト/時 |
| **ライセンス** | Giphy利用規約に準拠。商用利用可。Giphy帰属表示が必須（"Powered by GIPHY"ロゴ） |
| **統合難易度** | Easy |
| **FluentEdge価値** | ★★☆☆☆ — 文化的コンテキスト（英語圏のリアクションGIF文化の理解）には多少役立つが、ビジネス英語学習アプリとしてはトーンが合わない可能性。カジュアルなSmall Talk練習時のみ |

### 7.5 Icons & Illustrations

| 項目 | 詳細 |
|------|------|
| **Lucide Icons** | https://lucide.dev/ — MIT License。shadcn/uiで標準使用。統合済み |
| **unDraw** | https://undraw.co/ — MIT License。ビジネス系のSVGイラスト。商用利用可 |
| **FluentEdge価値** | ★★★☆☆ — UIデザインの品質向上。学習コンテンツのビジュアル強化 |

---

## 8. FluentEdge統合優先度マトリクス

### フェーズ別推奨統合

#### Phase 1 (MVP) — 必須

| ソース | 用途 | コスト |
|--------|------|--------|
| **Tatoeba** | 瞬間英作文の素材DB | 無料 (CC BY 2.0) |
| **Oxford Dictionaries API** | 語彙学習、定義、シソーラス | $59-239/月 |
| **Strapi (セルフホスト)** | フレーズバンク・シナリオ管理CMS | ~$20/月 (Container App) |
| **Unsplash API** | シナリオのビジュアル素材 | 無料 |
| **Podcast RSS** | リスニング素材のリンク提供 | 無料 |
| **Azure TTS (gpt-4o-mini-tts)** | テキストからの音声教材生成 | ~$0.015/1K chars |

#### Phase 2 — 高優先

| ソース | 用途 | コスト |
|--------|------|--------|
| **The Guardian API** | ディスカッション素材（全文取得可） | 無料（Commercial申請） |
| **YouTube Data API** | シャドーイング動画リスト | 無料 |
| **NewsAPI.org** | 最新ニュストピック取得 | $449/月 (Business) |
| **Calendar Integration (MS Graph)** | 会議準備の自動化 | 無料 |
| **Document Import (PDF/PPTX)** | カスタム語彙リスト生成 | ~$20/月 (Document Intelligence) |
| **FMP Earnings Transcripts** | ビジネス英語のリアル素材 | $29/月 |
| **Forvo API** | ネイティブ発音データ | $2-22/月 |

#### Phase 3 — 中優先

| ソース | 用途 | コスト |
|--------|------|--------|
| **Teams Integration** | 実際の業務会話分析 | 無料 (MS Graph) |
| **Slack Integration** | ワークプレイス英語分析 | 無料 |
| **Alpha Vantage / FMP** | ファイナンス系トピック素材 | $29-50/月 |
| **World Bank / OECD Data** | マクロ経済トピック素材 | 無料 |
| **English Vocabulary Profile** | CEFR語彙レベルデータ | 要ライセンス |

#### Phase 4 — 低優先 / 差別化機能

| ソース | 用途 | コスト |
|--------|------|--------|
| **D-ID / Synthesia** | AIアバター会議動画 | $16-67/月 |
| **Email Analysis** | ビジネスメール改善 | 無料 (MS Graph) |
| **Pexels API** | 追加のビジュアル素材 | 無料 |
| **COCA/BNC Corpora** | コーパスベースの表現分析 | $95+/年 |

### コスト概算

| フェーズ | 外部API月額コスト |
|---------|-----------------|
| Phase 1 | ~$100-280/月 |
| Phase 2 | ~$600-800/月 |
| Phase 3 | ~$700-900/月 |
| Phase 4 | ~$800-1,100/月 |

---

## 9. ライセンス・法的考慮事項まとめ

### 9.1 安全に使えるソース（商用利用OK）

| ソース | ライセンス | 条件 |
|--------|----------|------|
| Tatoeba | CC BY 2.0 | 帰属表示必須 |
| LibriVox | Public Domain | 制限なし |
| Unsplash | Unsplash License | API利用時は帰属表示必須 |
| Pexels | Pexels License | 帰属推奨 |
| SEC EDGAR | Public Domain | 制限なし |
| World Bank Data | CC BY 4.0 | 帰属表示必須 |
| Strapi | MIT License | 制限なし |

### 9.2 条件付きで使えるソース（要契約・要申請）

| ソース | 必要アクション |
|--------|--------------|
| Oxford Dictionaries API | 有料プラン契約 |
| NewsAPI.org | Business Plan ($449/月) 契約 |
| The Guardian API | Commercial tier申請 |
| YouTube Data API | 利用規約遵守、クォータ増加申請 |
| Forvo API | 有料プラン契約 |
| FMP | 有料プラン契約 |

### 9.3 注意が必要なソース（グレーゾーン）

| ソース | リスク | 対策 |
|--------|--------|------|
| ポッドキャスト音声 | 再配布権が不明確 | リンク再生のみ、キャッシュ不可 |
| TED Talks | CC BY-NC-ND | 非商用のみ、パートナーシップ検討 |
| YouTube字幕 | ToSのグレーゾーン | 埋め込み再生のみ、字幕ダウンロード回避 |
| Slack/Teams データ | プライバシー法 | ユーザー同意、データ最小化、暗号化 |

### 9.4 推奨しないソース（高コスト or 制限的）

| ソース | 理由 |
|--------|------|
| Reuters/Bloomberg API | 年間数万ドルのエンタープライズ契約 |
| Financial Times API | 法人専用、高額 |
| Cambridge Dictionary API | ライセンスプロセスが不透明 |
| Audible/Audiobook API | 一般開発者にAPIが非公開 |
| NPR API | パートナーシップ申請の難易度が高い |

---

## 10. 技術実装アーキテクチャ（外部コンテンツ統合）

### 10.1 コンテンツ取得・処理パイプライン

```
[外部API/RSS] → [Content Ingestion Service] → [AI Processing] → [Content Store]
                                                                       ↓
                                                               [Delivery API] → [Frontend]
```

### 10.2 推奨実装構成

```python
# backend/app/services/content_ingestion/

content_ingestion/
├── __init__.py
├── base.py                    # 基底クラス（共通インターフェース）
├── news_service.py            # NewsAPI, Guardian API
├── podcast_service.py         # RSS解析、エピソードリスト管理
├── dictionary_service.py      # Oxford API
├── financial_service.py       # FMP, Alpha Vantage
├── document_service.py        # PDF/PPTX テキスト抽出
├── calendar_service.py        # MS Graph Calendar
├── youtube_service.py         # YouTube Data API
├── tatoeba_service.py         # Tatoeba データインポート
├── content_processor.py       # AI (Claude) によるCEFRレベル判定、分類
└── cache_manager.py           # Redis + Blob Storageキャッシュ管理
```

### 10.3 データフロー例: ニュースベースのディスカッション素材生成

```
1. NewsAPI → 最新ビジネスニュースの見出し + 概要を取得
2. Guardian API → 関連記事の全文を取得
3. Claude Haiku → 記事を要約 + CEFR B2レベルにリライト
4. Claude Haiku → ディスカッション質問3-5問を生成
5. Claude Haiku → キーボキャブラリーリスト (+ Oxford APIで定義取得)
6. gpt-4o-mini-tts → 要約テキストを音声化 (シャドーイング素材)
7. PostgreSQL → コンテンツを保存 (daily_content テーブル)
8. Redis → 当日のコンテンツをキャッシュ
9. Frontend → ダッシュボード「Today's Topic」に表示
```

---

*本調査レポートは2026年2月14日時点の情報に基づく。各APIの仕様・料金は頻繁に変更されるため、実装前に最新の公式ドキュメントで確認すること。特にAI関連APIは急速に進化しているため、四半期ごとの見直しを推奨する。*
