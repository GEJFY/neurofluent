"""会話練習(Talk)ルーター - AIとの会話セッション管理"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation import ConversationMessage, ConversationSession
from app.models.user import User
from app.prompts.conversation import build_conversation_system_prompt
from app.prompts.scenarios import get_all_scenario_ids, get_scenario, get_scenarios_for_mode
from app.schemas.talk import (
    FeedbackData,
    SessionListResponse,
    SessionResponse,
    TalkMessageRequest,
    TalkMessageResponse,
    TalkStartRequest,
)
from app.services.claude_service import claude_service
from app.services.feedback_service import feedback_service

router = APIRouter()


@router.post("/start", response_model=SessionResponse)
async def start_session(
    data: TalkStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """会話セッションを開始し、AIの最初のメッセージを生成"""

    # シナリオを取得（scenario_idが指定されていればDBから、なければランダム or カスタム）
    scenario = None
    if data.scenario_id:
        scenario = get_scenario(data.mode, data.scenario_id)
    elif not data.scenario_description:
        # scenario_idもcustom descriptionもない場合、ランダムシナリオを選択
        scenario = get_scenario(data.mode)

    # セッションを作成
    scenario_desc = data.scenario_description
    if scenario and not scenario_desc:
        scenario_desc = f"[{scenario.get('id', '')}] {scenario.get('title', '')}"

    session = ConversationSession(
        user_id=current_user.id,
        mode=data.mode,
        scenario_description=scenario_desc,
    )
    db.add(session)
    await db.flush()

    # システムプロンプトを構築（シナリオ統合）
    system_prompt = build_conversation_system_prompt(
        mode=data.mode,
        user_level=current_user.target_level,
        scenario_description=data.scenario_description,
        native_language=current_user.native_language,
        scenario=scenario,
    )

    # AIの初回メッセージを生成
    opening_messages = [
        {
            "role": "user",
            "content": (
                "Please start the conversation. Greet me and set the scene "
                "for our practice scenario. Keep it brief (1-2 sentences)."
            ),
        }
    ]

    ai_response = await claude_service.chat(
        messages=opening_messages,
        model="sonnet",
        max_tokens=256,
        system=system_prompt,
    )

    # AIメッセージをDBに保存
    ai_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=ai_response,
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(session)
    await db.refresh(ai_message)

    return SessionResponse(
        id=session.id,
        mode=session.mode,
        scenario_description=session.scenario_description,
        started_at=session.started_at,
        messages=[
            TalkMessageResponse(
                id=ai_message.id,
                role=ai_message.role,
                content=ai_message.content,
                feedback=None,
                created_at=ai_message.created_at,
            )
        ],
    )


@router.post("/message", response_model=TalkMessageResponse)
async def send_message(
    data: TalkMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ユーザーメッセージを送信し、AIの応答とフィードバックを取得"""

    # セッション存在確認
    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == data.session_id,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません",
        )

    # ユーザーメッセージを保存
    user_message = ConversationMessage(
        session_id=session.id,
        role="user",
        content=data.content,
    )
    db.add(user_message)
    await db.flush()

    # 既存メッセージを取得して会話履歴を構築
    msg_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session.id)
        .order_by(ConversationMessage.created_at)
    )
    all_messages = msg_result.scalars().all()

    # Claude API用のメッセージ履歴を構築
    conversation_history = []
    for msg in all_messages:
        role = msg.role
        # Claude APIは"user"と"assistant"のみ受け付ける
        if role not in ("user", "assistant"):
            continue
        conversation_history.append({"role": role, "content": msg.content})

    # シナリオを復元（scenario_descriptionからscenario_idを抽出）
    scenario = _extract_scenario_from_session(session)

    # システムプロンプトを構築
    system_prompt = build_conversation_system_prompt(
        mode=session.mode,
        user_level=current_user.target_level,
        scenario_description=session.scenario_description,
        native_language=current_user.native_language,
        scenario=scenario,
    )

    # AI応答を生成
    ai_response = await claude_service.chat(
        messages=conversation_history,
        model="sonnet",
        max_tokens=512,
        system=system_prompt,
    )

    # 過去セッションから弱点履歴を取得
    weakness_history = await _get_weakness_history(current_user.id, db)

    # フィードバックを非同期的に生成（ユーザーの最新メッセージに対して）
    feedback_data = await feedback_service.generate_feedback(
        user_text=data.content,
        conversation_context=[
            {"role": m.role, "content": m.content} for m in all_messages[-6:]
        ],
        user_level=current_user.target_level,
        mode=session.mode,
        weakness_history=weakness_history,
    )

    # フィードバックをユーザーメッセージに保存
    user_message.feedback = feedback_data.model_dump()
    await db.flush()

    # AIメッセージを保存
    ai_message = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=ai_response,
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)

    return TalkMessageResponse(
        id=ai_message.id,
        role=ai_message.role,
        content=ai_message.content,
        feedback=feedback_data,
        created_at=ai_message.created_at,
    )


@router.get("/scenarios")
async def list_scenarios(
    mode: str | None = Query(default=None, description="モードでフィルタ"),
):
    """利用可能なシナリオ一覧を取得"""
    if mode:
        scenarios = get_scenarios_for_mode(mode)
        return [
            {
                "id": s["id"],
                "mode": mode,
                "title": s["title"],
                "description": s.get("description", ""),
                "difficulty": s.get("difficulty", "B2"),
                "accent_context": s.get("accent_context"),
            }
            for s in scenarios
        ]
    return get_all_scenario_ids()


@router.get("/sessions", response_model=list[SessionListResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """ユーザーの会話セッション一覧を取得（ページネーション対応）"""

    result = await db.execute(
        select(ConversationSession)
        .where(ConversationSession.user_id == current_user.id)
        .order_by(ConversationSession.started_at.desc())
        .offset(offset)
        .limit(limit)
    )
    sessions = result.scalars().all()

    return [
        SessionListResponse(
            id=s.id,
            mode=s.mode,
            started_at=s.started_at,
            duration_seconds=s.duration_seconds,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """セッション詳細（全メッセージ含む）を取得"""

    result = await db.execute(
        select(ConversationSession).where(
            ConversationSession.id == session_id,
            ConversationSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません",
        )

    # メッセージを取得
    msg_result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == session.id)
        .order_by(ConversationMessage.created_at)
    )
    messages = msg_result.scalars().all()

    return SessionResponse(
        id=session.id,
        mode=session.mode,
        scenario_description=session.scenario_description,
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_seconds=session.duration_seconds,
        overall_score=session.overall_score,
        messages=[
            TalkMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                feedback=FeedbackData(**m.feedback) if m.feedback else None,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


# --- プライベートヘルパー ---


def _extract_scenario_from_session(session: ConversationSession) -> dict | None:
    """セッションのscenario_descriptionからシナリオを復元"""
    desc = session.scenario_description
    if not desc or not desc.startswith("["):
        return None
    # "[scenario-id] Title" 形式からIDを抽出
    try:
        scenario_id = desc.split("]")[0].lstrip("[").strip()
        if scenario_id:
            return get_scenario(session.mode, scenario_id)
    except (IndexError, ValueError):
        pass
    return None


async def _get_weakness_history(
    user_id: uuid.UUID,
    db: AsyncSession,
    max_sessions: int = 5,
) -> list[str]:
    """過去セッションのフィードバックから頻出弱点を抽出"""
    result = await db.execute(
        select(ConversationMessage)
        .join(ConversationSession)
        .where(
            ConversationSession.user_id == user_id,
            ConversationMessage.role == "user",
            ConversationMessage.feedback.isnot(None),
        )
        .order_by(ConversationMessage.created_at.desc())
        .limit(max_sessions * 10)  # 直近数セッション分のメッセージ
    )
    messages = result.scalars().all()

    # 文法エラーのパターンを集計
    error_patterns: dict[str, int] = {}
    for msg in messages:
        feedback = msg.feedback
        if not feedback or not isinstance(feedback, dict):
            continue
        for error in feedback.get("grammar_errors", []):
            explanation = error.get("explanation", "")
            if explanation:
                # エラー説明をキーにして頻度を集計
                error_patterns[explanation] = error_patterns.get(explanation, 0) + 1

    # 頻度順にソートして上位5件を返す
    sorted_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
    return [pattern for pattern, _count in sorted_patterns[:5]]
