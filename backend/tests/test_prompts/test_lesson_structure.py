"""レッスン構造化プロンプトのテスト"""

from app.prompts.lesson_structure import (
    LESSON_PHASES,
    build_main_activity_prompt,
    build_review_prompt,
    build_warmup_prompt,
)


SAMPLE_SCENARIO = {
    "id": "test-scenario",
    "title": "Test Budget Meeting",
    "description": "A test scenario for budget discussion",
    "ai_role": "the CFO demanding answers",
    "learner_goal": "Explain budget overrun clearly",
    "key_phrases": [
        "I'd like to walk you through...",
        "Going forward, our plan is to...",
    ],
    "challenges": [
        "CFO asks tough questions",
        "CFO demands specific numbers",
    ],
}


class TestLessonPhases:
    """LESSON_PHASES 定義のテスト"""

    def test_three_phases_defined(self):
        """warmup, main, reviewの3フェーズが定義されている"""
        assert "warmup" in LESSON_PHASES
        assert "main" in LESSON_PHASES
        assert "review" in LESSON_PHASES

    def test_phases_have_required_keys(self):
        """各フェーズにlabel, duration_minutes, goalが存在する"""
        for phase_id, config in LESSON_PHASES.items():
            assert "label" in config, f"LESSON_PHASES['{phase_id}'] に 'label' がない"
            assert "duration_minutes" in config
            assert "goal" in config


class TestBuildWarmupPrompt:
    """build_warmup_prompt のテスト"""

    def test_contains_warmup_header(self):
        """プロンプトに"WARM-UP"が含まれる"""
        prompt = build_warmup_prompt("meeting", SAMPLE_SCENARIO)
        assert "WARM-UP" in prompt

    def test_contains_key_phrases(self):
        """プロンプトにkey_phrasesが含まれる"""
        prompt = build_warmup_prompt("meeting", SAMPLE_SCENARIO)
        assert "I'd like to walk you through" in prompt
        assert "Going forward" in prompt

    def test_contains_scenario_title(self):
        """プロンプトにシナリオタイトルが含まれる"""
        prompt = build_warmup_prompt("meeting", SAMPLE_SCENARIO)
        assert "Test Budget Meeting" in prompt

    def test_user_level_included(self):
        """ユーザーレベルがプロンプトに含まれる"""
        prompt = build_warmup_prompt("meeting", SAMPLE_SCENARIO, user_level="C1")
        assert "C1" in prompt


class TestBuildMainActivityPrompt:
    """build_main_activity_prompt のテスト"""

    def test_contains_main_activity_header(self):
        """プロンプトに"MAIN ACTIVITY"が含まれる"""
        prompt = build_main_activity_prompt("meeting", SAMPLE_SCENARIO)
        assert "MAIN ACTIVITY" in prompt

    def test_contains_ai_role(self):
        """プロンプトにai_roleが含まれる"""
        prompt = build_main_activity_prompt("meeting", SAMPLE_SCENARIO)
        assert "the CFO demanding answers" in prompt

    def test_contains_challenges(self):
        """プロンプトにchallengesが含まれる"""
        prompt = build_main_activity_prompt("meeting", SAMPLE_SCENARIO)
        assert "CFO asks tough questions" in prompt

    def test_weakness_history_included(self):
        """weakness_historyがプロンプトに反映される"""
        weaknesses = ["article errors (a/the)", "subject omission"]
        prompt = build_main_activity_prompt(
            "meeting", SAMPLE_SCENARIO, weakness_history=weaknesses
        )
        assert "article errors" in prompt
        assert "Known Weaknesses" in prompt

    def test_no_weakness_section_when_none(self):
        """weakness_historyがNoneならweakness_sectionが含まれない"""
        prompt = build_main_activity_prompt("meeting", SAMPLE_SCENARIO)
        assert "Known Weaknesses" not in prompt


class TestBuildReviewPrompt:
    """build_review_prompt のテスト"""

    def test_contains_review_header(self):
        """プロンプトに"REVIEW"が含まれる"""
        prompt = build_review_prompt("meeting", SAMPLE_SCENARIO)
        assert "REVIEW" in prompt

    def test_contains_key_phrases(self):
        """プロンプトにkey_phrasesが含まれる"""
        prompt = build_review_prompt("meeting", SAMPLE_SCENARIO)
        assert "I'd like to walk you through" in prompt

    def test_conversation_history_included(self):
        """会話履歴がプロンプトに反映される"""
        history = [
            {"role": "user", "content": "I'd like to explain the budget situation."},
            {"role": "assistant", "content": "Go ahead, I'm listening."},
        ]
        prompt = build_review_prompt(
            "meeting", SAMPLE_SCENARIO, conversation_history=history
        )
        assert "budget situation" in prompt
        assert "Learner" in prompt

    def test_no_history_when_none(self):
        """会話履歴がNoneでもエラーにならない"""
        prompt = build_review_prompt("meeting", SAMPLE_SCENARIO)
        assert "REVIEW" in prompt
