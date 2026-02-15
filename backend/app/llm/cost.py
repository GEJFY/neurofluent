"""LLMプロバイダー別コスト計算モジュール

入力/出力トークン数とプロバイダー+モデルから推定コスト（USD）を算出する。
料金は2025-2026年時点の公開価格に基づく。
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelPricing:
    """モデルの料金情報（USD / 1Mトークン）"""

    input_price_per_m: float  # 入力トークン 100万あたりの料金
    output_price_per_m: float  # 出力トークン 100万あたりの料金


# プロバイダー×モデル別の料金テーブル
# キー: (provider, model_alias) または (provider, full_model_id)
PRICING_TABLE: dict[tuple[str, str], ModelPricing] = {
    # === Azure AI Foundry (GPT-5 via Azure OpenAI) ===
    ("azure_foundry", "sonnet"): ModelPricing(0.25, 2.0),   # gpt-5-mini
    ("azure_foundry", "haiku"): ModelPricing(0.05, 0.40),   # gpt-5-nano
    ("azure_foundry", "opus"): ModelPricing(1.25, 10.0),    # gpt-5
    # === Anthropic Direct API ===
    ("anthropic", "sonnet"): ModelPricing(3.0, 15.0),
    ("anthropic", "haiku"): ModelPricing(0.80, 4.0),
    ("anthropic", "opus"): ModelPricing(5.0, 25.0),
    # === AWS Bedrock ===
    # Bedrock経由は若干プレミアムがある場合あり（同等として計算）
    ("bedrock", "sonnet"): ModelPricing(3.0, 15.0),
    ("bedrock", "haiku"): ModelPricing(0.80, 4.0),
    ("bedrock", "opus"): ModelPricing(5.0, 25.0),
    # === GCP Vertex AI ===
    ("vertex", "sonnet"): ModelPricing(3.0, 15.0),
    ("vertex", "haiku"): ModelPricing(0.80, 4.0),
    ("vertex", "opus"): ModelPricing(5.0, 25.0),
    # === Local / OpenAI-compatible ===
    # ローカルモデルはコスト0（電気代は含まず）
    ("local", "sonnet"): ModelPricing(0.0, 0.0),
    ("local", "haiku"): ModelPricing(0.0, 0.0),
    ("local", "opus"): ModelPricing(0.0, 0.0),
    ("openai_compat", "sonnet"): ModelPricing(0.0, 0.0),
    ("openai_compat", "haiku"): ModelPricing(0.0, 0.0),
    ("openai_compat", "opus"): ModelPricing(0.0, 0.0),
}

# デフォルト料金（テーブルにないモデルの場合）
DEFAULT_PRICING = ModelPricing(3.0, 15.0)


def estimate_cost(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> dict:
    """推定コストを算出

    Args:
        provider: プロバイダー名（"azure_foundry", "anthropic", etc.）
        model: モデルエイリアス（"sonnet", "haiku"）またはフルID
        input_tokens: 入力トークン数
        output_tokens: 出力トークン数

    Returns:
        {
            "input_cost_usd": float,
            "output_cost_usd": float,
            "total_cost_usd": float,
            "provider": str,
            "model": str,
            "input_tokens": int,
            "output_tokens": int,
        }
    """
    # モデルエイリアスの正規化（フルIDからエイリアスへの変換を試行）
    model_alias = _normalize_model_alias(model)

    pricing = PRICING_TABLE.get(
        (provider, model_alias),
        DEFAULT_PRICING,
    )

    input_cost = (input_tokens / 1_000_000) * pricing.input_price_per_m
    output_cost = (output_tokens / 1_000_000) * pricing.output_price_per_m
    total_cost = input_cost + output_cost

    result = {
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    logger.debug(
        "コスト推定: provider=%s model=%s input=%d output=%d total=$%.6f",
        provider,
        model,
        input_tokens,
        output_tokens,
        total_cost,
    )

    return result


def _normalize_model_alias(model: str) -> str:
    """フルモデルIDをエイリアスに正規化

    Args:
        model: モデル名（エイリアスまたはフルID）

    Returns:
        正規化されたエイリアス（"sonnet", "haiku"）
    """
    model_lower = model.lower()

    if model_lower in ("sonnet", "haiku", "opus"):
        return model_lower

    if "sonnet" in model_lower or "5-mini" in model_lower:
        return "sonnet"
    if "haiku" in model_lower or "5-nano" in model_lower:
        return "haiku"
    if "opus" in model_lower or model_lower == "gpt-5":
        return "opus"

    # ローカルモデルの場合はそのまま返す（料金テーブルで "sonnet" にフォールバック）
    return model_lower
