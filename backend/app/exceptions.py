"""アプリケーション例外定義"""


class AppError(Exception):
    """アプリケーション基底例外"""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(AppError):
    """認証エラー"""

    def __init__(
        self,
        message: str = "認証に失敗しました",
        details: dict | None = None,
    ):
        super().__init__(message, "AUTHENTICATION_ERROR", 401, details)


class AuthorizationError(AppError):
    """認可エラー"""

    def __init__(
        self,
        message: str = "権限がありません",
        details: dict | None = None,
    ):
        super().__init__(message, "AUTHORIZATION_ERROR", 403, details)


class NotFoundError(AppError):
    """リソース未検出"""

    def __init__(
        self,
        message: str = "リソースが見つかりません",
        details: dict | None = None,
    ):
        super().__init__(message, "NOT_FOUND", 404, details)


class ValidationError(AppError):
    """バリデーションエラー"""

    def __init__(
        self,
        message: str = "入力が不正です",
        details: dict | None = None,
    ):
        super().__init__(message, "VALIDATION_ERROR", 422, details)


class RateLimitError(AppError):
    """レート制限エラー"""

    def __init__(
        self,
        message: str = "リクエスト制限に達しました",
        details: dict | None = None,
    ):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, details)


class LLMProviderError(AppError):
    """LLMプロバイダーエラー"""

    def __init__(
        self,
        message: str = "LLMサービスでエラーが発生しました",
        provider: str = "",
        details: dict | None = None,
    ):
        details = details or {}
        details["provider"] = provider
        super().__init__(message, "LLM_PROVIDER_ERROR", 502, details)


class LLMTimeoutError(LLMProviderError):
    """LLMタイムアウト"""

    def __init__(self, provider: str = "", timeout: float = 0):
        super().__init__(
            f"LLMプロバイダー({provider})がタイムアウトしました",
            provider,
            {"timeout": timeout},
        )
        self.error_code = "LLM_TIMEOUT"
        self.status_code = 504


class LLMRateLimitError(LLMProviderError):
    """LLMレート制限"""

    def __init__(self, provider: str = ""):
        super().__init__(
            f"LLMプロバイダー({provider})のレート制限に達しました",
            provider,
        )
        self.error_code = "LLM_RATE_LIMIT"
        self.status_code = 429


class ExternalServiceError(AppError):
    """外部サービスエラー (Stripe, Azure Speech等)"""

    def __init__(
        self,
        service: str,
        message: str = "外部サービスでエラーが発生しました",
        details: dict | None = None,
    ):
        details = details or {}
        details["service"] = service
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, details)
