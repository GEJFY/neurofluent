"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Play, Pause, RotateCcw } from "lucide-react";

/**
 * AudioPlayer - 音声再生コンポーネント
 * HTMLAudioElementを使用した再生＋速度コントロール
 * - play/pause, progress bar, time display
 * - speed selector chips (0.7x-1.2x)
 * - waveform visualization (canvas)
 */

interface AudioPlayerProps {
  /** 音声ソース（URLまたはBlob） */
  src: string | Blob;
  /** 再生速度オプション */
  speeds?: number[];
  /** 再生終了時のコールバック */
  onEnded?: () => void;
  /** 速度コントロールの表示 */
  showSpeedControls?: boolean;
}

export default function AudioPlayer({
  src,
  speeds = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
  onEnded,
  showSpeedControls = false,
}: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [isLoaded, setIsLoaded] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceNodeRef = useRef<MediaElementAudioSourceNode | null>(null);

  // 音声ソースのURL生成
  const audioUrl = typeof src === "string" ? src : src instanceof Blob ? URL.createObjectURL(src) : "";

  // Blob URLのクリーンアップ
  useEffect(() => {
    return () => {
      if (src instanceof Blob && audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [src, audioUrl]);

  // Audio要素の初期化
  useEffect(() => {
    const audio = new Audio();
    audio.crossOrigin = "anonymous";
    audioRef.current = audio;

    audio.addEventListener("loadedmetadata", () => {
      setDuration(audio.duration);
      setIsLoaded(true);
    });

    audio.addEventListener("timeupdate", () => {
      setCurrentTime(audio.currentTime);
    });

    audio.addEventListener("ended", () => {
      setIsPlaying(false);
      setCurrentTime(0);
      onEnded?.();
    });

    audio.addEventListener("error", () => {
      // デモモードの場合はダミー表示
      setIsLoaded(true);
      setDuration(30);
    });

    if (audioUrl) {
      audio.src = audioUrl;
      audio.load();
    }

    return () => {
      audio.pause();
      audio.removeAttribute("src");
      audio.load();
    };
  }, [audioUrl, onEnded]);

  // Waveform描画
  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 波形描画
    ctx.lineWidth = 2;
    ctx.strokeStyle = isPlaying ? "#6366F1" : "#475569";
    ctx.beginPath();

    const sliceWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }

    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    if (isPlaying) {
      animationRef.current = requestAnimationFrame(drawWaveform);
    }
  }, [isPlaying]);

  // Web Audio APIでの解析セットアップ
  const setupAnalyser = useCallback(() => {
    const audio = audioRef.current;
    if (!audio || audioContextRef.current) return;

    try {
      const audioContext = new AudioContext();
      const source = audioContext.createMediaElementSource(audio);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;

      source.connect(analyser);
      analyser.connect(audioContext.destination);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      sourceNodeRef.current = source;
    } catch {
      // Web Audio API接続に失敗（CORS等）
    }
  }, []);

  // 再生 / 一時停止
  const togglePlay = useCallback(async () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    } else {
      try {
        setupAnalyser();
        audio.playbackRate = playbackRate;
        await audio.play();
        setIsPlaying(true);
        drawWaveform();
      } catch {
        // デモモード：再生できない場合はシミュレーション
        setIsPlaying(true);
        // タイマーで時間を進めるシミュレーション
        const interval = setInterval(() => {
          setCurrentTime((prev) => {
            const next = prev + 0.1 * playbackRate;
            if (next >= duration) {
              clearInterval(interval);
              setIsPlaying(false);
              setCurrentTime(0);
              onEnded?.();
              return 0;
            }
            return next;
          });
        }, 100);
      }
    }
  }, [isPlaying, playbackRate, duration, onEnded, setupAnalyser, drawWaveform]);

  // 速度変更
  const changeSpeed = useCallback(
    (speed: number) => {
      setPlaybackRate(speed);
      if (audioRef.current) {
        audioRef.current.playbackRate = speed;
      }
    },
    []
  );

  // プログレスバーのクリックでシーク
  const handleProgressClick = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      const rect = e.currentTarget.getBoundingClientRect();
      const ratio = (e.clientX - rect.left) / rect.width;
      const newTime = ratio * duration;

      if (audioRef.current) {
        audioRef.current.currentTime = newTime;
      }
      setCurrentTime(newTime);
    },
    [duration]
  );

  // リセット
  const handleReset = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.pause();
    }
    setCurrentTime(0);
    setIsPlaying(false);
  }, []);

  // 時間フォーマット
  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-4 space-y-3">
      {/* Waveform Canvas */}
      <canvas
        ref={canvasRef}
        width={400}
        height={40}
        className="w-full h-10 rounded-lg bg-[var(--color-bg-primary)]"
      />

      {/* コントロール行 */}
      <div className="flex items-center gap-3">
        {/* 再生 / 一時停止ボタン */}
        <button
          onClick={togglePlay}
          disabled={!isLoaded}
          className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white hover:bg-primary-500 disabled:opacity-40 transition-colors shrink-0"
        >
          {isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4 ml-0.5" />
          )}
        </button>

        {/* プログレスバー + 時間 */}
        <div className="flex-1 space-y-1">
          <div
            ref={progressRef}
            onClick={handleProgressClick}
            className="relative w-full h-2 bg-[var(--color-bg-primary)] rounded-full cursor-pointer group"
          >
            <div
              className="absolute left-0 top-0 h-full bg-primary rounded-full transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
            {/* ドラッグハンドル */}
            <div
              className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full bg-primary shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ left: `calc(${progress}% - 7px)` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-[var(--color-text-muted)] tabular-nums">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* リセットボタン */}
        <button
          onClick={handleReset}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-primary)] transition-colors shrink-0"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 速度コントロール */}
      {showSpeedControls && (
        <div className="flex items-center gap-1.5 pt-1">
          <span className="text-[10px] text-[var(--color-text-muted)] mr-1">Speed:</span>
          {speeds.map((speed) => (
            <button
              key={speed}
              onClick={() => changeSpeed(speed)}
              className={`px-2 py-1 rounded-lg text-[11px] font-semibold transition-colors ${
                playbackRate === speed
                  ? "bg-primary text-white"
                  : "bg-[var(--color-bg-primary)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
