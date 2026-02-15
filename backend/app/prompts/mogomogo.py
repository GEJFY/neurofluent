"""もごもごイングリッシュプロンプト - リンキング・リダクション音声変化訓練

リスニング力を伸ばすための音声変化パターン（リンキング、リダクション、
フラッピング、削除、弱形）の練習問題生成・評価用プロンプト。
"""


# --- 音声変化パターンデータベース ---

SOUND_PATTERN_DATABASE: dict = {
    "linking": {
        "name_en": "Linking",
        "name_ja": "リンキング（連結）",
        "description": "Words connect when one ends with a consonant and the next begins with a vowel.",
        "description_ja": "単語末の子音と次の単語の母音がつながって発音される現象",
        "examples": [
            {
                "text": "pick it up",
                "modified": "pi-ki-tup",
                "ipa_original": "/pɪk ɪt ʌp/",
                "ipa_modified": "/pɪ.kɪ.tʌp/",
            },
            {
                "text": "check it out",
                "modified": "che-ki-tout",
                "ipa_original": "/tʃɛk ɪt aʊt/",
                "ipa_modified": "/tʃɛ.kɪ.taʊt/",
            },
            {
                "text": "turn it off",
                "modified": "tur-ni-toff",
                "ipa_original": "/tɜːrn ɪt ɒf/",
                "ipa_modified": "/tɜːr.nɪ.tɒf/",
            },
            {
                "text": "put it on",
                "modified": "pu-ti-ton",
                "ipa_original": "/pʊt ɪt ɒn/",
                "ipa_modified": "/pʊ.tɪ.tɒn/",
            },
            {
                "text": "look at it",
                "modified": "loo-ka-tit",
                "ipa_original": "/lʊk æt ɪt/",
                "ipa_modified": "/lʊ.kæ.tɪt/",
            },
            {
                "text": "not at all",
                "modified": "no-ta-tall",
                "ipa_original": "/nɒt æt ɔːl/",
                "ipa_modified": "/nɒ.tæ.tɔːl/",
            },
            {
                "text": "come on in",
                "modified": "co-mo-nin",
                "ipa_original": "/kʌm ɒn ɪn/",
                "ipa_modified": "/kʌ.mɒ.nɪn/",
            },
            {
                "text": "an apple",
                "modified": "a-napple",
                "ipa_original": "/æn ˈæpəl/",
                "ipa_modified": "/ə.næpəl/",
            },
            {
                "text": "is it",
                "modified": "i-zit",
                "ipa_original": "/ɪz ɪt/",
                "ipa_modified": "/ɪ.zɪt/",
            },
            {
                "text": "run out of",
                "modified": "ru-nou-tof",
                "ipa_original": "/rʌn aʊt ɒv/",
                "ipa_modified": "/rʌ.naʊ.tɒv/",
            },
            {
                "text": "take it easy",
                "modified": "tay-ki-teasy",
                "ipa_original": "/teɪk ɪt ˈiːzi/",
                "ipa_modified": "/teɪ.kɪ.tiːzi/",
            },
            {
                "text": "hang on a minute",
                "modified": "han-go-na-minute",
                "ipa_original": "/hæŋ ɒn ə ˈmɪnɪt/",
                "ipa_modified": "/hæŋ.gɒ.nə.mɪnɪt/",
            },
            {
                "text": "fill it in",
                "modified": "fi-li-tin",
                "ipa_original": "/fɪl ɪt ɪn/",
                "ipa_modified": "/fɪ.lɪ.tɪn/",
            },
            {
                "text": "call us up",
                "modified": "ca-lu-sup",
                "ipa_original": "/kɔːl ʌs ʌp/",
                "ipa_modified": "/kɔː.lʌ.sʌp/",
            },
            {
                "text": "get on with it",
                "modified": "ge-ton-wi-thit",
                "ipa_original": "/ɡɛt ɒn wɪð ɪt/",
                "ipa_modified": "/ɡɛ.tɒn.wɪ.ðɪt/",
            },
            {
                "text": "figure it out",
                "modified": "fi-gyu-ri-tout",
                "ipa_original": "/ˈfɪɡər ɪt aʊt/",
                "ipa_modified": "/fɪ.ɡə.rɪ.taʊt/",
            },
            {
                "text": "keep it up",
                "modified": "kee-pi-tup",
                "ipa_original": "/kiːp ɪt ʌp/",
                "ipa_modified": "/kiː.pɪ.tʌp/",
            },
            {
                "text": "mix it up",
                "modified": "mi-xi-tup",
                "ipa_original": "/mɪks ɪt ʌp/",
                "ipa_modified": "/mɪk.sɪ.tʌp/",
            },
            {
                "text": "wrap it up",
                "modified": "wra-pi-tup",
                "ipa_original": "/ræp ɪt ʌp/",
                "ipa_modified": "/ræ.pɪ.tʌp/",
            },
            {
                "text": "think about it",
                "modified": "thin-ka-bou-tit",
                "ipa_original": "/θɪŋk əˈbaʊt ɪt/",
                "ipa_modified": "/θɪŋ.kə.baʊ.tɪt/",
            },
        ],
    },
    "reduction": {
        "name_en": "Reduction",
        "name_ja": "リダクション（短縮）",
        "description": "Common phrases are shortened in casual speech.",
        "description_ja": "日常会話でよく使われるフレーズが短縮されて発音される現象",
        "examples": [
            {
                "text": "going to",
                "modified": "gonna",
                "ipa_original": "/ˈɡoʊɪŋ tuː/",
                "ipa_modified": "/ˈɡʌnə/",
            },
            {
                "text": "want to",
                "modified": "wanna",
                "ipa_original": "/wɒnt tuː/",
                "ipa_modified": "/ˈwɒnə/",
            },
            {
                "text": "have to",
                "modified": "hafta",
                "ipa_original": "/hæv tuː/",
                "ipa_modified": "/ˈhæftə/",
            },
            {
                "text": "got to",
                "modified": "gotta",
                "ipa_original": "/ɡɒt tuː/",
                "ipa_modified": "/ˈɡɒtə/",
            },
            {
                "text": "has to",
                "modified": "hasta",
                "ipa_original": "/hæz tuː/",
                "ipa_modified": "/ˈhæstə/",
            },
            {
                "text": "ought to",
                "modified": "oughta",
                "ipa_original": "/ɔːt tuː/",
                "ipa_modified": "/ˈɔːtə/",
            },
            {
                "text": "used to",
                "modified": "useta",
                "ipa_original": "/juːst tuː/",
                "ipa_modified": "/ˈjuːstə/",
            },
            {
                "text": "supposed to",
                "modified": "supposta",
                "ipa_original": "/səˈpoʊzd tuː/",
                "ipa_modified": "/səˈpoʊstə/",
            },
            {
                "text": "kind of",
                "modified": "kinda",
                "ipa_original": "/kaɪnd ɒv/",
                "ipa_modified": "/ˈkaɪndə/",
            },
            {
                "text": "sort of",
                "modified": "sorta",
                "ipa_original": "/sɔːrt ɒv/",
                "ipa_modified": "/ˈsɔːrtə/",
            },
            {
                "text": "lot of",
                "modified": "lotta",
                "ipa_original": "/lɒt ɒv/",
                "ipa_modified": "/ˈlɒtə/",
            },
            {
                "text": "out of",
                "modified": "outta",
                "ipa_original": "/aʊt ɒv/",
                "ipa_modified": "/ˈaʊtə/",
            },
            {
                "text": "don't know",
                "modified": "dunno",
                "ipa_original": "/doʊnt noʊ/",
                "ipa_modified": "/dʌˈnoʊ/",
            },
            {
                "text": "give me",
                "modified": "gimme",
                "ipa_original": "/ɡɪv miː/",
                "ipa_modified": "/ˈɡɪmi/",
            },
            {
                "text": "let me",
                "modified": "lemme",
                "ipa_original": "/lɛt miː/",
                "ipa_modified": "/ˈlɛmi/",
            },
            {
                "text": "tell him",
                "modified": "tellim",
                "ipa_original": "/tɛl hɪm/",
                "ipa_modified": "/ˈtɛlɪm/",
            },
            {
                "text": "would have",
                "modified": "woulda",
                "ipa_original": "/wʊd hæv/",
                "ipa_modified": "/ˈwʊdə/",
            },
            {
                "text": "could have",
                "modified": "coulda",
                "ipa_original": "/kʊd hæv/",
                "ipa_modified": "/ˈkʊdə/",
            },
            {
                "text": "should have",
                "modified": "shoulda",
                "ipa_original": "/ʃʊd hæv/",
                "ipa_modified": "/ˈʃʊdə/",
            },
            {
                "text": "must have",
                "modified": "musta",
                "ipa_original": "/mʌst hæv/",
                "ipa_modified": "/ˈmʌstə/",
            },
            {
                "text": "what are you",
                "modified": "whatcha",
                "ipa_original": "/wɒt ɑːr juː/",
                "ipa_modified": "/ˈwɒtʃə/",
            },
            {
                "text": "did you",
                "modified": "didja",
                "ipa_original": "/dɪd juː/",
                "ipa_modified": "/ˈdɪdʒə/",
            },
        ],
    },
    "flapping": {
        "name_en": "Flapping (T/D Flap)",
        "name_ja": "フラッピング（弾音化）",
        "description": "T and D sounds between vowels become a quick flap, sounding like a soft D.",
        "description_ja": "母音に挟まれたT/D音が弾音化し、日本語のラ行に近い音になる現象",
        "examples": [
            {
                "text": "water",
                "modified": "wader",
                "ipa_original": "/ˈwɔːtər/",
                "ipa_modified": "/ˈwɔːɾər/",
            },
            {
                "text": "better",
                "modified": "bedder",
                "ipa_original": "/ˈbɛtər/",
                "ipa_modified": "/ˈbɛɾər/",
            },
            {
                "text": "getting",
                "modified": "gedding",
                "ipa_original": "/ˈɡɛtɪŋ/",
                "ipa_modified": "/ˈɡɛɾɪŋ/",
            },
            {
                "text": "butter",
                "modified": "budder",
                "ipa_original": "/ˈbʌtər/",
                "ipa_modified": "/ˈbʌɾər/",
            },
            {
                "text": "city",
                "modified": "ciddy",
                "ipa_original": "/ˈsɪti/",
                "ipa_modified": "/ˈsɪɾi/",
            },
            {
                "text": "pretty",
                "modified": "priddy",
                "ipa_original": "/ˈprɪti/",
                "ipa_modified": "/ˈprɪɾi/",
            },
            {
                "text": "meeting",
                "modified": "meeding",
                "ipa_original": "/ˈmiːtɪŋ/",
                "ipa_modified": "/ˈmiːɾɪŋ/",
            },
            {
                "text": "writing",
                "modified": "wriding",
                "ipa_original": "/ˈraɪtɪŋ/",
                "ipa_modified": "/ˈraɪɾɪŋ/",
            },
            {
                "text": "letter",
                "modified": "ledder",
                "ipa_original": "/ˈlɛtər/",
                "ipa_modified": "/ˈlɛɾər/",
            },
            {
                "text": "matter",
                "modified": "madder",
                "ipa_original": "/ˈmætər/",
                "ipa_modified": "/ˈmæɾər/",
            },
            {
                "text": "waiting",
                "modified": "waiding",
                "ipa_original": "/ˈweɪtɪŋ/",
                "ipa_modified": "/ˈweɪɾɪŋ/",
            },
            {
                "text": "data",
                "modified": "dada",
                "ipa_original": "/ˈdeɪtə/",
                "ipa_modified": "/ˈdeɪɾə/",
            },
            {
                "text": "later",
                "modified": "lader",
                "ipa_original": "/ˈleɪtər/",
                "ipa_modified": "/ˈleɪɾər/",
            },
            {
                "text": "item",
                "modified": "idem",
                "ipa_original": "/ˈaɪtəm/",
                "ipa_modified": "/ˈaɪɾəm/",
            },
            {
                "text": "little",
                "modified": "liddle",
                "ipa_original": "/ˈlɪtəl/",
                "ipa_modified": "/ˈlɪɾəl/",
            },
            {
                "text": "bottle",
                "modified": "boddle",
                "ipa_original": "/ˈbɒtəl/",
                "ipa_modified": "/ˈbɒɾəl/",
            },
            {
                "text": "total",
                "modified": "todal",
                "ipa_original": "/ˈtoʊtəl/",
                "ipa_modified": "/ˈtoʊɾəl/",
            },
            {
                "text": "computer",
                "modified": "compuder",
                "ipa_original": "/kəmˈpjuːtər/",
                "ipa_modified": "/kəmˈpjuːɾər/",
            },
            {
                "text": "automatic",
                "modified": "audomadic",
                "ipa_original": "/ˌɔːtəˈmætɪk/",
                "ipa_modified": "/ˌɔːɾəˈmæɾɪk/",
            },
            {
                "text": "a lot of",
                "modified": "a lodof",
                "ipa_original": "/ə lɒt ɒv/",
                "ipa_modified": "/ə lɒɾəv/",
            },
        ],
    },
    "deletion": {
        "name_en": "Deletion (Elision)",
        "name_ja": "削除（省略）",
        "description": "Sounds at the end of words are dropped, especially T and D in consonant clusters.",
        "description_ja": "単語末の子音（特にT, D）が子音連続の中で省略される現象",
        "examples": [
            {
                "text": "last night",
                "modified": "las' night",
                "ipa_original": "/læst naɪt/",
                "ipa_modified": "/læs naɪt/",
            },
            {
                "text": "next day",
                "modified": "nex' day",
                "ipa_original": "/nɛkst deɪ/",
                "ipa_modified": "/nɛks deɪ/",
            },
            {
                "text": "just fine",
                "modified": "jus' fine",
                "ipa_original": "/dʒʌst faɪn/",
                "ipa_modified": "/dʒʌs faɪn/",
            },
            {
                "text": "must be",
                "modified": "mus' be",
                "ipa_original": "/mʌst biː/",
                "ipa_modified": "/mʌs biː/",
            },
            {
                "text": "first thing",
                "modified": "firs' thing",
                "ipa_original": "/fɜːrst θɪŋ/",
                "ipa_modified": "/fɜːrs θɪŋ/",
            },
            {
                "text": "best practice",
                "modified": "bes' practice",
                "ipa_original": "/bɛst ˈpræktɪs/",
                "ipa_modified": "/bɛs ˈpræktɪs/",
            },
            {
                "text": "most people",
                "modified": "mos' people",
                "ipa_original": "/moʊst ˈpiːpəl/",
                "ipa_modified": "/moʊs ˈpiːpəl/",
            },
            {
                "text": "fact check",
                "modified": "fac' check",
                "ipa_original": "/fækt tʃɛk/",
                "ipa_modified": "/fæk tʃɛk/",
            },
            {
                "text": "old man",
                "modified": "ol' man",
                "ipa_original": "/oʊld mæn/",
                "ipa_modified": "/oʊl mæn/",
            },
            {
                "text": "hand bag",
                "modified": "han' bag",
                "ipa_original": "/hænd bæɡ/",
                "ipa_modified": "/hæn bæɡ/",
            },
            {
                "text": "round table",
                "modified": "roun' table",
                "ipa_original": "/raʊnd ˈteɪbəl/",
                "ipa_modified": "/raʊn ˈteɪbəl/",
            },
            {
                "text": "stand by",
                "modified": "stan' by",
                "ipa_original": "/stænd baɪ/",
                "ipa_modified": "/stæn baɪ/",
            },
            {
                "text": "send back",
                "modified": "sen' back",
                "ipa_original": "/sɛnd bæk/",
                "ipa_modified": "/sɛn bæk/",
            },
            {
                "text": "world class",
                "modified": "worl' class",
                "ipa_original": "/wɜːrld klæs/",
                "ipa_modified": "/wɜːrl klæs/",
            },
            {
                "text": "cold call",
                "modified": "col' call",
                "ipa_original": "/koʊld kɔːl/",
                "ipa_modified": "/koʊl kɔːl/",
            },
            {
                "text": "post mortem",
                "modified": "pos' mortem",
                "ipa_original": "/poʊst ˈmɔːrtəm/",
                "ipa_modified": "/poʊs ˈmɔːrtəm/",
            },
            {
                "text": "soft skill",
                "modified": "sof' skill",
                "ipa_original": "/sɒft skɪl/",
                "ipa_modified": "/sɒf skɪl/",
            },
            {
                "text": "left side",
                "modified": "lef' side",
                "ipa_original": "/lɛft saɪd/",
                "ipa_modified": "/lɛf saɪd/",
            },
            {
                "text": "kept going",
                "modified": "kep' going",
                "ipa_original": "/kɛpt ˈɡoʊɪŋ/",
                "ipa_modified": "/kɛp ˈɡoʊɪŋ/",
            },
            {
                "text": "exact copy",
                "modified": "exac' copy",
                "ipa_original": "/ɪɡˈzækt ˈkɒpi/",
                "ipa_modified": "/ɪɡˈzæk ˈkɒpi/",
            },
        ],
    },
    "weak_form": {
        "name_en": "Weak Forms",
        "name_ja": "弱形（弱化）",
        "description": "Function words (articles, prepositions, auxiliaries) are reduced to unstressed forms in natural speech.",
        "description_ja": "機能語（冠詞、前置詞、助動詞）がストレスを受けず弱く発音される現象",
        "examples": [
            {
                "text": "can",
                "modified": "/kən/",
                "ipa_original": "/kæn/",
                "ipa_modified": "/kən/",
            },
            {
                "text": "have",
                "modified": "/əv/",
                "ipa_original": "/hæv/",
                "ipa_modified": "/əv/",
            },
            {
                "text": "was",
                "modified": "/wəz/",
                "ipa_original": "/wɒz/",
                "ipa_modified": "/wəz/",
            },
            {
                "text": "are",
                "modified": "/ər/",
                "ipa_original": "/ɑːr/",
                "ipa_modified": "/ər/",
            },
            {
                "text": "were",
                "modified": "/wər/",
                "ipa_original": "/wɜːr/",
                "ipa_modified": "/wər/",
            },
            {
                "text": "do",
                "modified": "/də/",
                "ipa_original": "/duː/",
                "ipa_modified": "/də/",
            },
            {
                "text": "does",
                "modified": "/dəz/",
                "ipa_original": "/dʌz/",
                "ipa_modified": "/dəz/",
            },
            {
                "text": "has",
                "modified": "/əz/",
                "ipa_original": "/hæz/",
                "ipa_modified": "/əz/",
            },
            {
                "text": "had",
                "modified": "/əd/",
                "ipa_original": "/hæd/",
                "ipa_modified": "/əd/",
            },
            {
                "text": "will",
                "modified": "/əl/",
                "ipa_original": "/wɪl/",
                "ipa_modified": "/əl/",
            },
            {
                "text": "would",
                "modified": "/wəd/",
                "ipa_original": "/wʊd/",
                "ipa_modified": "/wəd/",
            },
            {
                "text": "shall",
                "modified": "/ʃəl/",
                "ipa_original": "/ʃæl/",
                "ipa_modified": "/ʃəl/",
            },
            {
                "text": "should",
                "modified": "/ʃəd/",
                "ipa_original": "/ʃʊd/",
                "ipa_modified": "/ʃəd/",
            },
            {
                "text": "must",
                "modified": "/məst/",
                "ipa_original": "/mʌst/",
                "ipa_modified": "/məst/",
            },
            {
                "text": "to",
                "modified": "/tə/",
                "ipa_original": "/tuː/",
                "ipa_modified": "/tə/",
            },
            {
                "text": "for",
                "modified": "/fər/",
                "ipa_original": "/fɔːr/",
                "ipa_modified": "/fər/",
            },
            {
                "text": "from",
                "modified": "/frəm/",
                "ipa_original": "/frɒm/",
                "ipa_modified": "/frəm/",
            },
            {
                "text": "of",
                "modified": "/əv/",
                "ipa_original": "/ɒv/",
                "ipa_modified": "/əv/",
            },
            {
                "text": "at",
                "modified": "/ət/",
                "ipa_original": "/æt/",
                "ipa_modified": "/ət/",
            },
            {
                "text": "and",
                "modified": "/ən/",
                "ipa_original": "/ænd/",
                "ipa_modified": "/ən/",
            },
            {
                "text": "but",
                "modified": "/bət/",
                "ipa_original": "/bʌt/",
                "ipa_modified": "/bət/",
            },
            {
                "text": "that",
                "modified": "/ðət/",
                "ipa_original": "/ðæt/",
                "ipa_modified": "/ðət/",
            },
        ],
    },
}


def build_mogomogo_generation_prompt(
    pattern_types: list[str],
    level: str = "B2",
) -> str:
    """
    もごもごエクササイズ生成用のシステムプロンプトを構築

    Args:
        pattern_types: 対象パターン種別リスト
        level: ユーザーのCEFRレベル

    Returns:
        システムプロンプト文字列
    """
    # パターンごとの例を集約
    pattern_sections = []
    for pt in pattern_types:
        if pt in SOUND_PATTERN_DATABASE:
            db_entry = SOUND_PATTERN_DATABASE[pt]
            examples_text = "\n".join(
                f'  - "{ex["text"]}" -> "{ex["modified"]}" ({ex["ipa_original"]} -> {ex["ipa_modified"]})'
                for ex in db_entry["examples"][:5]
            )
            pattern_sections.append(
                f"### {db_entry['name_en']} ({db_entry['name_ja']})\n"
                f"{db_entry['description']}\n"
                f"Examples:\n{examples_text}"
            )

    patterns_block = "\n\n".join(pattern_sections)

    level_guidance = {
        "A2": "Use simple, everyday phrases and short sentences. Focus on the most common reductions.",
        "B1": "Use common business phrases and medium-length sentences. Include multiple patterns per sentence.",
        "B2": "Use natural business conversations. Include subtle sound changes and connected speech.",
        "C1": "Use fast-paced natural speech patterns. Include complex connected speech with multiple simultaneous changes.",
        "C2": "Use advanced native-like speech patterns with multiple overlapping sound changes.",
    }

    guidance = level_guidance.get(level, level_guidance["B2"])

    return f"""You are a Connected Speech exercise generator for FluentEdge AI's "Mogomogo English" module.
Your task is to create listening exercises that help Japanese learners recognize natural English sound changes.

## Target Level: CEFR {level}
{guidance}

## Sound Change Patterns to Focus On

{patterns_block}

## Exercise Design Rules

1. Each exercise must clearly demonstrate ONE primary sound change pattern
2. Include the full sentence context (not just the changed phrase)
3. Provide accurate IPA for both the formal and natural pronunciations
4. The practice_sentence should be a natural business English sentence containing the pattern
5. Explanations should be clear and helpful for Japanese speakers
6. audio_text is the sentence to be read aloud with the sound change applied

## Output Format
Return ONLY a JSON array:
[
    {{
        "exercise_id": "unique-id",
        "pattern_type": "linking|reduction|flapping|deletion|weak_form",
        "audio_text": "The sentence with the sound change",
        "ipa_original": "/formal IPA/",
        "ipa_modified": "/natural IPA/",
        "explanation": "Clear explanation of the sound change for Japanese learners",
        "practice_sentence": "A practice sentence containing this pattern",
        "difficulty": "{level}"
    }}
]

## Rules
- Generate exactly the requested number of exercises
- Use business English context where possible
- Explanations should reference how this differs from Japanese phonology
- Return ONLY valid JSON, no markdown formatting"""


def build_dictation_check_prompt() -> str:
    """
    ディクテーションチェック用のシステムプロンプトを構築

    Returns:
        システムプロンプト文字列
    """
    return """You are a dictation evaluator for FluentEdge AI's "Mogomogo English" module.
Your task is to compare a user's dictation attempt against the original text, specifically focusing on
how well they caught the natural sound changes in connected speech.

## Evaluation Criteria

### Accuracy Scoring (0.0 to 1.0)
- **1.0**: Perfect transcription
- **0.8-0.9**: Minor differences (capitalization, punctuation) that don't affect meaning
- **0.6-0.7**: Most words correct but missed some connected speech elements
- **0.4-0.5**: Got the general idea but missed significant portions
- **0.2-0.3**: Partial understanding, many missed words
- **0.0-0.1**: Completely incorrect or unrelated

### What to Check
1. Did the user correctly hear words affected by sound changes?
2. Did they write the standard English form (not the phonetic reduction)?
3. Were function words (articles, prepositions) correctly identified?
4. Was the overall sentence structure understood?

## Output Format
Return ONLY a JSON object:
{
    "accuracy": 0.0-1.0,
    "missed_words": ["list", "of", "missed", "words"],
    "identified_patterns": ["description of sound patterns the user missed or caught"],
    "score": 0.0-1.0,
    "feedback": "Constructive feedback explaining what was missed and why, referencing specific sound change patterns"
}

## Rules
- Be encouraging but accurate
- Focus feedback on the specific sound change patterns that were missed
- The score may differ from accuracy if the user showed understanding of the pattern even with minor errors
- missed_words should list ONLY the words that were wrong or omitted
- Return ONLY valid JSON"""
