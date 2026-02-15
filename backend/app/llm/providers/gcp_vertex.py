"""GCP Vertex AI プロバイダー

GCP Vertex AI 経由で Anthropic Claude モデルを呼び出す。
httpx ベースで以下のエンドポイントに POST:
  https://{region}-aiplatform.googleapis.com/v1/projects/{project}/
  locations/{region}/publishers/anthropic/models/{model}:rawPredict
google-auth でアクセストークン取得。オプショナルインポート。
"""

import logging

import httpx

from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

# オプショナルインポート: google-auth
try:
    import google.auth
    import google.auth.transport.requests

    HAS_GOOGLE_AUTH = True
except ImportError:
    HAS_GOOGLE_AUTH = False
    google = None  # type: ignore[assignment]

# Vertex AIモデルマッピング
MODEL_MAP = {
    "sonnet": settings.gcp_vertex_model_sonnet,
    "haiku": settings.gcp_vertex_model_haiku,
}


class GCPVertexProvider(LLMProvider):
    """GCP Vertex AI経由でClaudeモデルを呼び出すプロバイダー"""

    def __init__(self):
        if not HAS_GOOGLE_AUTH:
            raise ImportError(
                "GCP Vertex AIプロバイダーには google-auth が必要です。"
                "インストール: pip install google-auth"
            )

        self.project_id = settings.gcp_project_id
        self.region = settings.gcp_region
        self.timeout = httpx.Timeout(60.0, connect=10.0)

        if not self.project_id:
            logger.warning("GCP_PROJECT_ID が未設定です")

        # 認証情報の取得
        self._credentials = None
        self._auth_request = None

        logger.info(
            "GCP Vertex AI プロバイダー初期化: project=%s region=%s",
            self.project_id,
            self.region,
        )

    @property
    def name(self) -> str:
        return "vertex"

    def _resolve_model(self, model: str) -> str:
        """モデルのエイリアスをVertex AI用モデルIDに解決"""
        return MODEL_MAP.get(model, model)

    def _get_access_token(self) -> str:
        """Google Cloud認証トークンを取得・更新

        Application Default Credentials (ADC) を使用。
        """
        if self._credentials is None:
            self._credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self._auth_request = google.auth.transport.requests.Request()

        # トークンの更新
        self._credentials.refresh(self._auth_request)
        return self._credentials.token

    def _build_url(self, model: str) -> str:
        """Vertex AI エンドポイントURLを構築"""
        resolved_model = self._resolve_model(model)
        return (
            f"https://{self.region}-aiplatform.googleapis.com/v1/"
            f"projects/{self.project_id}/locations/{self.region}/"
            f"publishers/anthropic/models/{resolved_model}:rawPredict"
        )

    def _build_headers(self) -> dict:
        """リクエストヘッダーを構築"""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _build_body(
        self,
        messages: list[dict],
        max_tokens: int,
        system: str | None,
    ) -> dict:
        """Vertex AI用リクエストボディを構築

        rawPredict エンドポイントはAnthropic Messages API形式を受け付ける。
        """
        body = {
            "anthropic_version": "vertex-2023-10-16",
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            body["system"] = system
        return body

    async def chat(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """Vertex AIにメッセージを送信してテキスト応答を取得"""
        body = self._build_body(messages, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(model),
                headers=self._build_headers(),
                json=body,
            )

            if response.status_code != 200:
                logger.error(
                    "Vertex AI API エラー: status=%d body=%s",
                    response.status_code,
                    response.text[:500],
                )
                raise httpx.HTTPStatusError(
                    f"Vertex AI API returned {response.status_code}",
                    request=response.request,
                    response=response,
                )

            data = response.json()
            return self._extract_text_from_anthropic_response(data)

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Vertex AIにメッセージを送信してJSON応答を取得・パース"""
        raw = await self.chat(messages, model, max_tokens, system)
        return self._parse_json_response(raw)

    async def get_usage_info(
        self,
        messages: list[dict],
        model: str = "haiku",
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> dict:
        """Vertex AIを呼び出し、レスポンスとトークン使用量を返す"""
        body = self._build_body(messages, max_tokens, system)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self._build_url(model),
                headers=self._build_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            text = self._extract_text_from_anthropic_response(data)
            usage = self._extract_usage_from_anthropic_response(data)

            return {
                "text": text,
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "model": self._resolve_model(model),
            }
