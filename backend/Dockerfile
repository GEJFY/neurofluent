# =============================================================================
# FluentEdge Backend - Multi-stage Dockerfile
# =============================================================================

# Stage 1: 依存関係インストール
FROM python:3.11-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: 本番イメージ
FROM python:3.11-slim AS production

# セキュリティ: non-root ユーザー
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# 依存関係をコピー
COPY --from=builder /install /usr/local

# アプリケーションコードをコピー
COPY . .

# 所有権変更
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
