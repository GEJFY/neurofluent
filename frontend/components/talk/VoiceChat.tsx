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
  AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api";

/**
 * VoiceChat - 音声チャットコンポーネント
 * Web Speech API（STT）+ Talk API（AI応答）+ Azure TTS（音声再生）
 *
 * フロー:
 * 1. マイクボタン押下 → SpeechRecognition で音声をテキスト変換
 * 2. テキストを api.sendMessage() で送信 → AI応答テキスト取得
 * 3. api.requestTTS() でAI応答を音声化 → Audio再生
 */

interface VoiceChatProps {
  sessionId: string;
  mode: string;
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

// SpeechRecognition対応チェック
function getSpeechRecognition(): SpeechRecognitionConstructor | null {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

export default function VoiceChat({ sessionId, mode, onEnd }: VoiceChatProps) {
  const [status, setStatus] = useState<VoiceChatStatus>("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showFeedback, setShowFeedback] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSupported] = useState(() => getSpeechRecognition() !== null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch {}
      }
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (audioContextRef.current) {
        try { audioContextRef.current.close(); } catch {}
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

    const average = dataArray.reduce((sum, val) => sum + val, 0) / bufferLength;
    setAudioLevel(average / 255);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

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

  // AI応答を処理 (Talk API + TTS)
  const processAIResponse = useCallback(async (userText: string) => {
    // ユーザーメッセージ追加
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: userText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setStatus("processing");

    try {
      // Talk APIでAI応答取得
      const response = await api.sendMessage(sessionId, userText);
      const aiContent = response.content || "I understand. Could you tell me more?";

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: aiContent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);

      // TTS で音声再生
      setStatus("ai_speaking");
      try {
        const audioBlob = await api.requestTTS(aiContent, "en-US-JennyMultilingualNeural", 1.0);
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          audioRef.current = null;
          setStatus("idle");
        };
        audio.onerror = () => {
          URL.revokeObjectURL(audioUrl);
          audioRef.current = null;
          setStatus("idle");
        };
        await audio.play();
      } catch {
        // TTS失敗時はテキスト表示のみでidle状態に戻す
        console.warn("TTS playback failed, continuing with text only");
        setStatus("idle");
      }
    } catch (err) {
      console.error("AI response failed:", err);
      setError("AI応答の取得に失敗しました。もう一度お試しください。");
      setStatus("error");
    }
  }, [sessionId]);

  // マイク開始 + SpeechRecognition
  const startListening = useCallback(async () => {
    setError(null);
    setTranscript("");

    const SpeechRecognitionClass = getSpeechRecognition();
    if (!SpeechRecognitionClass) {
      setError("このブラウザは音声認識に対応していません。Chrome または Edge をご利用ください。");
      return;
    }

    try {
      // マイクアクセス (ビジュアライゼーション用)
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      });
      streamRef.current = stream;

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // SpeechRecognition開始
      const recognition = new SpeechRecognitionClass();
      recognition.lang = "en-US";
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      let finalTranscript = "";

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interim += result[0].transcript;
          }
        }
        setTranscript(finalTranscript + interim);
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === "no-speech") {
          setError("音声が検出されませんでした。もう一度お試しください。");
        } else if (event.error === "not-allowed") {
          setError("マイクへのアクセスが拒否されました。");
        }
        stream.getTracks().forEach((track) => track.stop());
        setStatus("idle");
      };

      recognition.onend = () => {
        // マイクストリーム停止
        stream.getTracks().forEach((track) => track.stop());
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }

        const textToSend = finalTranscript.trim();
        if (textToSend) {
          processAIResponse(textToSend);
        } else {
          setStatus("idle");
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
      setStatus("listening");

      // ビジュアライゼーション開始
      animationFrameRef.current = requestAnimationFrame(drawVisualization);
    } catch (err) {
      console.error("Microphone access failed:", err);
      setError("マイクへのアクセスが拒否されました。");
      setStatus("error");
    }
  }, [drawVisualization, processAIResponse]);

  // マイク停止
  const stopListening = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
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

  // AI音声停止
  const stopAISpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setStatus("idle");
  }, []);

  // ステータステキスト
  const getStatusText = () => {
    switch (status) {
      case "idle":
        return "Tap to speak";
      case "listening":
        return transcript ? `"${transcript}"` : "Listening...";
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

  // ブラウザ非対応の場合
  if (!isSupported) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-3 max-w-sm">
          <AlertCircle className="w-10 h-10 text-warning mx-auto" />
          <p className="text-sm text-[var(--color-text-primary)] font-medium">
            Voice Chat is not available
          </p>
          <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
            このブラウザは音声認識 (Web Speech API) に対応していません。
            Chrome、Edge、または Safari をご利用ください。
          </p>
          <button
            onClick={onEnd}
            className="px-4 py-2 rounded-lg text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
          >
            テキストモードに切り替え
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col relative overflow-hidden">
      {/* メインエリア */}
      <div className="flex-1 flex flex-col items-center justify-center relative">
        {/* 波形ビジュアライゼーション */}
        <canvas
          ref={canvasRef}
          width={400}
          height={400}
          className="absolute w-64 h-64 md:w-80 md:h-80 lg:w-96 lg:h-96 opacity-60"
        />

        {/* ステータス表示 */}
        <div className="relative z-10 flex flex-col items-center gap-6">
          <div className="text-center space-y-2">
            {status === "processing" && (
              <Loader2 className="w-6 h-6 text-warning animate-spin mx-auto" />
            )}
            {status === "ai_speaking" && (
              <Volume2 className="w-6 h-6 text-accent animate-pulse mx-auto" />
            )}
            <p className={`text-sm font-medium ${getStatusColor()} max-w-xs`}>
              {getStatusText()}
            </p>
          </div>

          {/* マイクボタン */}
          <div className="relative">
            {status === "listening" && (
              <>
                <div
                  className="absolute inset-0 rounded-full bg-primary/20 animate-ping"
                  style={{ animationDuration: "2s", inset: "-12px" }}
                />
                <div
                  className="absolute rounded-full bg-primary/10 transition-all duration-100"
                  style={{ inset: `${-12 - audioLevel * 30}px` }}
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
              onClick={status === "ai_speaking" ? stopAISpeaking : handleMicToggle}
              disabled={status === "processing"}
              className={`relative w-24 h-24 md:w-28 md:h-28 rounded-full flex items-center justify-center transition-all duration-200 ${
                status === "listening"
                  ? "bg-primary text-white shadow-lg shadow-primary/30"
                  : status === "processing"
                    ? "bg-[var(--color-bg-card)] text-[var(--color-text-muted)] cursor-not-allowed border border-[var(--color-border)]"
                    : status === "ai_speaking"
                      ? "bg-accent/20 text-accent border border-accent/30 hover:bg-accent/30 cursor-pointer"
                      : "bg-[var(--color-bg-card)] text-[var(--color-text-primary)] border border-[var(--color-border)] hover:border-primary hover:text-primary shadow-lg"
              }`}
            >
              {status === "listening" ? (
                <Mic className="w-10 h-10" />
              ) : status === "processing" ? (
                <Loader2 className="w-10 h-10 animate-spin" />
              ) : status === "ai_speaking" ? (
                <Volume2 className="w-10 h-10" />
              ) : (
                <MicOff className="w-10 h-10" />
              )}
            </button>
          </div>

          {/* AI Speaking中のスキップヒント */}
          {status === "ai_speaking" && (
            <p className="text-[10px] text-[var(--color-text-muted)]">
              Tap to skip
            </p>
          )}

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
        <div className="absolute right-0 top-0 bottom-0 w-80 md:w-96 bg-[var(--color-bg-secondary)] border-l border-[var(--color-border)] flex flex-col z-20 animate-slide-in">
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
      <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--color-border)]">
        <div className="flex items-center gap-2">
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
        </div>

        <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-muted)]">
          <span>Messages: {messages.length}</span>
          <span>Mode: {mode}</span>
        </div>

        <button
          onClick={onEnd}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
        >
          <Phone className="w-3.5 h-3.5" />
          End
        </button>
      </div>
    </div>
  );
}
