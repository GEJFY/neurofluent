from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.logging_config import setup_logging
from app.middleware.error_handler import register_error_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.routers import (
    analytics,
    analytics_router,
    auth,
    comprehension,
    health,
    # Phase 2: 音声統合
    listening,
    # Phase 3: 学習最適化
    mogomogo,
    pattern,
    # Phase 4: 高度な機能
    pronunciation,
    realtime,
    review,
    speaking,
    subscription,
    talk,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield
    await engine.dispose()


app = FastAPI(
    title="FluentEdge API",
    description="AI-Powered Business English Accelerator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_error_handlers(app)

# Phase 1 (MVP)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(talk.router, prefix="/api/talk", tags=["talk"])
app.include_router(speaking.router, prefix="/api/speaking", tags=["speaking"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Phase 2: 音声統合
app.include_router(listening.router, prefix="/api/listening", tags=["listening"])
app.include_router(
    pattern.router, prefix="/api/speaking/pattern", tags=["pattern-practice"]
)
app.include_router(
    realtime.router, prefix="/api/talk/realtime", tags=["realtime-voice"]
)

# Phase 3: 学習最適化
app.include_router(mogomogo.router, prefix="/api/listening/mogomogo", tags=["mogomogo"])
app.include_router(
    analytics_router.router,
    prefix="/api/analytics/advanced",
    tags=["analytics-advanced"],
)
app.include_router(
    subscription.router, prefix="/api/subscription", tags=["subscription"]
)

# Phase 4: 高度な機能
app.include_router(
    pronunciation.router, prefix="/api/speaking/pronunciation", tags=["pronunciation"]
)
app.include_router(
    comprehension.router, prefix="/api/listening/comprehension", tags=["comprehension"]
)
