"""認証関連スキーマ - ユーザー登録・ログイン・レスポンス"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """ユーザー登録リクエスト"""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    """ログインリクエスト"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""

    id: uuid.UUID
    email: str
    name: str
    target_level: str
    subscription_plan: str
    daily_goal_minutes: int
    native_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT トークンレスポンス"""

    access_token: str
    token_type: str = "bearer"
