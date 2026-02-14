"""リアルタイム会話ルーター - GPT Realtime APIセッション管理

リアルタイム音声会話のセッション設定と
利用可能な会話モードの情報を提供。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.realtime import (
    RealtimeSessionConfig,
    RealtimeStartRequest,
    ConversationMode,
    ConversationModeList,
)
from app.services.realtime_service import realtime_service

router = APIRouter()


@router.post("/session", response_model=RealtimeSessionConfig)
async def create_realtime_session(
    data: RealtimeStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    リアルタイム会話セッションを作成

    指定されたモードとユーザーのレベルに基づいて、
    WebSocket接続に必要な設定情報を返す。

    クライアントはこのレスポンスのws_urlに接続し、
    session_tokenで認証を行う。
    """
    # モードのバリデーション
    valid_modes = [
        "casual_chat",
        "meeting",
        "debate",
        "presentation_qa",
        "negotiation",
        "small_talk",
    ]
    if data.mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効な会話モードです。有効な値: {', '.join(valid_modes)}",
        )

    # セッション設定を生成
    session_data = realtime_service.create_session(
        mode=data.mode,
        user_level=current_user.target_level,
        scenario=data.scenario_description,
    )

    return RealtimeSessionConfig(
        ws_url=session_data["ws_url"],
        session_token=session_data["session_token"],
        model=session_data["model"],
        voice=session_data["voice"],
        mode=session_data["mode"],
        instructions_summary=session_data["instructions_summary"],
    )


@router.get("/modes", response_model=ConversationModeList)
async def get_conversation_modes(
    current_user: User = Depends(get_current_user),
):
    """
    利用可能な会話モード一覧を取得

    各モードの名前、説明、利用可能状態、
    実装フェーズを返す。
    """
    modes_data = realtime_service.get_available_modes()

    modes = [
        ConversationMode(
            id=m["id"],
            name=m["name"],
            description=m["description"],
            available=m["available"],
            phase=m["phase"],
        )
        for m in modes_data
    ]

    return ConversationModeList(
        modes=modes,
        current_phase="phase2",
    )
