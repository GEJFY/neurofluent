"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  Play,
  Pause,
  Mic,
  MicOff,
  Eye,
  EyeOff,
  RotateCcw,
  ArrowRight,
  Loader2,
  ChevronLeft,
  Volume2,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import AudioPlayer from "@/components/audio/AudioPlayer";
import AudioRecorder from "@/components/audio/AudioRecorder";
import PronunciationScore from "@/components/audio/PronunciationScore";
import { api } from "@/lib/api";

/**
 * シャドーイングページ
 * States: setup → listening → shadowing → result
 */

type ShadowingState = "setup" | "listening" | "shadowing" | "result";

interface TopicOption {
  id: string;
  label: string;
  labelJa: string;
  description: string;
}

interface DifficultyOption {
  id: string;
  label: string;
  color: string;
}

// シャドーイング用の練習テキスト型
interface ShadowingExercise {
  id: string;
  topic: string;
  difficulty: string;
  text: string;
  audioUrl: string;
  duration: number;
}

// 発音評価結果型
interface PronunciationResult {
  accuracy: number;
  fluency: number;
  prosody: number;
  completeness: number;
  wordScores: {
    word: string;
    accuracy: number;
    error?: string;
  }[];
}

const TOPICS: TopicOption[] = [
  {
    id: "business_meeting",
    label: "Business Meeting",
    labelJa: "ビジネスミーティング",
    description: "Standard meeting discussions and agenda items",
  },
  {
    id: "earnings_call",
    label: "Earnings Call",
    labelJa: "決算説明会",
    description: "Financial reporting and investor communications",
  },
  {
    id: "team_discussion",
    label: "Team Discussion",
    labelJa: "チームディスカッション",
    description: "Collaborative team planning and brainstorming",
  },
  {
    id: "client_presentation",
    label: "Client Presentation",
    labelJa: "クライアントプレゼン",
    description: "Client-facing presentations and pitches",
  },
  {
    id: "casual_networking",
    label: "Casual Networking",
    labelJa: "カジュアルな交流",
    description: "Informal professional conversations",
  },
];

const DIFFICULTIES: DifficultyOption[] = [
  { id: "beginner", label: "Beginner", color: "text-green-400 bg-green-500/15" },
  { id: "intermediate", label: "Intermediate", color: "text-warning bg-warning/15" },
  { id: "advanced", label: "Advanced", color: "text-red-400 bg-red-500/15" },
];

// デモ用のサンプルデータ（実際にはAPIから取得）
const SAMPLE_EXERCISES: Record<string, ShadowingExercise> = {
  business_meeting: {
    id: "shadow-1",
    topic: "business_meeting",
    difficulty: "intermediate",
    text: "I'd like to start by reviewing our quarterly targets. As you can see from the slides, we've exceeded expectations in the APAC region, but we still have some ground to cover in the European market. Let's discuss our strategy for the remaining quarter.",
    audioUrl: "",
    duration: 15,
  },
  earnings_call: {
    id: "shadow-2",
    topic: "earnings_call",
    difficulty: "advanced",
    text: "Revenue for the third quarter came in at 4.2 billion dollars, representing a 12% year-over-year increase. Our operating margin expanded by 200 basis points, driven primarily by efficiency gains in our cloud infrastructure division.",
    audioUrl: "",
    duration: 12,
  },
  team_discussion: {
    id: "shadow-3",
    topic: "team_discussion",
    difficulty: "beginner",
    text: "Hey everyone, thanks for joining. I wanted to quickly go over the timeline for the new feature release. We're looking at a two-week sprint starting Monday. Does that work for everyone?",
    audioUrl: "",
    duration: 10,
  },
  client_presentation: {
    id: "shadow-4",
    topic: "client_presentation",
    difficulty: "intermediate",
    text: "Thank you for taking the time to meet with us today. We've prepared a comprehensive proposal that addresses your core requirements. Our solution offers scalability, security, and seamless integration with your existing systems.",
    audioUrl: "",
    duration: 13,
  },
  casual_networking: {
    id: "shadow-5",
    topic: "casual_networking",
    difficulty: "beginner",
    text: "Nice to meet you! I heard you're working on some exciting projects in the AI space. We're actually exploring something similar at our company. Would love to grab coffee sometime and exchange ideas.",
    audioUrl: "",
    duration: 10,
  },
};

export default function ShadowingPage() {
  const [state, setState] = useState<ShadowingState>("setup");
  const [selectedTopic, setSelectedTopic] = useState("business_meeting");
  const [selectedDifficulty, setSelectedDifficulty] = useState("intermediate");
  const [exercise, setExercise] = useState<ShadowingExercise | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showText, setShowText] = useState(true);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [result, setResult] = useState<PronunciationResult | null>(null);

  // セットアップ → リスニング開始
  const handleStart = useCallback(async () => {
    setIsLoading(true);
    try {
      // デモ用：ローカルサンプルデータを使用
      // 実際にはAPIからデータを取得: await api.getShadowingExercise(selectedTopic, selectedDifficulty)
      const sample = SAMPLE_EXERCISES[selectedTopic] || SAMPLE_EXERCISES.business_meeting;
      setExercise({
        ...sample,
        difficulty: selectedDifficulty,
      });
      setState("listening");
    } catch (err) {
      console.error("Failed to load exercise:", err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedTopic, selectedDifficulty]);

  // リスニング完了 → シャドーイングへ
  const handleListeningComplete = useCallback(() => {
    setShowText(false);
    setState("shadowing");
  }, []);

  // 録音完了 → 結果へ
  const handleRecordingComplete = useCallback(async (blob: Blob) => {
    setRecordedBlob(blob);
    setIsLoading(true);
    try {
      // デモ用：モック結果を生成
      // 実際にはAPIで音声解析: await api.analyzePronunciation(blob, exercise.id)
      const mockResult: PronunciationResult = {
        accuracy: 78 + Math.random() * 15,
        fluency: 72 + Math.random() * 18,
        prosody: 68 + Math.random() * 20,
        completeness: 80 + Math.random() * 15,
        wordScores: (exercise?.text.split(" ") || []).map((word) => ({
          word,
          accuracy: 60 + Math.random() * 40,
          error: Math.random() > 0.8 ? "pronunciation" : undefined,
        })),
      };
      setResult(mockResult);
      setState("result");
    } catch (err) {
      console.error("Failed to analyze pronunciation:", err);
    } finally {
      setIsLoading(false);
    }
  }, [exercise]);

  // リトライ
  const handleRetry = useCallback(() => {
    setRecordedBlob(null);
    setResult(null);
    setShowText(true);
    setState("listening");
  }, []);

  // 次の問題
  const handleNext = useCallback(() => {
    setRecordedBlob(null);
    setResult(null);
    setExercise(null);
    setShowText(true);
    setState("setup");
  }, []);

  // セットアップに戻る
  const handleBack = useCallback(() => {
    setState("setup");
    setExercise(null);
    setRecordedBlob(null);
    setResult(null);
    setShowText(true);
  }, []);

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* ===== セットアップ画面 ===== */}
        {state === "setup" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-lg space-y-6">
              {/* ヘッダー */}
              <div className="text-center space-y-1">
                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
                  <Volume2 className="w-7 h-7 text-primary" />
                </div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Speed Shadowing
                </h1>
                <p className="text-sm text-[var(--color-text-muted)]">
                  音声を聞いてすぐに真似る。発音・リズム・イントネーションを同時に鍛えましょう。
                </p>
              </div>

              {/* トピック選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Topic
                </p>
                <div className="grid gap-2">
                  {TOPICS.map((topic) => (
                    <button
                      key={topic.id}
                      onClick={() => setSelectedTopic(topic.id)}
                      className={`flex items-start gap-3 p-3 rounded-xl border text-left transition-colors ${
                        selectedTopic === topic.id
                          ? "border-primary bg-primary/5"
                          : "border-[var(--color-border)] hover:border-primary/30"
                      }`}
                    >
                      <div
                        className={`w-4 h-4 mt-0.5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                          selectedTopic === topic.id
                            ? "border-primary"
                            : "border-[var(--color-text-muted)]"
                        }`}
                      >
                        {selectedTopic === topic.id && (
                          <div className="w-2 h-2 rounded-full bg-primary" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--color-text-primary)]">
                          {topic.label}
                        </p>
                        <p className="text-[11px] text-[var(--color-text-muted)]">
                          {topic.labelJa} - {topic.description}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 難易度選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Difficulty
                </p>
                <div className="flex gap-2">
                  {DIFFICULTIES.map((diff) => (
                    <button
                      key={diff.id}
                      onClick={() => setSelectedDifficulty(diff.id)}
                      className={`flex-1 py-2.5 rounded-xl text-xs font-semibold text-center transition-colors border ${
                        selectedDifficulty === diff.id
                          ? `${diff.color} border-current`
                          : "text-[var(--color-text-muted)] border-[var(--color-border)] hover:border-primary/30"
                      }`}
                    >
                      {diff.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 開始ボタン */}
              <button
                onClick={handleStart}
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Start Shadowing
              </button>
            </div>
          </div>
        )}

        {/* ===== リスニング画面 ===== */}
        {state === "listening" && exercise && (
          <div className="flex-1 flex flex-col">
            {/* 上部ナビ */}
            <div className="flex items-center justify-between pb-4 border-b border-[var(--color-border)]">
              <button
                onClick={handleBack}
                className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </button>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/15 text-primary">
                  Listening
                </span>
                <span className="text-xs text-[var(--color-text-muted)]">
                  Step 1 of 2
                </span>
              </div>
            </div>

            {/* メインコンテンツ */}
            <div className="flex-1 flex flex-col items-center justify-center py-8 space-y-8">
              {/* テキスト表示 */}
              <div className="w-full max-w-2xl">
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                      Listen & Read
                    </p>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {TOPICS.find((t) => t.id === exercise.topic)?.label}
                    </span>
                  </div>
                  <p className="text-base md:text-lg text-[var(--color-text-primary)] leading-relaxed font-body">
                    {exercise.text}
                  </p>
                </div>
              </div>

              {/* オーディオプレーヤー */}
              <div className="w-full max-w-md">
                <AudioPlayer
                  src={exercise.audioUrl}
                  speeds={[0.7, 0.8, 0.9, 1.0, 1.1, 1.2]}
                  showSpeedControls
                  onEnded={() => {}}
                />
              </div>

              {/* シャドーイングに進むボタン */}
              <button
                onClick={handleListeningComplete}
                className="px-6 py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center gap-2"
              >
                Ready to Shadow
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* ===== シャドーイング画面 ===== */}
        {state === "shadowing" && exercise && (
          <div className="flex-1 flex flex-col">
            {/* 上部ナビ */}
            <div className="flex items-center justify-between pb-4 border-b border-[var(--color-border)]">
              <button
                onClick={() => setState("listening")}
                className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
              >
                <ChevronLeft className="w-4 h-4" />
                Back to Listening
              </button>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-accent/15 text-accent">
                  Shadowing
                </span>
                <span className="text-xs text-[var(--color-text-muted)]">
                  Step 2 of 2
                </span>
              </div>
            </div>

            {/* メインコンテンツ */}
            <div className="flex-1 flex flex-col items-center justify-center py-8 space-y-6">
              {/* テキスト表示トグル */}
              <div className="w-full max-w-2xl">
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                      Shadow the Audio
                    </p>
                    <button
                      onClick={() => setShowText(!showText)}
                      className="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
                    >
                      {showText ? (
                        <>
                          <EyeOff className="w-3.5 h-3.5" />
                          Hide Text
                        </>
                      ) : (
                        <>
                          <Eye className="w-3.5 h-3.5" />
                          Show Text
                        </>
                      )}
                    </button>
                  </div>

                  {showText ? (
                    <p className="text-base md:text-lg text-[var(--color-text-primary)] leading-relaxed font-body">
                      {exercise.text}
                    </p>
                  ) : (
                    <div className="py-8 text-center">
                      <p className="text-sm text-[var(--color-text-muted)]">
                        テキストは非表示になっています。音声を聞いて真似しましょう。
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* オーディオプレーヤー（シャドーイング中も使用可能） */}
              <div className="w-full max-w-md">
                <AudioPlayer
                  src={exercise.audioUrl}
                  speeds={[0.7, 0.8, 0.9, 1.0, 1.1, 1.2]}
                  showSpeedControls
                />
              </div>

              {/* 録音コンポーネント */}
              <div className="w-full max-w-md">
                <AudioRecorder
                  onRecordingComplete={handleRecordingComplete}
                  maxDuration={60}
                />
              </div>

              {/* ローディング表示 */}
              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  発音を分析中...
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===== 結果画面 ===== */}
        {state === "result" && result && exercise && (
          <div className="flex-1 flex flex-col items-center py-6 space-y-6">
            {/* ヘッダー */}
            <div className="text-center space-y-1">
              <h2 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                Shadowing Results
              </h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                {TOPICS.find((t) => t.id === exercise.topic)?.label} -{" "}
                {selectedDifficulty}
              </p>
            </div>

            {/* 発音スコア表示 */}
            <div className="w-full max-w-2xl">
              <PronunciationScore
                scores={{
                  accuracy: result.accuracy,
                  fluency: result.fluency,
                  prosody: result.prosody,
                  completeness: result.completeness,
                }}
                wordScores={result.wordScores}
              />
            </div>

            {/* 原文テキスト */}
            <div className="w-full max-w-2xl">
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-3">
                  Original Text
                </p>
                <p className="text-sm text-[var(--color-text-primary)] leading-relaxed">
                  {exercise.text}
                </p>
              </div>
            </div>

            {/* アクションボタン */}
            <div className="flex gap-3 w-full max-w-md">
              <button
                onClick={handleRetry}
                className="flex-1 py-3 rounded-xl border border-[var(--color-border)] text-sm font-semibold text-[var(--color-text-primary)] hover:bg-[var(--color-bg-card)] transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Retry
              </button>
              <button
                onClick={handleNext}
                className="flex-1 py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
              >
                Next Topic
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
