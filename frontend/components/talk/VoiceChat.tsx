"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  Mic,
  MicOff,
  Phone,
  MessageSquare,
  X,
  Volume2,
  Loader2,
} from "lucide-react";

/**
 * VoiceChat - 音声チャットコンポーネント
 * フルスクリーン音声会話インターフェース
 * - マイクボタン中央配置
 * - 音声波形ビジュアライゼーション
 * - ステータスインジケーター
 * - フィードバックパネル（トグル可能）
 */

interface VoiceChatProps {
  /** セッションID */
  sessionId: string;
  /** 会話モード */
  mode: string;
  /** セッション終了コールバック */
  onEnd: () => void;
}

type VoiceChatStatus =
  | "idle"
  | "listening"
  | "processing"
  | "ai_speaking"
  | "error";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function VoiceChat({ sessionId, mode, onEnd }: VoiceChatProps) {
  const [status, setStatus] = useState<VoiceChatStatus>("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // 音声波形ビジュアライゼーション描画
  const drawVisualization = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    // 平均レベル
    const average = dataArray.reduce((sum, val) => sum + val, 0) / bufferLength;
    setAudioLevel(average / 255);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 中央から放射状の波形
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const maxRadius = Math.min(centerX, centerY) * 0.8;
    const bars = 64;

    for (let i = 0; i < bars; i++) {
      const angle = (i / bars) * Math.PI * 2;
      const dataIndex = Math.floor((i / bars) * bufferLength);
      const value = dataArray[dataIndex] / 255;

      const innerRadius = maxRadius * 0.3;
      const outerRadius = innerRadius + value * maxRadius * 0.7;

      const x1 = centerX + Math.cos(angle) * innerRadius;
      const y1 = centerY + Math.sin(angle) * innerRadius;
      const x2 = centerX + Math.cos(angle) * outerRadius;
      const y2 = centerY + Math.sin(angle) * outerRadius;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle =
        status === "listening"
          ? `rgba(99, 102, 241, ${0.3 + value * 0.7})`
          : status === "ai_speaking"
            ? `rgba(34, 211, 238, ${0.3 + value * 0.7})`
            : `rgba(100, 116, 139, ${0.2 + value * 0.3})`;
      ctx.lineWidth = 2;
      ctx.lineCap = "round";
      ctx.stroke();
    }

    animationFrameRef.current = requestAnimationFrame(drawVisualization);
  }, [status]);

  // マイク開始
  const startListening = useCallback(async () => {
    setError(null);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // Web Audio APIセットアップ
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());

        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];

        // AIの処理を開始
        setStatus("processing");

        // デモ用：モックの処理
        // 実際にはAPIで音声をテキスト変換し、AIレスポンスを取得
        setTimeout(() => {
          const userMessage: ChatMessage = {
            id: `user-${Date.now()}`,
            role: "user",
            content: transcript || "That sounds like a great idea. Let me think about it.",
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, userMessage]);

          setStatus("ai_speaking");

          // AI応答のシミュレーション
          setTimeout(() => {
            const aiMessage: ChatMessage = {
              id: `ai-${Date.now()}`,
              role: "assistant",
              content:
                "That's a thoughtful approach. Would you like to explore that idea further? I think there are some interesting aspects we could discuss.",
              timestamp: new Date(),
            };
            setMessages((prev) => [...prev, aiMessage]);
            setStatus("idle");
          }, 2000);
        }, 1500);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100);
      setStatus("listening");

      // ビジュアライゼーション開始
      animationFrameRef.current = requestAnimationFrame(drawVisualization);
    } catch (err) {
      console.error("Microphone access failed:", err);
      setError("マイクへのアクセスが拒否されました。");
      setStatus("error");
    }
  }, [transcript, drawVisualization]);

  // マイク停止
  const stopListening = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state === "recording"
    ) {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // マイクボタンのトグル
  const handleMicToggle = useCallback(() => {
    if (status === "listening") {
      stopListening();
    } else if (status === "idle" || status === "error") {
      startListening();
    }
  }, [status, startListening, stopListening]);

  // ステータステキスト
  const getStatusText = () => {
    switch (status) {
      case "idle":
        return "Tap to speak";
      case "listening":
        return "Listening...";
      case "processing":
        return "AI is thinking...";
      case "ai_speaking":
        return "AI is speaking...";
      case "error":
        return "Error occurred";
      default:
        return "";
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "listening":
        return "text-primary";
      case "processing":
        return "text-warning";
      case "ai_speaking":
        return "text-accent";
      case "error":
        return "text-red-400";
      default:
        return "text-[var(--color-text-muted)]";
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[var(--color-bg-primary)] flex flex-col">
      {/* ヘッダー */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                status === "idle"
                  ? "bg-green-400"
                  : status === "listening"
                    ? "bg-primary animate-pulse"
                    : status === "ai_speaking"
                      ? "bg-accent animate-pulse"
                      : "bg-warning animate-pulse"
              }`}
            />
            <span className="text-sm font-medium text-[var(--color-text-primary)]">
              Voice Chat
            </span>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/15 text-primary">
            {mode}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* フィードバックトグル */}
          <button
            onClick={() => setShowFeedback(!showFeedback)}
            className={`p-2 rounded-lg transition-colors ${
              showFeedback
                ? "bg-primary/10 text-primary"
                : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
          </button>

          {/* 終了ボタン */}
          <button
            onClick={onEnd}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
          >
            <Phone className="w-3.5 h-3.5" />
            End
          </button>
        </div>
      </div>

      {/* メインエリア */}
      <div className="flex-1 flex flex-col items-center justify-center relative overflow-hidden">
        {/* 波形ビジュアライゼーション */}
        <canvas
          ref={canvasRef}
          width={400}
          height={400}
          className="absolute w-80 h-80 md:w-96 md:h-96 opacity-60"
        />

        {/* ステータス表示 */}
        <div className="relative z-10 flex flex-col items-center gap-6">
          {/* ステータスインジケーター */}
          <div className="text-center space-y-2">
            {status === "processing" && (
              <Loader2 className="w-6 h-6 text-warning animate-spin mx-auto" />
            )}
            {status === "ai_speaking" && (
              <Volume2 className="w-6 h-6 text-accent animate-pulse mx-auto" />
            )}
            <p className={`text-sm font-medium ${getStatusColor()}`}>
              {getStatusText()}
            </p>
          </div>

          {/* マイクボタン */}
          <div className="relative">
            {/* パルスリング */}
            {status === "listening" && (
              <>
                <div
                  className="absolute inset-0 rounded-full bg-primary/20 animate-ping"
                  style={{
                    animationDuration: "2s",
                    inset: "-12px",
                  }}
                />
                <div
                  className="absolute rounded-full bg-primary/10 transition-all duration-100"
                  style={{
                    inset: `${-12 - audioLevel * 30}px`,
                  }}
                />
              </>
            )}
            {status === "ai_speaking" && (
              <div
                className="absolute rounded-full bg-accent/10 animate-pulse"
                style={{ inset: "-16px" }}
              />
            )}

            <button
              onClick={handleMicToggle}
              disabled={status === "processing" || status === "ai_speaking"}
              className={`relative w-24 h-24 md:w-28 md:h-28 rounded-full flex items-center justify-center transition-all duration-200 ${
                status === "listening"
                  ? "bg-primary text-white shadow-lg shadow-primary/30"
                  : status === "processing" || status === "ai_speaking"
                    ? "bg-[var(--color-bg-card)] text-[var(--color-text-muted)] cursor-not-allowed border border-[var(--color-border)]"
                    : "bg-[var(--color-bg-card)] text-[var(--color-text-primary)] border border-[var(--color-border)] hover:border-primary hover:text-primary shadow-lg"
              }`}
            >
              {status === "listening" ? (
                <Mic className="w-10 h-10" />
              ) : status === "processing" ? (
                <Loader2 className="w-10 h-10 animate-spin" />
              ) : status === "ai_speaking" ? (
                <Volume2 className="w-10 h-10 text-accent" />
              ) : (
                <MicOff className="w-10 h-10" />
              )}
            </button>
          </div>

          {/* エラー表示 */}
          {error && (
            <div className="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400 text-center max-w-xs">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* フィードバックパネル（サイドバー） */}
      {showFeedback && (
        <div className="absolute right-0 top-0 bottom-0 w-80 md:w-96 bg-[var(--color-bg-secondary)] border-l border-[var(--color-border)] flex flex-col z-20 animate-slide-in-right">
          {/* パネルヘッダー */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)]">
            <span className="text-sm font-semibold text-[var(--color-text-primary)]">
              Conversation
            </span>
            <button
              onClick={() => setShowFeedback(false)}
              className="p-1 rounded text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* メッセージ一覧 */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-xs text-[var(--color-text-muted)] text-center">
                  Start speaking to see the conversation transcript here.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-3 py-2 text-xs leading-relaxed ${
                      msg.role === "user"
                        ? "bg-primary text-white rounded-br-sm"
                        : "bg-[var(--color-bg-card)] text-[var(--color-text-primary)] border border-[var(--color-border)] rounded-bl-sm"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ボトム情報バー */}
      <div className="flex items-center justify-center px-4 py-3 border-t border-[var(--color-border)]">
        <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-muted)]">
          <span>Session: {sessionId.slice(0, 8)}...</span>
          <span>Messages: {messages.length}</span>
          <span>Mode: {mode}</span>
        </div>
      </div>
    </div>
  );
}
