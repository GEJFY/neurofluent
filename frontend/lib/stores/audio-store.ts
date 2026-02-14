"use client";

import { create } from "zustand";

/**
 * オーディオストア
 * 録音・再生状態の管理
 * MediaRecorder APIを内部使用
 */

interface AudioState {
  /** 録音中かどうか */
  isRecording: boolean;
  /** 再生中かどうか */
  isPlaying: boolean;
  /** 録音された音声Blob */
  audioBlob: Blob | null;
  /** 録音された音声のURL（再生用） */
  audioUrl: string | null;
  /** 録音時間（秒） */
  recordingDuration: number;
  /** エラーメッセージ */
  error: string | null;

  // === 内部参照（storeの外で管理） ===
  _mediaRecorder: MediaRecorder | null;
  _audioElement: HTMLAudioElement | null;
  _stream: MediaStream | null;
  _timer: ReturnType<typeof setInterval> | null;
  _chunks: Blob[];

  // === アクション ===
  /** 録音開始 */
  startRecording: () => Promise<void>;
  /** 録音停止 */
  stopRecording: () => void;
  /** 音声再生 */
  playAudio: () => void;
  /** 音声一時停止 */
  pauseAudio: () => void;
  /** 状態リセット */
  resetAudio: () => void;
}

export const useAudioStore = create<AudioState>((set, get) => ({
  isRecording: false,
  isPlaying: false,
  audioBlob: null,
  audioUrl: null,
  recordingDuration: 0,
  error: null,

  _mediaRecorder: null,
  _audioElement: null,
  _stream: null,
  _timer: null,
  _chunks: [],

  startRecording: async () => {
    const state = get();

    // 既に録音中の場合は何もしない
    if (state.isRecording) return;

    // 前回の録音データをクリア
    if (state.audioUrl) {
      URL.revokeObjectURL(state.audioUrl);
    }

    set({
      audioBlob: null,
      audioUrl: null,
      recordingDuration: 0,
      error: null,
      _chunks: [],
    });

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? "audio/webm;codecs=opus"
          : "audio/webm",
      });

      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        // ストリーム停止
        stream.getTracks().forEach((track) => track.stop());

        // Blobを作成
        const blob = new Blob(chunks, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);

        // タイマー停止
        const currentTimer = get()._timer;
        if (currentTimer) {
          clearInterval(currentTimer);
        }

        set({
          isRecording: false,
          audioBlob: blob,
          audioUrl: url,
          _mediaRecorder: null,
          _stream: null,
          _timer: null,
          _chunks: [],
        });
      };

      // 録音開始
      mediaRecorder.start(100);

      // タイマー開始
      const timer = setInterval(() => {
        set((state) => ({
          recordingDuration: state.recordingDuration + 1,
        }));
      }, 1000);

      set({
        isRecording: true,
        _mediaRecorder: mediaRecorder,
        _stream: stream,
        _timer: timer,
        _chunks: chunks,
      });
    } catch (err) {
      console.error("Failed to start recording:", err);
      set({
        error: "マイクへのアクセスが拒否されました。ブラウザの設定を確認してください。",
        isRecording: false,
      });
    }
  },

  stopRecording: () => {
    const { _mediaRecorder, _timer, isRecording } = get();

    if (!isRecording) return;

    if (_timer) {
      clearInterval(_timer);
    }

    if (_mediaRecorder && _mediaRecorder.state === "recording") {
      _mediaRecorder.stop();
    }
  },

  playAudio: () => {
    const { audioUrl, isPlaying } = get();

    if (!audioUrl || isPlaying) return;

    const audio = new Audio(audioUrl);

    audio.addEventListener("ended", () => {
      set({ isPlaying: false, _audioElement: null });
    });

    audio.addEventListener("error", () => {
      set({
        isPlaying: false,
        error: "音声の再生に失敗しました",
        _audioElement: null,
      });
    });

    audio.play().then(() => {
      set({ isPlaying: true, _audioElement: audio });
    }).catch((err) => {
      console.error("Playback failed:", err);
      set({ error: "音声の再生に失敗しました" });
    });
  },

  pauseAudio: () => {
    const { _audioElement, isPlaying } = get();

    if (!isPlaying || !_audioElement) return;

    _audioElement.pause();
    set({ isPlaying: false });
  },

  resetAudio: () => {
    const { _mediaRecorder, _audioElement, _stream, _timer, audioUrl } = get();

    // 録音停止
    if (_timer) clearInterval(_timer);
    if (_mediaRecorder && _mediaRecorder.state === "recording") {
      _mediaRecorder.stop();
    }
    if (_stream) {
      _stream.getTracks().forEach((track) => track.stop());
    }

    // 再生停止
    if (_audioElement) {
      _audioElement.pause();
      _audioElement.removeAttribute("src");
    }

    // URL解放
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }

    set({
      isRecording: false,
      isPlaying: false,
      audioBlob: null,
      audioUrl: null,
      recordingDuration: 0,
      error: null,
      _mediaRecorder: null,
      _audioElement: null,
      _stream: null,
      _timer: null,
      _chunks: [],
    });
  },
}));
