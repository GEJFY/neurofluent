"""マルチクラウドLLM抽象化レイヤー

Azure AI Foundry, Anthropic Direct, AWS Bedrock, GCP Vertex AI,
OpenAI互換 (Ollama, vLLM) をサポートするマルチクラウドLLM統合モジュール。

使用例:
    from app.llm import LLMService, get_llm_service

    llm = get_llm_service()
    response = await llm.chat([{"role": "user", "content": "Hello"}])
"""

from app.llm.service import LLMService, get_llm_service

__all__ = ["LLMService", "get_llm_service"]
