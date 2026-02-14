# =============================================================================
# FluentEdge AI - Frontend Dockerfile
# Multi-stage build for Next.js 15 production image
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Dependencies - パッケージインストール
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json package-lock.json* ./
RUN \
  if [ -f package-lock.json ]; then npm ci --ignore-scripts; \
  else npm install --ignore-scripts; \
  fi

# ---------------------------------------------------------------------------
# Stage 2: Builder - ビルド実行
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# API URLをビルド時に注入
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Telemetry無効化
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# ---------------------------------------------------------------------------
# Stage 3: Runner - 本番実行環境（最小構成）
# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# セキュリティ: 非rootユーザーで実行
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# standalone出力をコピー
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# ラベル
LABEL org.opencontainers.image.title="FluentEdge AI Frontend"
LABEL org.opencontainers.image.description="Next.js 15 frontend for FluentEdge AI"
LABEL org.opencontainers.image.vendor="FluentEdge"
LABEL org.opencontainers.image.source="https://github.com/fluentedge/fluentedge-ai"

CMD ["node", "server.js"]
