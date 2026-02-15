"""発音トレーニングプロンプト - 日本語話者向け音素・韻律訓練

日本語のL1干渉パターンに基づいた発音エクササイズ生成、
韻律（ストレス・リズム・イントネーション）訓練用のプロンプト。
"""


# --- 日本語話者のL1干渉パターン ---

JAPANESE_L1_INTERFERENCE: dict = {
    "/r/-/l/": {
        "phoneme_pair": "/r/-/l/",
        "description_en": "Japanese has a single liquid consonant /ɾ/ that falls between English /r/ and /l/.",
        "description_ja": "日本語のラ行音/ɾ/は英語の/r/と/l/の中間的な音。英語では舌の位置が全く異なる。",
        "common_mistake": "Substituting Japanese /ɾ/ for both /r/ and /l/, making 'right' and 'light' sound identical.",
        "tip": "/r/: 舌を丸めて口の天井に触れない。/l/: 舌先を上の歯茎にしっかりつける。",
        "minimal_pairs": [
            ("right", "light"),
            ("read", "lead"),
            ("road", "load"),
            ("rain", "lane"),
            ("rock", "lock"),
            ("rice", "lice"),
            ("red", "led"),
            ("ramp", "lamp"),
            ("row", "low"),
            ("arrive", "alive"),
            ("correct", "collect"),
            ("pray", "play"),
        ],
        "practice_sentences": [
            "The lawyer will lead the legal review of the railway report.",
            "Larry really likes the large library near the railroad.",
            "Please reply to the letter regarding the real estate listing.",
            "The rally leader released a long list of requirements.",
        ],
        "tongue_twisters": [
            "Red lorry, yellow lorry, red lorry, yellow lorry.",
            "Larry sent the letter to the literary leader.",
            "Really leery, rarely lily, rolling lightly.",
        ],
    },
    "/θ/-/s/": {
        "phoneme_pair": "/θ/-/s/",
        "description_en": "Japanese lacks the dental fricative /θ/, often substituted with /s/.",
        "description_ja": "/θ/（th音）は日本語に存在しない。舌を上下の歯の間に挟んで息を出す。",
        "common_mistake": "Saying 'sink' instead of 'think', 'sick' instead of 'thick'.",
        "tip": "舌先を上の歯の裏（または歯の間）に軽く当て、隙間から息を出す。/s/との違いは舌の位置。",
        "minimal_pairs": [
            ("think", "sink"),
            ("thick", "sick"),
            ("three", "see"),
            ("thought", "sought"),
            ("theme", "seem"),
            ("thin", "sin"),
            ("path", "pass"),
            ("math", "mass"),
            ("faith", "face"),
            ("both", "boss"),
            ("worth", "worse"),
            ("mouth", "mouse"),
        ],
        "practice_sentences": [
            "I think the third Thursday of this month works for the meeting.",
            "Thank the author for their thorough thesis on the theory.",
            "Something about the method seems thoughtful and thorough.",
            "Both brothers thought through the math problem together.",
        ],
        "tongue_twisters": [
            "The thirty-three thieves thought that they thrilled the throne throughout Thursday.",
            "Three thin thinkers thinking thick thoughtful thoughts.",
        ],
    },
    "/v/-/b/": {
        "phoneme_pair": "/v/-/b/",
        "description_en": "Japanese lacks the labiodental fricative /v/, often substituted with /b/.",
        "description_ja": "/v/は日本語に存在しない。上の歯を下唇に軽く当てて振動させる。/b/は両唇を閉じて破裂させる。",
        "common_mistake": "Saying 'berry' instead of 'very', 'best' instead of 'vest'.",
        "tip": "/v/: 上の前歯を下唇に軽く当て、声を出しながら空気を出す。唇を完全に閉じない。",
        "minimal_pairs": [
            ("very", "berry"),
            ("vest", "best"),
            ("vine", "bine"),
            ("vet", "bet"),
            ("van", "ban"),
            ("vow", "bow"),
            ("vale", "bale"),
            ("veil", "bail"),
            ("vote", "boat"),
            ("vase", "base"),
            ("curve", "curb"),
            ("marvel", "marble"),
        ],
        "practice_sentences": [
            "The vendor provided a very valuable service to every visitor.",
            "Vivian gave a vibrant overview of the innovative venture.",
            "The investment review revealed several viable alternatives.",
            "I believe the revised version covers every vital variable.",
        ],
        "tongue_twisters": [
            "Very verbose vendors vowed to vastly improve every venture.",
            "Vivid visions of vast valleys vanished in the vivacious village.",
        ],
    },
    "/f/-/h/": {
        "phoneme_pair": "/f/-/h/",
        "description_en": "Japanese speakers may confuse /f/ and /h/, as Japanese /ɸ/ is bilabial, not labiodental.",
        "description_ja": "日本語のフ（/ɸ/）は両唇音で、英語の/f/（唇歯音）とは異なる。",
        "common_mistake": "Using Japanese bilabial /ɸ/ instead of English labiodental /f/.",
        "tip": "/f/: 上の前歯を下唇に軽く当てて息を出す。/h/: 口を開けたまま喉の奥から息を出す。",
        "minimal_pairs": [
            ("fan", "han"),
            ("fat", "hat"),
            ("fit", "hit"),
            ("fail", "hail"),
            ("fear", "hear"),
            ("feel", "heel"),
            ("fold", "hold"),
            ("food", "hood"),
            ("four", "hoar"),
            ("fun", "hun"),
        ],
        "practice_sentences": [
            "The financial firm finalized a five-year forecast for the future.",
            "Find the perfect fit between form and function for the final product.",
            "The first floor office featured a fine view of the forest.",
            "Five professional staff members offered helpful feedback.",
        ],
        "tongue_twisters": [
            "Fresh French fried fish, fish fresh French fried.",
            "Four furious friends fought for the phone.",
        ],
    },
    "/æ/-/ʌ/": {
        "phoneme_pair": "/æ/-/ʌ/",
        "description_en": "Japanese lacks both vowels; speakers often use Japanese /a/ for both.",
        "description_ja": "/æ/（catのア）と/ʌ/（cutのア）は日本語の「ア」とは異なる2つの母音。",
        "common_mistake": "Making 'cat' and 'cut', 'bat' and 'but' sound the same.",
        "tip": "/æ/: 口を横に大きく開いて「エ」と「ア」の中間。/ʌ/: 口を少し開いて短く「ア」。",
        "minimal_pairs": [
            ("cat", "cut"),
            ("bat", "but"),
            ("cap", "cup"),
            ("bag", "bug"),
            ("fan", "fun"),
            ("ran", "run"),
            ("hat", "hut"),
            ("mat", "mutt"),
            ("lack", "luck"),
            ("match", "much"),
            ("bad", "bud"),
            ("mash", "mush"),
        ],
        "practice_sentences": [
            "The manager ran the annual budget analysis with much accuracy.",
            "Can you hand me that cup from the cabinet above the counter?",
            "The staff had lunch at the campus cafeteria last Sunday.",
            "Jack cut the fabric and packed it in the trunk of the van.",
        ],
        "tongue_twisters": [
            "The fat cat sat on the flat mat and had a chat about luck.",
            "Back from the bus, the man grabbed a bag and had some fun.",
        ],
    },
    "/ɪ/-/iː/": {
        "phoneme_pair": "/ɪ/-/iː/",
        "description_en": "Japanese has a single /i/ vowel; English distinguishes short /ɪ/ from long /iː/.",
        "description_ja": "日本語の「イ」は1種類だが、英語には短い/ɪ/と長い/iː/がある。長さだけでなく口の形も違う。",
        "common_mistake": "Making 'ship' and 'sheep', 'sit' and 'seat' sound identical.",
        "tip": "/ɪ/: 口を少し開いてリラックスした短い「イ」。/iː/: 口を横に引いて緊張させた長い「イー」。",
        "minimal_pairs": [
            ("ship", "sheep"),
            ("sit", "seat"),
            ("hit", "heat"),
            ("bit", "beat"),
            ("fill", "feel"),
            ("live", "leave"),
            ("slip", "sleep"),
            ("chip", "cheap"),
            ("fit", "feet"),
            ("dip", "deep"),
        ],
        "practice_sentences": [
            "Please leave the list of items near the printer by the east wing.",
            "The team will meet to discuss the key issues with the new system.",
            "She will read the report and give feedback within this week.",
            "Keep the receipt in case you need to exchange the item.",
        ],
        "tongue_twisters": [
            "She sells six thin silk sheets in the chic little shop.",
            "The big ship with cheap chips slipped into the deep sea.",
        ],
    },
    "/w/-/ʊ/": {
        "phoneme_pair": "/w/ initial",
        "description_en": "Japanese speakers may add a vowel before /w/ or pronounce it weakly.",
        "description_ja": "英語の/w/は唇を丸めて強く発音する。日本語の「ウ」のように弱く発音しない。",
        "common_mistake": "Weak /w/ production or adding a vowel sound before words starting with /w/.",
        "tip": "唇を小さく丸めてから素早く開く。「ウ」よりも唇の丸めを強くする。",
        "minimal_pairs": [
            ("west", "vest"),
            ("wine", "vine"),
            ("wet", "vet"),
            ("wail", "vale"),
            ("wane", "vane"),
            ("worse", "verse"),
        ],
        "practice_sentences": [
            "We went to work on Wednesday to wrap up the weekly review.",
            "The woman wondered whether the weather would worsen.",
            "Would you want to wait while I write the witness report?",
        ],
        "tongue_twisters": [
            "Whether the weather is warm, whether the weather is hot, we have to put up with the weather, whether we like it or not.",
        ],
    },
    "/ð/-/z/": {
        "phoneme_pair": "/ð/-/z/",
        "description_en": "Voiced dental fricative /ð/ is often substituted with /z/ or /d/ by Japanese speakers.",
        "description_ja": "有声の/ð/（theのth）は日本語に存在しない。/z/や/d/で代用しがち。",
        "common_mistake": "Saying 'zis' or 'dis' instead of 'this', 'zat' instead of 'that'.",
        "tip": "舌先を上の歯の裏（または歯の間）に当て、声を出しながら息を出す。/θ/の有声版。",
        "minimal_pairs": [
            ("then", "zen"),
            ("this", "dis"),
            ("that", "dat"),
            ("these", "deez"),
            ("those", "doze"),
            ("breathe", "breeze"),
            ("bathe", "bays"),
            ("with", "wiz"),
        ],
        "practice_sentences": [
            "The other brother gathered the leather together with the feather.",
            "This is the method they use for the analysis rather than the other.",
            "Whether or not they bother, the weather will change nonetheless.",
        ],
        "tongue_twisters": [
            "The father lathered the leather with the other soothing lotion.",
        ],
    },
}


def build_pronunciation_exercise_prompt(
    target_phonemes: list[str],
    level: str = "B2",
) -> str:
    """
    発音エクササイズ生成用のシステムプロンプトを構築

    Args:
        target_phonemes: 対象音素ペアリスト (例: ["/r/-/l/", "/θ/-/s/"])
        level: ユーザーのCEFRレベル

    Returns:
        システムプロンプト文字列
    """
    # 対象音素のデータを集約
    phoneme_sections = []
    for phoneme in target_phonemes:
        if phoneme in JAPANESE_L1_INTERFERENCE:
            data = JAPANESE_L1_INTERFERENCE[phoneme]
            pairs_text = ", ".join(f"{a}/{b}" for a, b in data["minimal_pairs"][:6])
            phoneme_sections.append(
                f"### {phoneme}\n"
                f"Problem: {data['description_en']}\n"
                f"Common mistake: {data['common_mistake']}\n"
                f"Minimal pairs: {pairs_text}\n"
                f"Tip: {data['tip']}"
            )

    phonemes_block = "\n\n".join(phoneme_sections)

    level_guidance = {
        "A2": "Use common, everyday words. Keep sentences short and simple.",
        "B1": "Use intermediate vocabulary in simple business contexts.",
        "B2": "Use business English vocabulary in professional contexts.",
        "C1": "Use advanced vocabulary with complex sentence structures.",
        "C2": "Use sophisticated, native-like vocabulary and natural phrasing.",
    }
    guidance = level_guidance.get(level, level_guidance["B2"])

    return f"""You are a Pronunciation Exercise Generator for FluentEdge AI, specializing in helping Japanese speakers improve their English pronunciation.

## Target Level: CEFR {level}
{guidance}

## Target Phonemes for This Session

{phonemes_block}

## Exercise Types to Generate

### 1. Minimal Pairs
- Two words that differ by only one phoneme
- Include both words, IPA transcription, and a sentence using each
- Help the learner hear and produce the difference

### 2. Tongue Twisters
- Short phrases that repeatedly use the target phoneme
- Should be fun and challenging but achievable
- Business-relevant when possible

### 3. Sentence Practice
- Natural sentences containing multiple instances of the target phoneme
- Business English context
- Include IPA for the key words

## Output Format
Return ONLY a JSON array:
[
    {{
        "exercise_id": "unique-id",
        "target_phoneme": "/r/-/l/",
        "exercise_type": "minimal_pair|tongue_twister|sentence",
        "word_a": "first word or main word",
        "word_b": "second word (for minimal pairs, null otherwise)",
        "sentence": "Practice sentence containing the target sounds",
        "ipa": "IPA transcription of key words or sentence",
        "difficulty": "{level}",
        "tip": "Pronunciation tip specific to this exercise for Japanese speakers"
    }}
]

## Rules
- Generate exactly the requested number of exercises
- Mix all three exercise types
- Each exercise should have a clear tip relevant to Japanese speakers
- Business English context where possible
- IPA must be accurate
- Return ONLY valid JSON, no markdown formatting"""


def build_prosody_exercise_prompt(pattern_type: str = "stress") -> str:
    """
    韻律エクササイズ生成用のシステムプロンプトを構築

    Args:
        pattern_type: パターン種別 (stress, rhythm, intonation)

    Returns:
        システムプロンプト文字列
    """
    pattern_guidance = {
        "stress": {
            "focus": "Word and sentence stress patterns",
            "description": "Japanese is a pitch-accent language with relatively even stress. "
            "English uses stress to convey meaning and emphasis.",
            "examples": [
                "REcord (noun) vs reCORD (verb)",
                "PREsent (noun) vs preSENT (verb)",
                "CONtract (noun) vs conTRACT (verb)",
                "I DIDN'T say he stole the money (denial) vs I didn't SAY he stole the money (implied communication)",
            ],
        },
        "rhythm": {
            "focus": "Stress-timed rhythm patterns",
            "description": "English is stress-timed: stressed syllables are roughly equally spaced, "
            "while unstressed syllables are compressed. Japanese is mora-timed.",
            "examples": [
                "CATS chase MICE (3 stressed, regular rhythm)",
                "The CATS are CHASing the MICE (same rhythm despite more syllables)",
                "WALK to WORK vs WALKing to the OFfice (different syllable count, same stress timing)",
            ],
        },
        "intonation": {
            "focus": "Sentence intonation patterns",
            "description": "English uses intonation to convey meaning, emotion, and intention. "
            "Rising intonation for questions, falling for statements, etc.",
            "examples": [
                "You're coming? (rising - genuine question)",
                "You're coming. (falling - statement)",
                "You're COMING? (rise-fall - surprise)",
                "That's interesting... (fall-rise - implied 'but')",
            ],
        },
    }

    info = pattern_guidance.get(pattern_type, pattern_guidance["stress"])
    examples_text = "\n".join(f"- {ex}" for ex in info["examples"])

    return f"""You are a Prosody Exercise Generator for FluentEdge AI, helping Japanese speakers master English prosody.

## Focus Area: {info["focus"]}
{info["description"]}

## Examples
{examples_text}

## Exercise Design for Japanese Speakers
- Japanese speakers tend to give equal weight to all syllables
- Emphasize the contrast between stressed and unstressed syllables
- Show how meaning changes with different stress/intonation patterns
- Use business English contexts

## Output Format
Return ONLY a JSON array:
[
    {{
        "exercise_id": "unique-id",
        "sentence": "The practice sentence",
        "stress_pattern": "Pattern notation (e.g., 'oOo' for weak-STRONG-weak)",
        "intonation_type": "rising|falling|rise-fall|fall-rise",
        "explanation": "What this pattern conveys and how it differs from Japanese",
        "context": "Business situation where this pattern is used"
    }}
]

## Rules
- Generate exercises that highlight the contrast with Japanese prosody
- Include at least one pair showing meaning change through prosody
- Explanations should reference Japanese L1 interference
- Business English context
- Return ONLY valid JSON"""
