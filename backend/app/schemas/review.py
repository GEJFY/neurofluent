"""復習（Spaced Repetition）スキーマ"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReviewItemResponse(BaseModel):
    """復習アイテムレスポンス"""

    id: uuid.UUID
    item_type: str
    content: dict
    next_review_at: datetime | None = None
    ease_factor: float
    interval_days: int
    repetitions: int

    model_config = {"from_attributes": True}


class ReviewCompleteRequest(BaseModel):
    """復習完了リクエスト - FSRSレーティング"""

    item_id: uuid.UUID
    rating: int = Field(ge=1, le=4, description="評価（1=Again, 2=Hard, 3=Good, 4=Easy）")


class ReviewCompleteResponse(BaseModel):
    """復習完了レスポンス - 次回復習スケジュール"""

    next_review_at: datetime
    new_interval_days: int
    new_ease_factor: float
