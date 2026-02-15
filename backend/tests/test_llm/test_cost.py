"""LLMコスト計算モジュールのテスト"""

import pytest

from app.llm.cost import (
    DEFAULT_PRICING,
    PRICING_TABLE,
    ModelPricing,
    _normalize_model_alias,
    estimate_cost,
)


class TestModelPricing:
    """ModelPricingデータクラスのテスト"""

    def test_frozen_dataclass(self):
        """immutableであること"""
        pricing = ModelPricing(1.0, 2.0)
        with pytest.raises(AttributeError):
            pricing.input_price_per_m = 3.0

    def test_pricing_values(self):
        """値が正しく格納される"""
        pricing = ModelPricing(0.25, 2.0)
        assert pricing.input_price_per_m == 0.25
        assert pricing.output_price_per_m == 2.0


class TestPricingTable:
    """料金テーブルのテスト"""

    def test_azure_foundry_gpt5_pricing(self):
        """Azure Foundry GPT-5モデルの料金が設定されている"""
        assert ("azure_foundry", "sonnet") in PRICING_TABLE
        assert ("azure_foundry", "haiku") in PRICING_TABLE
        assert ("azure_foundry", "opus") in PRICING_TABLE

        # GPT-5-mini (sonnet)
        assert PRICING_TABLE[("azure_foundry", "sonnet")].input_price_per_m == 0.25
        assert PRICING_TABLE[("azure_foundry", "sonnet")].output_price_per_m == 2.0

        # GPT-5-nano (haiku)
        assert PRICING_TABLE[("azure_foundry", "haiku")].input_price_per_m == 0.05
        assert PRICING_TABLE[("azure_foundry", "haiku")].output_price_per_m == 0.40

        # GPT-5 (opus)
        assert PRICING_TABLE[("azure_foundry", "opus")].input_price_per_m == 1.25
        assert PRICING_TABLE[("azure_foundry", "opus")].output_price_per_m == 10.0

    def test_local_models_are_free(self):
        """ローカルモデルのコストが0であること"""
        for alias in ("sonnet", "haiku", "opus"):
            pricing = PRICING_TABLE[("local", alias)]
            assert pricing.input_price_per_m == 0.0
            assert pricing.output_price_per_m == 0.0

    def test_all_providers_have_three_tiers(self):
        """全プロバイダーがsonnet/haiku/opusの3階層を持つ"""
        providers = {"azure_foundry", "anthropic", "bedrock", "vertex", "local", "openai_compat"}
        for provider in providers:
            for alias in ("sonnet", "haiku", "opus"):
                assert (provider, alias) in PRICING_TABLE, f"Missing: ({provider}, {alias})"


class TestNormalizeModelAlias:
    """モデルエイリアス正規化のテスト"""

    def test_direct_aliases(self):
        """直接エイリアスがそのまま返る"""
        assert _normalize_model_alias("sonnet") == "sonnet"
        assert _normalize_model_alias("haiku") == "haiku"
        assert _normalize_model_alias("opus") == "opus"

    def test_case_insensitive(self):
        """大文字小文字を区別しない"""
        assert _normalize_model_alias("SONNET") == "sonnet"
        assert _normalize_model_alias("Haiku") == "haiku"

    def test_gpt5_model_names(self):
        """GPT-5モデル名からのエイリアス解決"""
        assert _normalize_model_alias("gpt-5-mini") == "sonnet"
        assert _normalize_model_alias("gpt-5-nano") == "haiku"
        assert _normalize_model_alias("gpt-5") == "opus"

    def test_claude_model_names(self):
        """Claudeモデル名からのエイリアス解決"""
        assert _normalize_model_alias("claude-sonnet-4-5-20250929") == "sonnet"
        assert _normalize_model_alias("claude-haiku-4-5-20251001") == "haiku"
        assert _normalize_model_alias("claude-opus-4-6") == "opus"

    def test_unknown_model(self):
        """不明なモデルはそのまま小文字で返る"""
        assert _normalize_model_alias("llama3.1:8b") == "llama3.1:8b"


class TestEstimateCost:
    """コスト推定のテスト"""

    def test_azure_foundry_gpt5_mini_cost(self):
        """GPT-5-mini (sonnet) のコスト計算"""
        result = estimate_cost("azure_foundry", "sonnet", 1_000_000, 1_000_000)
        assert result["input_cost_usd"] == 0.25
        assert result["output_cost_usd"] == 2.0
        assert result["total_cost_usd"] == 2.25
        assert result["provider"] == "azure_foundry"
        assert result["model"] == "sonnet"

    def test_azure_foundry_gpt5_nano_cost(self):
        """GPT-5-nano (haiku) のコスト計算"""
        result = estimate_cost("azure_foundry", "haiku", 1_000_000, 1_000_000)
        assert result["input_cost_usd"] == 0.05
        assert result["output_cost_usd"] == 0.40
        assert result["total_cost_usd"] == 0.45

    def test_zero_tokens(self):
        """トークン0でコスト0"""
        result = estimate_cost("azure_foundry", "sonnet", 0, 0)
        assert result["total_cost_usd"] == 0.0

    def test_small_token_count(self):
        """少量トークンのコスト計算"""
        result = estimate_cost("azure_foundry", "haiku", 1000, 500)
        assert result["input_cost_usd"] == pytest.approx(0.00005, abs=1e-8)
        assert result["output_cost_usd"] == pytest.approx(0.0002, abs=1e-8)

    def test_full_model_id_normalization(self):
        """フルモデルIDが正規化されてコスト計算される"""
        result = estimate_cost("azure_foundry", "gpt-5-mini", 1_000_000, 0)
        assert result["input_cost_usd"] == 0.25

    def test_unknown_model_uses_default(self):
        """不明なモデルはデフォルト料金を使用"""
        result = estimate_cost("unknown_provider", "unknown_model", 1_000_000, 1_000_000)
        assert result["input_cost_usd"] == DEFAULT_PRICING.input_price_per_m
        assert result["output_cost_usd"] == DEFAULT_PRICING.output_price_per_m

    def test_result_structure(self):
        """戻り値の構造が正しいこと"""
        result = estimate_cost("azure_foundry", "sonnet", 100, 50)
        assert "input_cost_usd" in result
        assert "output_cost_usd" in result
        assert "total_cost_usd" in result
        assert "provider" in result
        assert "model" in result
        assert "input_tokens" in result
        assert "output_tokens" in result
        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 50

    def test_local_model_free(self):
        """ローカルモデルのコストが0"""
        result = estimate_cost("local", "sonnet", 1_000_000, 1_000_000)
        assert result["total_cost_usd"] == 0.0
