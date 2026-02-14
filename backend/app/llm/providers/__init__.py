"""LLMプロバイダーレジストリ

利用可能なプロバイダーのマッピングを提供する。
各プロバイダーはオプショナルインポートのため、
必要な依存関係がインストールされていなくてもインポートエラーにならない。
"""

from app.llm.providers.anthropic_direct import AnthropicDirectProvider
from app.llm.providers.aws_bedrock import AWSBedrockProvider
from app.llm.providers.azure_foundry import AzureFoundryProvider
from app.llm.providers.gcp_vertex import GCPVertexProvider
from app.llm.providers.openai_compat import OpenAICompatibleProvider

# プロバイダー名 -> プロバイダークラスのマッピング
PROVIDER_MAP = {
    "azure_foundry": AzureFoundryProvider,
    "anthropic": AnthropicDirectProvider,
    "bedrock": AWSBedrockProvider,
    "vertex": GCPVertexProvider,
    "local": OpenAICompatibleProvider,
    "openai_compat": OpenAICompatibleProvider,
}

__all__ = [
    "PROVIDER_MAP",
    "AzureFoundryProvider",
    "AnthropicDirectProvider",
    "AWSBedrockProvider",
    "GCPVertexProvider",
    "OpenAICompatibleProvider",
]
