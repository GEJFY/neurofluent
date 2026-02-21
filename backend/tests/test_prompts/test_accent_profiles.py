"""アクセントプロファイルのテスト"""

from app.prompts.accent_profiles import (
    ACCENT_VOICES,
    AUDIO_ENVIRONMENTS,
    build_accent_awareness_prompt,
    get_language_code,
    get_voice_for_accent,
)


class TestGetVoiceForAccent:
    """get_voice_for_accent のテスト"""

    def test_known_accent_female(self):
        """既知アクセント(us) + female で正しい音声名を返す"""
        voice = get_voice_for_accent("us", "female")
        assert voice == "en-US-JennyMultilingualNeural"

    def test_known_accent_male(self):
        """既知アクセント(uk) + male で正しい音声名を返す"""
        voice = get_voice_for_accent("uk", "male")
        assert voice == "en-GB-RyanNeural"

    def test_india_accent(self):
        """インドアクセントの音声名"""
        voice = get_voice_for_accent("india", "female")
        assert voice == "en-IN-NeerjaNeural"

    def test_unknown_accent_fallback_to_us(self):
        """不明アクセントはUSにフォールバック"""
        voice = get_voice_for_accent("unknown_accent", "female")
        assert "en-US" in voice

    def test_unknown_gender_fallback_to_default(self):
        """不明性別はdefault_voiceにフォールバック"""
        voice = get_voice_for_accent("singapore", "nonbinary")
        assert voice == "en-SG-LunaNeural"


class TestGetLanguageCode:
    """get_language_code のテスト"""

    def test_us_language_code(self):
        assert get_language_code("us") == "en-US"

    def test_uk_language_code(self):
        assert get_language_code("uk") == "en-GB"

    def test_india_language_code(self):
        assert get_language_code("india") == "en-IN"

    def test_singapore_language_code(self):
        assert get_language_code("singapore") == "en-SG"

    def test_australia_language_code(self):
        assert get_language_code("australia") == "en-AU"

    def test_unknown_accent_fallback(self):
        """不明アクセントはen-USにフォールバック"""
        assert get_language_code("martian") == "en-US"


class TestBuildAccentAwarenessPrompt:
    """build_accent_awareness_prompt のテスト"""

    def test_uk_accent_prompt(self):
        """UKアクセントで"British English"を含むプロンプトが生成される"""
        prompt = build_accent_awareness_prompt("uk")
        assert "British English" in prompt
        assert "Phonetic Characteristics" in prompt
        assert "Common Expressions" in prompt

    def test_india_accent_prompt(self):
        """インドアクセントで"Indian English"を含むプロンプトが生成される"""
        prompt = build_accent_awareness_prompt("india")
        assert "Indian English" in prompt

    def test_unknown_accent_returns_empty(self):
        """不明アクセントで空文字を返す"""
        prompt = build_accent_awareness_prompt("unknown_accent")
        assert prompt == ""

    def test_us_returns_empty(self):
        """USアクセントはACCENT_FEATURESにないため空文字を返す"""
        prompt = build_accent_awareness_prompt("us")
        assert prompt == ""


class TestAccentVoicesData:
    """ACCENT_VOICES データ構造のテスト"""

    def test_all_entries_have_required_keys(self):
        """全エントリに必要キーが存在する"""
        required_keys = {
            "label",
            "label_ja",
            "voices",
            "default_voice",
            "language_code",
        }
        for accent_id, config in ACCENT_VOICES.items():
            for key in required_keys:
                assert key in config, f"ACCENT_VOICES['{accent_id}'] に '{key}' がない"

    def test_all_entries_have_female_voice(self):
        """全エントリにfemale音声がある"""
        for accent_id, config in ACCENT_VOICES.items():
            assert "female" in config["voices"], (
                f"ACCENT_VOICES['{accent_id}'] に female 音声がない"
            )

    def test_at_least_5_accents(self):
        """少なくとも5種類のアクセントが定義されている"""
        assert len(ACCENT_VOICES) >= 5


class TestAudioEnvironmentsData:
    """AUDIO_ENVIRONMENTS データ構造のテスト"""

    def test_all_entries_have_required_keys(self):
        """全エントリに必要キーが存在する"""
        required_keys = {"label", "description", "ssml_effect", "noise_level"}
        for env_id, config in AUDIO_ENVIRONMENTS.items():
            for key in required_keys:
                assert key in config, (
                    f"AUDIO_ENVIRONMENTS['{env_id}'] に '{key}' がない"
                )

    def test_clean_environment_exists(self):
        """クリーン環境が定義されている"""
        assert "clean" in AUDIO_ENVIRONMENTS
        assert AUDIO_ENVIRONMENTS["clean"]["noise_level"] == 0

    def test_at_least_4_environments(self):
        """少なくとも4種類の環境が定義されている"""
        assert len(AUDIO_ENVIRONMENTS) >= 4
