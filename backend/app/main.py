from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import auth, health, talk, speaking, review, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="FluentEdge API",
    description="AI-Powered Business English Accelerator",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(talk.router, prefix="/api/talk", tags=["talk"])
app.include_router(speaking.router, prefix="/api/speaking", tags=["speaking"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
