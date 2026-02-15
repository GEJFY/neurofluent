"""リスニング・シャドーイングルーター - 音声練習機能のAPI

シャドーイング教材の生成、音声評価、TTS変換を提供。
"""

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation import ConversationSession
from app.models.user import User
from app.schemas.listening import (
    ShadowingMaterial,
    ShadowingResult,
    TTSRequest,
)
from app.services.shadowing_service import shadowing_service

router = APIRouter()


@router.get("/shadowing/material", response_model=ShadowingMaterial)
async def generate_shadowing_material(
    current_user: User = Depends(get_current_user),
    topic: str | None = Query(
        default=None,
        description="トピック: business_meeting, earnings_call, team_discussion, client_presentation, casual_networking",
    ),
    difficulty: str = Query(
        default="intermediate",
        description="難易度: beginner, intermediate, advanced",
    ),
    mode: str = Query(
        default="standard",
        description="モード: standard, chunk, parallel",
    ),
):
    """
    シャドーイング教材を動的に生成

    ユーザーのレベルと指定されたトピック・難易度に基づいて、
    2-4文のビジネス英語テキストと付随情報を返す。
    """
    # トピックのバリデーション
    valid_topics = [
        "business_meeting",
        "earnings_call",
        "team_discussion",
        "client_presentation",
        "casual_networking",
    ]
    if topic and topic not in valid_topics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効なトピックです。有効な値: {', '.join(valid_topics)}",
        )

    # 難易度のバリデーション
    valid_difficulties = ["beginner", "intermediate", "advanced"]
    if difficulty not in valid_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"無効な難易度です。有効な値: {', '.join(valid_difficulties)}",
        )

    # トピック未指定時はランダムに選択
    if topic is None:
        import random

        topic = random.choice(valid_topics)

    material = await shadowing_service.generate_material(
        topic=topic,
        difficulty=difficulty,
        user_level=current_user.target_level,
    )

    return material


@router.post("/shadowing/evaluate", response_model=ShadowingResult)
async def evaluate_shadowing(
    audio: UploadFile = File(..., description="ユーザーの音声ファイル（WAV形式）"),
    reference_text: str = Form(..., description="リファレンステキスト"),
    speed: float = Form(default=1.0, ge=0.5, le=2.0, description="再生速度"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    シャドーイング音声を評価

    ユーザーがアップロードした音声ファイルを
    Azure Speech SDKで発音評価し、結果を返す。
    """
    # ファイルサイズチェック（最大10MB）
    content = await audio.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="音声ファイルが大きすぎます（最大10MB）",
        )

    # Content-Typeチェック
    if audio.content_type and not audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="音声ファイルを送信してください",
        )

    try:
        result = await shadowing_service.evaluate_shadowing(
            user_audio=content,
            reference_text=reference_text,
            target_speed=speed,
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音声評価に失敗しました: {str(e)}",
        )


@router.get("/shadowing/history")
async def get_shadowing_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    ユーザーのシャドーイング練習履歴を取得

    シャドーイングモードの会話セッション一覧を返す。
    """
    result = await db.execute(
        select(ConversationSession)
        .where(
            ConversationSession.user_id == current_user.id,
            ConversationSession.mode == "shadowing",
        )
        .order_by(ConversationSession.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    sessions = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "mode": s.mode,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "duration_seconds": s.duration_seconds,
            "overall_score": s.overall_score,
        }
        for s in sessions
    ]


@router.post("/tts")
async def text_to_speech(
    data: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """
    テキストを音声に変換（Text-to-Speech）

    Azure TTSを使用して、指定されたテキストを
    WAV形式の音声に変換して返す。
    """
    try:
        audio_bytes = await shadowing_service.generate_audio(
            text=data.text,
            speed=data.speed,
            voice=data.voice,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=tts_output.wav",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音声合成に失敗しました: {str(e)}",
        )
