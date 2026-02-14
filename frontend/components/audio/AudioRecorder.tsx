"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Mic, Square, Loader2 } from "lucide-react";

/**
 * AudioRecorder - 音声録音コンポーネント
 * MediaRecorder APIを使用した録音機能
 * - idle: 録音待機
 * - recording: 録音中（パルスアニメーション + タイマー）
 * - processing: 録音データ処理中
 */

interface AudioRecorderProps {
  /** 録音完了時のコールバック */
  onRecordingComplete: (audioBlob: Blob) => void;
  /** 最大録音時間（秒）。デフォルト120秒 */
  maxDuration?: number;
}

type RecordingState = "idle" | "recording" | "processing";

export default function AudioRecorder({
  onRecordingComplete,
  maxDuration = 120,
}: AudioRecorderProps) {
  const [state, setState] = useState<RecordingState>("idle");
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // 最大時間に達したら自動停止
  useEffect(() => {
    if (state === "recording" && duration >= maxDuration) {
      handleStop();
    }
  }, [duration, maxDuration, state]);

  // 音声レベルメーター更新
  const updateAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // 平均音量を計算（0-1の範囲）
    const average = dataArray.reduce((sum, val) => sum + val, 0) / dataArray.length;
    setAudioLevel(average / 255);

    if (state === "recording") {
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [state]);

  // 録音開始
  const handleStart = useCallback(async () => {
    setError(null);
    setDuration(0);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });
      streamRef.current = stream;

      // Web Audio APIでレベルメーター用のanalyserを接続
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      // MediaRecorder設定
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

      mediaRecorder.onstop = () => {
        setState("processing");

        // ストリームを停止
        stream.getTracks().forEach((track) => track.stop());

        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];

        // コールバック実行
        onRecordingComplete(blob);
        setState("idle");
        setAudioLevel(0);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100); // 100msごとにデータ取得
      setState("recording");

      // タイマー開始
      timerRef.current = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);

      // レベルメーター開始
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    } catch (err) {
      console.error("Microphone access failed:", err);
      setError("マイクへのアクセスが拒否されました。ブラウザの設定を確認してください。");
    }
  }, [onRecordingComplete, updateAudioLevel]);

  // 録音停止
  const handleStop = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // 時間フォーマット
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {/* エラー表示 */}
      {error && (
        <div className="w-full p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400 text-center">
          {error}
        </div>
      )}

      {/* 録音ボタン */}
      <div className="relative">
        {/* 録音中のパルスリング */}
        {state === "recording" && (
          <>
            <div
              className="absolute inset-0 rounded-full bg-red-500/20 animate-ping"
              style={{ animationDuration: "1.5s" }}
            />
            <div
              className="absolute rounded-full bg-red-500/10 transition-all duration-100"
              style={{
                inset: `${-8 - audioLevel * 20}px`,
              }}
            />
          </>
        )}

        <button
          onClick={state === "idle" ? handleStart : state === "recording" ? handleStop : undefined}
          disabled={state === "processing"}
          className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 ${
            state === "idle"
              ? "bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/25"
              : state === "recording"
                ? "bg-red-600 text-white shadow-lg shadow-red-600/30"
                : "bg-[var(--color-bg-card)] text-[var(--color-text-muted)] cursor-not-allowed"
          }`}
        >
          {state === "idle" && <Mic className="w-8 h-8" />}
          {state === "recording" && <Square className="w-7 h-7" />}
          {state === "processing" && <Loader2 className="w-7 h-7 animate-spin" />}
        </button>
      </div>

      {/* タイマー表示 */}
      <div className="text-center space-y-1">
        {state === "recording" && (
          <>
            <p className="text-lg font-heading font-bold text-red-400 tabular-nums">
              {formatTime(duration)}
            </p>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              <span className="text-xs text-red-400 font-medium">Recording</span>
            </div>
          </>
        )}
        {state === "idle" && (
          <p className="text-xs text-[var(--color-text-muted)]">
            Tap to start recording
          </p>
        )}
        {state === "processing" && (
          <p className="text-xs text-[var(--color-text-muted)]">
            Processing...
          </p>
        )}
      </div>

      {/* レベルメーター */}
      {state === "recording" && (
        <div className="flex items-center gap-0.5 h-8">
          {Array.from({ length: 20 }).map((_, i) => {
            const barLevel = (i + 1) / 20;
            const isActive = audioLevel >= barLevel * 0.8;
            return (
              <div
                key={i}
                className={`w-1.5 rounded-full transition-all duration-75 ${
                  isActive
                    ? barLevel > 0.7
                      ? "bg-red-400"
                      : barLevel > 0.4
                        ? "bg-warning"
                        : "bg-green-400"
                    : "bg-[var(--color-border)]"
                }`}
                style={{
                  height: `${Math.max(4, (isActive ? audioLevel : 0.1) * 32)}px`,
                }}
              />
            );
          })}
        </div>
      )}

      {/* 最大時間インジケーター */}
      {state === "recording" && (
        <div className="w-full max-w-[200px]">
          <div className="w-full h-1 bg-[var(--color-border)] rounded-full overflow-hidden">
            <div
              className="h-full bg-red-500 rounded-full transition-all duration-1000"
              style={{ width: `${(duration / maxDuration) * 100}%` }}
            />
          </div>
          <p className="text-[10px] text-[var(--color-text-muted)] mt-1 text-center">
            Max {Math.floor(maxDuration / 60)}:{(maxDuration % 60).toString().padStart(2, "0")}
          </p>
        </div>
      )}
    </div>
  );
}
