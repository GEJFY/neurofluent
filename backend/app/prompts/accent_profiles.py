"""アクセントプロファイル - 多国籍英語対応

グローバルビジネスで遭遇する主要な英語アクセントの
音声設定・特徴・練習ポイントを定義。
Azure TTS Neural Voice マッピング含む。
"""

# --- Azure TTS Neural Voice マッピング ---

ACCENT_VOICES: dict[str, dict] = {
    "us": {
        "label": "American English",
        "label_ja": "アメリカ英語",
        "voices": {
            "female": "en-US-JennyMultilingualNeural",
            "male": "en-US-GuyNeural",
            "female_alt": "en-US-AriaNeural",
            "male_alt": "en-US-DavisNeural",
        },
        "default_voice": "en-US-JennyMultilingualNeural",
        "language_code": "en-US",
    },
    "uk": {
        "label": "British English",
        "label_ja": "イギリス英語",
        "voices": {
            "female": "en-GB-SoniaNeural",
            "male": "en-GB-RyanNeural",
            "female_alt": "en-GB-LibbyNeural",
            "male_alt": "en-GB-ThomasNeural",
        },
        "default_voice": "en-GB-SoniaNeural",
        "language_code": "en-GB",
    },
    "india": {
        "label": "Indian English",
        "label_ja": "インド英語",
        "voices": {
            "female": "en-IN-NeerjaNeural",
            "male": "en-IN-PrabhatNeural",
        },
        "default_voice": "en-IN-NeerjaNeural",
        "language_code": "en-IN",
    },
    "singapore": {
        "label": "Singaporean English",
        "label_ja": "シンガポール英語",
        "voices": {
            "female": "en-SG-LunaNeural",
            "male": "en-SG-WayneNeural",
        },
        "default_voice": "en-SG-LunaNeural",
        "language_code": "en-SG",
    },
    "australia": {
        "label": "Australian English",
        "label_ja": "オーストラリア英語",
        "voices": {
            "female": "en-AU-NatashaNeural",
            "male": "en-AU-WilliamNeural",
        },
        "default_voice": "en-AU-NatashaNeural",
        "language_code": "en-AU",
    },
    "ireland": {
        "label": "Irish English",
        "label_ja": "アイルランド英語",
        "voices": {
            "female": "en-IE-EmilyNeural",
            "male": "en-IE-ConnorNeural",
        },
        "default_voice": "en-IE-ConnorNeural",
        "language_code": "en-IE",
    },
    "hongkong": {
        "label": "Hong Kong English",
        "label_ja": "香港英語",
        "voices": {
            "female": "en-HK-YanNeural",
            "male": "en-HK-SamNeural",
        },
        "default_voice": "en-HK-YanNeural",
        "language_code": "en-HK",
    },
    "southafrica": {
        "label": "South African English",
        "label_ja": "南アフリカ英語",
        "voices": {
            "female": "en-ZA-LeahNeural",
            "male": "en-ZA-LukeNeural",
        },
        "default_voice": "en-ZA-LeahNeural",
        "language_code": "en-ZA",
    },
}


# --- アクセント別の音声変化特徴DB ---

ACCENT_FEATURES: dict[str, dict] = {
    "india": {
        "phonetic_features": [
            "Retroflex /t/ and /d/ (舌を後ろに巻いて発音、日本語のタ行に近い)",
            "/v/ と /w/ の融合 (very → wery のように聞こえることがある)",
            "/θ/ → /t/ 置換 (think → tink)",
            "/ð/ → /d/ 置換 (the → de)",
            "母音のリズムが syllable-timed (各音節がほぼ等間隔)",
            "語末の子音が明瞭 (called の /d/ をはっきり発音)",
        ],
        "common_expressions": [
            "Do one thing... (提案の前置き。「こうしましょう」の意味)",
            "Kindly do the needful (必要な対応をお願いします)",
            "Prepone (bring forward の意味。postpone の逆)",
            "What is your good name? (お名前は？ 丁寧な表現)",
            "I have a doubt (I have a question の意味)",
            "Let us discuss about... (about は冗長だが一般的)",
        ],
        "business_context": "インドのIT企業・BPO・グローバル拠点でのミーティング。"
        "時差のあるビデオ会議、テクニカルディスカッションに頻出。",
        "listening_tips": [
            "retroflex の /t/ /d/ に慣れる → water が「ウォーター」ではなく「ウォータル」に近い",
            "syllable-timed リズムを意識 → 英語の強弱リズムと異なる",
            "/v/-/w/ の区別が曖昧な場合は文脈から判断",
        ],
    },
    "uk": {
        "phonetic_features": [
            "Non-rhotic: 語末・子音前の /r/ を発音しない (car → /kɑː/, worker → /wɜːkə/)",
            "Broad A: bath, can't, dance の母音が /ɑː/ (アメリカ英語の /æ/ と異なる)",
            "T-glottalization: water → wa'er (声門閉鎖音に変化、特にロンドン方言)",
            "Intrusive /r/: idea of → idea-r-of (母音間にrが挿入)",
            "/juː/ の保持: tube → /tjuːb/ (アメリカ英語では /tuːb/)",
            "イントネーションの下降が明確",
        ],
        "common_expressions": [
            "Shall we crack on? (始めましょうか)",
            "Quite good (かなり良い、ではなく「まあまあ」の含みがあることも)",
            "Brilliant! (素晴らしい！ 口語で多用)",
            "I reckon... (I think... のイギリス口語)",
            "Cheers (ありがとう/じゃあね の両方で使用)",
            "Taking the mickey (からかっている)",
        ],
        "business_context": "ロンドン金融街、マンチェスター・エディンバラのテック企業。"
        "フォーマルなミーティングと、パブでのインフォーマルな商談の両方。",
        "listening_tips": [
            "r が聞こえなくても焦らない → car park は「カーパーク」ではなく「カーパーク」（rなし）",
            "quite は「とても」ではなく「まあまあ」の意味になることがある",
            "understatement 文化 → 'not bad' = 実はかなり良い",
        ],
    },
    "singapore": {
        "phonetic_features": [
            "語末子音の脱落 (good → goo, fact → fac)",
            "Singlish particle: lah, lor, mah, leh (文末助詞)",
            "/θ/ → /t/ 置換 (three → tree)",
            "/ð/ → /d/ 置換",
            "ストレス・タイミングが syllable-timed",
            "イントネーションが独特 (文末の上昇が特徴的)",
        ],
        "common_expressions": [
            "Can or not? (できますか？/大丈夫？)",
            "Confirm plus chop (間違いなく確実)",
            "Steady lah (落ち着いて/素晴らしい)",
            "Die die must try (絶対に試すべき)",
            "Bo jio! (誘ってくれなかった！)",
            "Last time I was there... (前回そこに行った時... 過去形の使い方が独特)",
        ],
        "business_context": "シンガポールの多国籍企業・金融ハブでのミーティング。"
        "中華系・マレー系・インド系の多文化環境。英語が公用語だが独自の変化がある。",
        "listening_tips": [
            "語末の子音が消えても文脈で補う → 'goo morning' = good morning",
            "lah, lor 等の助詞は意味を持つ感嘆詞 → 無視して構わない",
            "ビジネスシーンではフォーマルな英語に切り替わることも多い",
        ],
    },
    "australia": {
        "phonetic_features": [
            "/eɪ/ → /aɪ/ 方向へのシフト (day → 'die' に近く聞こえる)",
            "/aɪ/ → /ɒɪ/ (time → 'toime')",
            "語尾の上昇イントネーション (AQI: Australian Question Intonation)",
            "Non-rhotic (イギリス英語と同様、rを弱く発音)",
            "短縮形が多い (afternoon → arvo, breakfast → brekkie)",
            "ナーサル共鳴が強い (鼻にかかった響き)",
        ],
        "common_expressions": [
            "No worries (問題ない/どういたしまして)",
            "Arvo (afternoon の短縮)",
            "Reckon (think の意味で非常に多用)",
            "Fair dinkum (本当に/本物の)",
            "Good on ya! (よくやった！)",
            "She'll be right (大丈夫、問題ない)",
        ],
        "business_context": "シドニー・メルボルンのビジネスシーン。"
        "カジュアルなコミュニケーション文化だが、プロフェッショナルさも重視。",
        "listening_tips": [
            "'today' が 'to-die' に聞こえる → /eɪ/ の変化に慣れる",
            "文末の上昇調は質問ではなく確認のニュアンス",
            "短縮形（arvo, brekkie等）はインフォーマルなシーンで頻出",
        ],
    },
}


# --- 環境音シミュレーション設定 ---

AUDIO_ENVIRONMENTS: dict[str, dict] = {
    "clean": {
        "label": "クリーン（スタジオ品質）",
        "description": "雑音なし。学習初期向け。",
        "ssml_effect": None,
        "noise_level": 0,
    },
    "phone_call": {
        "label": "電話回線",
        "description": "帯域制限された電話品質。海外拠点との電話でよくある音質。",
        "ssml_effect": "telephone",
        "noise_level": 1,
    },
    "video_call": {
        "label": "ビデオ通話 (Zoom/Teams)",
        "description": "軽い圧縮と遅延。リモートワークのミーティング品質。",
        "ssml_effect": None,  # SSML prosodyで模擬
        "noise_level": 1,
        "ssml_adjustments": {
            "pitch": "-2%",
        },
    },
    "office": {
        "label": "オフィス",
        "description": "キーボード音・空調音・同僚の会話が遠くに聞こえる。",
        "ssml_effect": None,
        "noise_level": 2,
    },
    "cafe": {
        "label": "カフェ",
        "description": "BGM・食器音・他の会話。ビジネスランチやインフォーマルミーティング。",
        "ssml_effect": None,
        "noise_level": 3,
    },
    "conference_room": {
        "label": "会議室",
        "description": "軽い反響音。大きめの会議室でのプレゼンやミーティング。",
        "ssml_effect": None,
        "noise_level": 1,
    },
}


# --- マルチスピーカーシナリオ設定 ---

MULTI_SPEAKER_CONFIGS: dict[str, dict] = {
    "team_standup": {
        "label": "チームスタンドアップ",
        "speakers": [
            {"role": "Scrum Master", "accent": "us", "gender": "female"},
            {"role": "Developer", "accent": "india", "gender": "male"},
            {"role": "QA Engineer", "accent": "singapore", "gender": "female"},
        ],
        "context": "Daily standup meeting at a multinational tech company",
    },
    "client_call": {
        "label": "クライアント電話会議",
        "speakers": [
            {"role": "Account Manager", "accent": "uk", "gender": "male"},
            {"role": "Client CTO", "accent": "india", "gender": "male"},
        ],
        "context": "Project status call between London office and Bangalore team",
    },
    "global_meeting": {
        "label": "グローバルミーティング",
        "speakers": [
            {"role": "VP of Sales", "accent": "us", "gender": "male"},
            {"role": "APAC Director", "accent": "singapore", "gender": "female"},
            {"role": "EMEA Manager", "accent": "uk", "gender": "female"},
            {"role": "Product Lead", "accent": "australia", "gender": "male"},
        ],
        "context": "Quarterly global alignment meeting across time zones",
    },
    "vendor_negotiation": {
        "label": "ベンダー交渉",
        "speakers": [
            {"role": "Procurement Manager", "accent": "us", "gender": "female"},
            {"role": "Vendor Representative", "accent": "india", "gender": "male"},
        ],
        "context": "SaaS contract renewal negotiation",
    },
}


def get_voice_for_accent(
    accent: str = "us",
    gender: str = "female",
) -> str:
    """アクセントと性別からAzure TTS音声名を取得"""
    accent_config = ACCENT_VOICES.get(accent, ACCENT_VOICES["us"])
    voices = accent_config["voices"]
    return voices.get(gender, accent_config["default_voice"])


def get_language_code(accent: str = "us") -> str:
    """アクセントからAzure Speech言語コードを取得"""
    accent_config = ACCENT_VOICES.get(accent, ACCENT_VOICES["us"])
    return accent_config["language_code"]


def get_accent_tips(accent: str) -> list[str]:
    """アクセントのリスニングTipsを取得"""
    features = ACCENT_FEATURES.get(accent, {})
    return features.get("listening_tips", [])


def build_accent_awareness_prompt(accent: str) -> str:
    """アクセント認識用のプロンプト補足を生成"""
    features = ACCENT_FEATURES.get(accent)
    if not features:
        return ""

    phonetic = "\n".join(f"  - {f}" for f in features["phonetic_features"])
    expressions = "\n".join(f"  - {e}" for e in features["common_expressions"])

    return f"""
## Accent: {ACCENT_VOICES[accent]["label"]}
The speaker has a {ACCENT_VOICES[accent]["label"]} accent.

### Phonetic Characteristics
{phonetic}

### Common Expressions
{expressions}

### Context
{features["business_context"]}

Generate text that naturally reflects these accent-specific patterns and expressions.
Use vocabulary and phrasing typical of this English variety."""
