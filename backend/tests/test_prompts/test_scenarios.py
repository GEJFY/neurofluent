"""シナリオDBのテスト"""

from app.prompts.scenarios import (
    SCENARIOS,
    get_all_scenario_ids,
    get_scenario,
    get_scenarios_for_mode,
)


class TestGetScenario:
    """get_scenario のテスト"""

    def test_specific_id(self):
        """ID指定で正しいシナリオを取得"""
        scenario = get_scenario("meeting", "mtg-budget-overrun")
        assert scenario["id"] == "mtg-budget-overrun"
        assert scenario["title"] == "Budget Overrun Explanation"

    def test_random_selection(self):
        """ID未指定でランダムにシナリオを取得"""
        scenario = get_scenario("meeting")
        assert "id" in scenario
        assert "title" in scenario
        assert "ai_role" in scenario

    def test_unknown_mode_fallback(self):
        """不明モードでもフォールバックシナリオを返す"""
        scenario = get_scenario("unknown_mode")
        assert "id" in scenario
        assert "title" in scenario

    def test_unknown_id_returns_random(self):
        """不明IDではランダムにシナリオを返す"""
        scenario = get_scenario("meeting", "nonexistent-id")
        assert "id" in scenario
        assert scenario["id"] != "nonexistent-id"


class TestGetScenariosForMode:
    """get_scenarios_for_mode のテスト"""

    def test_meeting_scenarios(self):
        """meetingモードは4件以上のシナリオを持つ"""
        scenarios = get_scenarios_for_mode("meeting")
        assert len(scenarios) >= 4

    def test_negotiation_scenarios(self):
        """negotiationモードにもシナリオが存在する"""
        scenarios = get_scenarios_for_mode("negotiation")
        assert len(scenarios) >= 2

    def test_unknown_mode_returns_empty(self):
        """不明モードは空リストを返す"""
        scenarios = get_scenarios_for_mode("unknown_mode")
        assert scenarios == []


class TestGetAllScenarioIds:
    """get_all_scenario_ids のテスト"""

    def test_returns_at_least_15(self):
        """全シナリオは15件以上"""
        all_ids = get_all_scenario_ids()
        assert len(all_ids) >= 15

    def test_entries_have_required_fields(self):
        """各エントリにid, mode, title, difficultyが存在する"""
        all_ids = get_all_scenario_ids()
        for entry in all_ids:
            assert "id" in entry
            assert "mode" in entry
            assert "title" in entry
            assert "difficulty" in entry

    def test_unique_ids(self):
        """全シナリオIDがユニーク"""
        all_ids = get_all_scenario_ids()
        ids = [entry["id"] for entry in all_ids]
        assert len(ids) == len(set(ids))


class TestScenariosDataIntegrity:
    """SCENARIOSデータの整合性テスト"""

    def test_all_scenarios_have_required_fields(self):
        """全シナリオに必須フィールドが存在する"""
        required_fields = {"id", "title", "ai_role", "learner_goal", "key_phrases"}
        for mode, scenarios in SCENARIOS.items():
            for scenario in scenarios:
                for field in required_fields:
                    assert field in scenario, (
                        f"SCENARIOS['{mode}']['{scenario.get('id', '?')}'] に '{field}' がない"
                    )

    def test_key_phrases_not_empty(self):
        """全シナリオのkey_phrasesが空でない"""
        for mode, scenarios in SCENARIOS.items():
            for scenario in scenarios:
                assert len(scenario["key_phrases"]) > 0, (
                    f"SCENARIOS['{mode}']['{scenario['id']}'] の key_phrases が空"
                )

    def test_at_least_4_modes(self):
        """少なくとも4種類のモードが定義されている"""
        assert len(SCENARIOS) >= 4
