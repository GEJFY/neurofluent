"""GPT Realtime API サービス - リアルタイム音声会話管理

Azure OpenAI GPT Realtime APIへのWebSocket接続設定と
セッション管理を提供するサービス。
"""

import hashlib
import logging
import time
import uuid

from app.config import settings
from app.prompts.realtime_modes import (
    CONVERSATION_MODES,
    get_all_modes_summary,
    get_system_prompt,
)

logger = logging.getLogger(__name__)

# モード別の推奨音声設定
MODE_VOICE_MAP = {
    "casual_chat": "alloy",
    "meeting": "echo",
    "debate": "onyx",
    "presentation_qa": "nova",
    "negotiation": "echo",
    "small_talk": "shimmer",
}

# モード別のターン検出設定
MODE_TURN_DETECTION = {
    "casual_chat": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500,
    },
    "meeting": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 700,
    },
    "debate": {
        "type": "server_vad",
        "threshold": 0.6,
        "prefix_padding_ms": 200,
        "silence_duration_ms": 800,
    },
    "presentation_qa": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 1000,
    },
    "negotiation": {
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 800,
    },
    "small_talk": {
        "type": "server_vad",
        "threshold": 0.4,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500,
    },
}


class RealtimeService:
    """GPT Realtime APIのセッション管理サービス"""

    def __init__(self):
        self.endpoint = settings.azure_openai_endpoint.rstrip("/")
        self.api_key = settings.azure_openai_api_key
        self.deployment = settings.azure_openai_realtime_deployment
        self.api_version = "2024-10-01-preview"

    @property
    def _ws_base_url(self) -> str:
        """WebSocket接続のベースURL"""
        # Azure OpenAIのエンドポイントからwssスキームを構築
        host = self.endpoint.replace("https://", "").replace("http://", "")
        return (
            f"wss://{host}/openai/realtime"
            f"?api-version={self.api_version}"
            f"&deployment={self.deployment}"
        )

    def _generate_session_token(self, user_id: str, mode: str) -> str:
        """
        セッショントークンを生成

        ユーザーIDとモードとタイムスタンプからハッシュを生成。
        クライアント側での接続時に認証に使用。

        Args:
            user_id: ユーザーID文字列
            mode: 会話モード

        Returns:
            セッショントークン文字列
        """
        raw = f"{user_id}:{mode}:{time.time()}:{uuid.uuid4().hex}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def create_session(
        self,
        mode: str,
        user_level: str,
        scenario: str | None = None,
    ) -> dict:
        """
        リアルタイム会話セッションの設定を生成

        指定されたモードとユーザーレベルに基づいて、
        WebSocket URL、セッショントークン、システムプロンプトを生成。

        Args:
            mode: 会話モード（casual_chat, meeting, debate等）
            user_level: ユーザーのCEFRレベル
            scenario: カスタムシナリオの説明（任意）

        Returns:
            セッション設定辞書:
                ws_url, session_token, model, voice,
                mode, instructions_summary
        """
        # モードのバリデーション
        if mode not in CONVERSATION_MODES:
            logger.warning(
                "未知のモード '%s' が指定されました。casual_chatにフォールバック。",
                mode,
            )
            mode = "casual_chat"

        mode_config = CONVERSATION_MODES[mode]

        # セッショントークンを生成
        session_token = self._generate_session_token(
            user_id=str(uuid.uuid4()),  # 実際にはユーザーIDを使用
            mode=mode,
        )

        # 音声設定
        voice = MODE_VOICE_MAP.get(mode, "alloy")

        # システムプロンプトにユーザーレベル情報を追加
        system_prompt = get_system_prompt(mode)
        level_addendum = (
            f"\n\n## User Level Information\n"
            f"The user's current English level is CEFR {user_level}. "
            f"Adjust your vocabulary, speech rate, and complexity accordingly."
        )
        if scenario:
            level_addendum += (
                f"\n\n## Custom Scenario\n"
                f"The user has requested the following specific scenario: {scenario}"
            )
        full_instructions = system_prompt + level_addendum

        # 概要テキスト（クライアント表示用）
        instructions_summary = f"{mode_config['name']}: {mode_config['description']}"

        return {
            "ws_url": self._ws_base_url,
            "session_token": session_token,
            "model": self.deployment,
            "voice": voice,
            "mode": mode,
            "instructions_summary": instructions_summary,
            "instructions": full_instructions,
            "api_key": self.api_key,
        }

    def build_realtime_config(
        self,
        mode: str,
        user_level: str,
    ) -> dict:
        """
        GPT Realtime APIのセッション設定を構築

        クライアントがWebSocket接続後に送信する
        session.updateイベントのペイロードを生成。

        Args:
            mode: 会話モード
            user_level: ユーザーのCEFRレベル

        Returns:
            Realtime API設定辞書:
                model, voice, instructions, tools,
                turn_detection, input_audio_format, output_audio_format
        """
        if mode not in CONVERSATION_MODES:
            mode = "casual_chat"

        voice = MODE_VOICE_MAP.get(mode, "alloy")
        turn_detection = MODE_TURN_DETECTION.get(
            mode, MODE_TURN_DETECTION["casual_chat"]
        )

        # システムプロンプトにレベル情報を追加
        system_prompt = get_system_prompt(mode)
        instructions = (
            system_prompt
            + f"\n\nThe user's current English level is CEFR {user_level}."
        )

        # ツール定義（会話中に使用可能な機能）
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "provide_vocabulary_help",
                    "description": (
                        "When the user asks about a word or expression, "
                        "provide the definition, pronunciation guide, "
                        "and example usage."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "word": {
                                "type": "string",
                                "description": "The word or expression to explain",
                            },
                            "context": {
                                "type": "string",
                                "description": "The context in which the word was used",
                            },
                        },
                        "required": ["word"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "end_conversation",
                    "description": (
                        "End the conversation session when the user indicates "
                        "they want to stop or wrap up."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Reason for ending the conversation",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Brief summary of the conversation",
                            },
                        },
                        "required": ["reason"],
                    },
                },
            },
        ]

        return {
            "model": self.deployment,
            "voice": voice,
            "instructions": instructions,
            "tools": tools,
            "turn_detection": turn_detection,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1",
            },
            "temperature": 0.8,
            "max_response_output_tokens": 512,
        }

    def get_available_modes(self) -> list[dict]:
        """
        利用可能な会話モードの一覧を取得

        Returns:
            モード概要のリスト
        """
        return get_all_modes_summary()


# シングルトンインスタンス
realtime_service = RealtimeService()
