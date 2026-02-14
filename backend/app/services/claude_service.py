"""Claude APIサービス - LLM抽象化レイヤーへのブリッジ

後方互換性のため、全10サービスの
  from app.services.claude_service import claude_service
が引き続き動作する。

内部的には app.llm.service.LLMService に委譲。
プロバイダーの切替は環境変数 LLM_PROVIDER で制御。
"""

from app.llm.service import get_llm_service

# 後方互換: 全サービスの `from app.services.claude_service import claude_service` が動作
claude_service = get_llm_service()
