"use client";

import { useState, useCallback } from "react";
import {
  Headphones,
  Play,
  RotateCcw,
  Send,
  CheckCircle2,
  XCircle,
  Trophy,
  Loader2,
  Volume2,
  ChevronRight,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import { api, MogomogoExercise, DictationResult } from "@/lib/api";
import { useToastStore } from "@/lib/stores/toast-store";
import { CardSkeleton } from "@/components/ui/Skeleton";

/**
 * もごもごイングリッシュページ
 * ネイティブの音声変化パターンを聞き分けるトレーニング
 */

type PageState = "setup" | "listening" | "dictation" | "result";

interface PatternType {
  id: string;
  name: string;
  nameJa: string;
  description: string;
  example: string;
}

interface ExerciseResult {
  original: string;
  userText: string;
  isCorrect: boolean;
  score: number;
  pattern: string;
  patternExplanation: string;
  ipa: string;
  missedPatterns: string[];
}

// APIから取得した問題をUI用にマッピングしたデータ型
interface MappedExercise {
  id: string;
  pattern: string;
  original: string;
  ipa: string;
  patternExplanation: string;
  missedPatterns: string[];
}

const PATTERN_TYPES: PatternType[] = [
  {
    id: "linking",
    name: "Linking",
    nameJa: "リンキング",
    description: "語と語がつながって発音される",
    example: "pick it up → pi-ki-tup",
  },
  {
    id: "reduction",
    name: "Reduction",
    nameJa: "リダクション",
    description: "音が弱くなったり消えたりする",
    example: "going to → gonna",
  },
  {
    id: "flapping",
    name: "Flapping",
    nameJa: "フラッピング",
    description: "t/dが柔らかい音に変わる",
    example: "water → wader",
  },
  {
    id: "deletion",
    name: "Deletion",
    nameJa: "脱落",
    description: "子音が省略される",
    example: "last night → las' night",
  },
  {
    id: "weak_form",
    name: "Weak Form",
    nameJa: "弱形",
    description: "機能語が弱く発音される",
    example: "can → /kən/",
  },
];

// フォールバック用のデモ問題データ（API失敗時に使用）
const FALLBACK_EXERCISES: MappedExercise[] = [
  {
    id: "1",
    pattern: "linking",
    original: "Check it out",
    ipa: "/ˈtʃɛ.kɪ.daʊt/",
    patternExplanation:
      "check の /k/ と it の /ɪ/ がリンクし、it の /t/ と out の /aʊ/ もリンクします。",
    missedPatterns: ["check+it linking", "it+out linking"],
  },
  {
    id: "2",
    pattern: "reduction",
    original: "I want to go",
    ipa: "/aɪ ˈwɑ.nə ɡoʊ/",
    patternExplanation:
      "want to が wanna に縮約されます。日常会話で非常に頻繁に使われる形です。",
    missedPatterns: ["want to → wanna reduction"],
  },
  {
    id: "3",
    pattern: "flapping",
    original: "Better water",
    ipa: "/ˈbɛ.ɾɚ ˈwɑ.ɾɚ/",
    patternExplanation:
      "母音間の /t/ がフラップ化して /ɾ/（ラ行に近い音）になります。",
    missedPatterns: ["better /t/ flapping", "water /t/ flapping"],
  },
  {
    id: "4",
    pattern: "deletion",
    original: "Most people",
    ipa: "/ˈmoʊs ˈpiː.pəl/",
    patternExplanation:
      "most の末尾 /t/ が次の子音 /p/ の前で脱落します。",
    missedPatterns: ["most /t/ deletion"],
  },
  {
    id: "5",
    pattern: "weak_form",
    original: "Can you help me",
    ipa: "/kən jə ˈhɛlp mi/",
    patternExplanation:
      "can が弱形 /kən/ に、you が /jə/ に弱化します。",
    missedPatterns: ["can weak form", "you weak form"],
  },
];

/**
 * APIレスポンスのMogomogoExerciseをUI用MappedExerciseに変換
 */
function mapApiExercise(apiExercise: MogomogoExercise): MappedExercise {
  return {
    id: apiExercise.exercise_id,
    pattern: apiExercise.pattern_type,
    original: apiExercise.audio_text,
    ipa: apiExercise.ipa_modified || apiExercise.ipa_original,
    patternExplanation: apiExercise.explanation,
    missedPatterns: [], // APIの結果でdictation check時に埋まる
  };
}

export default function MogomogoPage() {
  const [pageState, setPageState] = useState<PageState>("setup");
  const [selectedPatterns, setSelectedPatterns] = useState<string[]>([
    "linking",
  ]);
  const [exerciseCount, setExerciseCount] = useState(5);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [replaysLeft, setReplaysLeft] = useState(3);
  const [hasListened, setHasListened] = useState(false);
  const [userInput, setUserInput] = useState("");
  const [results, setResults] = useState<ExerciseResult[]>([]);
  const [showFinalResult, setShowFinalResult] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const [isCheckingAnswer, setIsCheckingAnswer] = useState(false);
  // APIまたはフォールバックから取得した問題リスト
  const [exercises, setExercises] = useState<MappedExercise[]>([]);
  const addToast = useToastStore((s) => s.addToast);

  const currentExercise = exercises[currentIndex];

  // パターン選択切り替え
  const togglePattern = useCallback((patternId: string) => {
    setSelectedPatterns((prev) => {
      if (prev.includes(patternId)) {
        if (prev.length <= 1) return prev; // 最低1つは選択
        return prev.filter((p) => p !== patternId);
      }
      return [...prev, patternId];
    });
  }, []);

  // フォールバック問題をフィルタリングして取得
  const getFallbackExercises = useCallback(
    (patterns: string[], count: number): MappedExercise[] => {
      return FALLBACK_EXERCISES.filter((e) =>
        patterns.includes(e.pattern)
      ).slice(0, count);
    },
    []
  );

  // 開始
  const handleStart = useCallback(async () => {
    setIsLoadingExercises(true);
    setCurrentIndex(0);
    setResults([]);
    setReplaysLeft(3);
    setHasListened(false);
    setUserInput("");
    setShowFinalResult(false);

    try {
      // APIからもごもご問題を取得
      const patternTypesStr = selectedPatterns.join(",");
      const apiExercises: MogomogoExercise[] = await api.getMogomogoExercises(
        patternTypesStr,
        exerciseCount
      );
      if (apiExercises.length === 0) {
        throw new Error("No exercises returned from API");
      }
      setExercises(apiExercises.map(mapApiExercise));
      setPageState("listening");
    } catch (err) {
      // API失敗時はフォールバックデータを使用
      console.error("Failed to load mogomogo exercises from API:", err);
      addToast("error", "APIからデータを取得できませんでした。デモデータを使用します。");
      const fallback = getFallbackExercises(selectedPatterns, exerciseCount);
      if (fallback.length === 0) {
        addToast("error", "選択されたパターンのデモデータがありません。");
        setIsLoadingExercises(false);
        return;
      }
      setExercises(fallback);
      setPageState("listening");
    } finally {
      setIsLoadingExercises(false);
    }
  }, [selectedPatterns, exerciseCount, addToast, getFallbackExercises]);

  // 音声再生（デモ）
  const handlePlay = useCallback(() => {
    if (replaysLeft <= 0) return;
    setIsPlaying(true);
    setReplaysLeft((prev) => prev - 1);
    // デモ：1.5秒後に再生完了とする
    setTimeout(() => {
      setIsPlaying(false);
      setHasListened(true);
    }, 1500);
  }, [replaysLeft]);

  // ディクテーションへ
  const handleProceedToDictation = useCallback(() => {
    setPageState("dictation");
  }, []);

  // 回答送信
  const handleSubmit = useCallback(async () => {
    if (!currentExercise || !userInput.trim()) return;

    setIsCheckingAnswer(true);

    try {
      // APIでディクテーション結果をチェック
      const dictResult: DictationResult = await api.checkDictation(
        currentExercise.id,
        userInput.trim(),
        currentExercise.original
      );
      const isCorrect = dictResult.accuracy >= 0.95;
      const result: ExerciseResult = {
        original: currentExercise.original,
        userText: userInput.trim(),
        isCorrect,
        score: dictResult.score,
        pattern: currentExercise.pattern,
        patternExplanation: currentExercise.patternExplanation,
        ipa: currentExercise.ipa,
        missedPatterns: isCorrect ? [] : dictResult.missed_words,
      };
      setResults((prev) => [...prev, result]);
      setPageState("result");
    } catch (err) {
      // API失敗時はローカルスコア計算でフォールバック
      console.error("Failed to check dictation via API:", err);
      addToast("error", "回答チェックに失敗しました。ローカル判定を使用します。");

      const original = currentExercise.original.toLowerCase().trim();
      const user = userInput.toLowerCase().trim();
      const isCorrect = original === user;
      const score = isCorrect
        ? 100
        : Math.max(
            0,
            Math.round(
              (1 -
                Math.abs(original.length - user.length) /
                  Math.max(original.length, 1)) *
                70
            )
          );

      const result: ExerciseResult = {
        original: currentExercise.original,
        userText: userInput.trim(),
        isCorrect,
        score,
        pattern: currentExercise.pattern,
        patternExplanation: currentExercise.patternExplanation,
        ipa: currentExercise.ipa,
        missedPatterns: isCorrect ? [] : currentExercise.missedPatterns,
      };
      setResults((prev) => [...prev, result]);
      setPageState("result");
    } finally {
      setIsCheckingAnswer(false);
    }
  }, [currentExercise, userInput, addToast]);

  // 次の問題へ
  const handleNext = useCallback(() => {
    if (currentIndex + 1 >= exercises.length) {
      setShowFinalResult(true);
    } else {
      setCurrentIndex((prev) => prev + 1);
      setReplaysLeft(3);
      setHasListened(false);
      setUserInput("");
      setPageState("listening");
    }
  }, [currentIndex, exercises.length]);

  // リスタート
  const handleRestart = useCallback(() => {
    setPageState("setup");
    setCurrentIndex(0);
    setResults([]);
    setShowFinalResult(false);
    setUserInput("");
    setExercises([]);
  }, []);

  // パターン別スコア集計
  const patternScores = PATTERN_TYPES.map((p) => {
    const patternResults = results.filter((r) => r.pattern === p.id);
    const avg =
      patternResults.length > 0
        ? Math.round(
            patternResults.reduce((s, r) => s + r.score, 0) /
              patternResults.length
          )
        : null;
    return { ...p, avgScore: avg, count: patternResults.length };
  }).filter((p) => p.count > 0);

  const overallScore =
    results.length > 0
      ? Math.round(
          results.reduce((s, r) => s + r.score, 0) / results.length
        )
      : 0;

  // セットアップ画面の問題数プレビュー（フォールバックの数を使用）
  const previewExerciseCount = getFallbackExercises(
    selectedPatterns,
    exerciseCount
  ).length;

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* セットアップ画面 */}
        {pageState === "setup" && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                もごもごイングリッシュ
              </h1>
              <p className="text-sm text-[var(--color-text-muted)]">
                ネイティブの音声変化パターンを聞き分けよう
              </p>
            </div>

            {/* パターン選択 */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Pattern Type
              </p>
              <div className="flex flex-wrap gap-2">
                {PATTERN_TYPES.map((pattern) => (
                  <button
                    key={pattern.id}
                    onClick={() => togglePattern(pattern.id)}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors border ${
                      selectedPatterns.includes(pattern.id)
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                    }`}
                  >
                    {pattern.name}
                  </button>
                ))}
              </div>

              {/* 選択されたパターンの説明 */}
              <div className="space-y-2">
                {PATTERN_TYPES.filter((p) =>
                  selectedPatterns.includes(p.id)
                ).map((pattern) => (
                  <div
                    key={pattern.id}
                    className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-3"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-[var(--color-text-primary)]">
                        {pattern.name}
                      </span>
                      <span className="text-xs text-[var(--color-text-muted)]">
                        {pattern.nameJa}
                      </span>
                    </div>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      {pattern.description}
                    </p>
                    <p className="text-xs text-accent mt-1 font-mono">
                      例: {pattern.example}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* 問題数選択 */}
            <div className="space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Exercise Count
              </p>
              <div className="flex gap-2">
                {[3, 5, 10].map((count) => (
                  <button
                    key={count}
                    onClick={() => setExerciseCount(count)}
                    className={`px-5 py-2 rounded-xl text-sm font-medium transition-colors border ${
                      exerciseCount === count
                        ? "bg-primary/10 border-primary text-primary"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-primary/30"
                    }`}
                  >
                    {count}
                  </button>
                ))}
              </div>
            </div>

            {/* 開始ボタン */}
            <button
              onClick={handleStart}
              disabled={isLoadingExercises}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
            >
              {isLoadingExercises ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Headphones className="w-4 h-4" />
              )}
              {isLoadingExercises
                ? "Loading..."
                : `Start (${exerciseCount} Questions)`}
            </button>
          </div>
        )}

        {/* リスニング画面 */}
        {pageState === "listening" && currentExercise && (
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            {/* 進捗バー */}
            <div className="w-full max-w-lg mb-6">
              <div className="flex items-center justify-between mb-2 text-xs text-[var(--color-text-muted)]">
                <span>
                  {currentIndex + 1} / {exercises.length}
                </span>
                <span className="capitalize">{currentExercise.pattern}</span>
              </div>
              <div className="w-full h-1.5 bg-[var(--color-bg-card)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-500"
                  style={{
                    width: `${((currentIndex + 1) / exercises.length) * 100}%`,
                  }}
                />
              </div>
            </div>

            <div className="w-full max-w-lg bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 space-y-6">
              {/* タイトル */}
              <div className="text-center">
                <p className="text-xs text-[var(--color-text-muted)] mb-2 uppercase tracking-wider">
                  Listen Carefully
                </p>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  音声を聞いて、何と言っているか聞き取ってください
                </p>
              </div>

              {/* 再生ボタン */}
              <div className="flex flex-col items-center gap-4">
                <button
                  onClick={handlePlay}
                  disabled={replaysLeft <= 0 || isPlaying}
                  className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                    isPlaying
                      ? "bg-primary/20 border-2 border-primary animate-pulse"
                      : replaysLeft > 0
                        ? "bg-primary/10 border-2 border-primary hover:bg-primary/20"
                        : "bg-[var(--color-bg-input)] border-2 border-[var(--color-border)] opacity-50 cursor-not-allowed"
                  }`}
                >
                  {isPlaying ? (
                    <Volume2 className="w-10 h-10 text-primary animate-pulse" />
                  ) : (
                    <Play className="w-10 h-10 text-primary ml-1" />
                  )}
                </button>
                <p className="text-xs text-[var(--color-text-muted)]">
                  Replays left: {replaysLeft}
                </p>
              </div>

              {/* IPA（リスニング後に表示） */}
              {hasListened && (
                <div className="text-center animate-fade-in">
                  <p className="text-xs text-[var(--color-text-muted)] mb-1">
                    IPA Transcription
                  </p>
                  <p className="text-lg font-mono text-accent">
                    {currentExercise.ipa}
                  </p>
                </div>
              )}

              {/* ディクテーションへ進むボタン */}
              {hasListened && (
                <button
                  onClick={handleProceedToDictation}
                  className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
                >
                  What did you hear?
                  <ChevronRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}

        {/* ディクテーション画面 */}
        {pageState === "dictation" && currentExercise && (
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            <div className="w-full max-w-lg bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 space-y-6">
              <div className="text-center">
                <p className="text-xs text-[var(--color-text-muted)] mb-2 uppercase tracking-wider">
                  Write what you heard
                </p>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  聞き取った英語をそのまま入力してください
                </p>
              </div>

              {/* IPA表示 */}
              <div className="text-center">
                <p className="text-lg font-mono text-accent">
                  {currentExercise.ipa}
                </p>
              </div>

              {/* テキスト入力 */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  placeholder="Type what you heard..."
                  className="flex-1 px-4 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                  autoFocus
                  disabled={isCheckingAnswer}
                />
                <button
                  onClick={handleSubmit}
                  disabled={!userInput.trim() || isCheckingAnswer}
                  className="px-4 py-3 rounded-xl bg-primary text-white hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {isCheckingAnswer ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 個別結果画面 */}
        {pageState === "result" && !showFinalResult && (
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            <div className="w-full max-w-lg bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 space-y-5 animate-fade-in">
              {/* 正誤表示 */}
              {results[results.length - 1] && (
                <>
                  <div
                    className={`flex items-center gap-3 p-4 rounded-xl ${
                      results[results.length - 1].isCorrect
                        ? "bg-green-500/10 border border-green-500/20"
                        : "bg-red-500/10 border border-red-500/20"
                    }`}
                  >
                    {results[results.length - 1].isCorrect ? (
                      <CheckCircle2 className="w-6 h-6 text-green-400 shrink-0" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-400 shrink-0" />
                    )}
                    <div>
                      <p
                        className={`text-sm font-semibold ${
                          results[results.length - 1].isCorrect
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        {results[results.length - 1].isCorrect
                          ? "Correct!"
                          : "Not quite..."}
                      </p>
                      <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                        Score: {results[results.length - 1].score}%
                      </p>
                    </div>
                  </div>

                  {/* テキスト比較 */}
                  <div className="space-y-2">
                    <div className="flex items-start gap-2 text-sm">
                      <span className="text-[var(--color-text-muted)] shrink-0 w-20">
                        Original:
                      </span>
                      <span className="text-green-400 font-medium">
                        {results[results.length - 1].original}
                      </span>
                    </div>
                    <div className="flex items-start gap-2 text-sm">
                      <span className="text-[var(--color-text-muted)] shrink-0 w-20">
                        You heard:
                      </span>
                      <span
                        className={
                          results[results.length - 1].isCorrect
                            ? "text-green-400"
                            : "text-red-400"
                        }
                      >
                        {results[results.length - 1].userText}
                      </span>
                    </div>
                  </div>

                  {/* IPA */}
                  <div className="text-center p-3 rounded-lg bg-[var(--color-bg-primary)]/50">
                    <p className="text-xs text-[var(--color-text-muted)] mb-1">
                      IPA
                    </p>
                    <p className="text-lg font-mono text-accent">
                      {results[results.length - 1].ipa}
                    </p>
                  </div>

                  {/* パターン解説 */}
                  <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
                    <p className="text-xs font-semibold text-primary mb-1">
                      Pattern:{" "}
                      {
                        PATTERN_TYPES.find(
                          (p) => p.id === results[results.length - 1].pattern
                        )?.name
                      }
                    </p>
                    <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                      {results[results.length - 1].patternExplanation}
                    </p>
                  </div>

                  {/* 見逃したパターン */}
                  {results[results.length - 1].missedPatterns.length > 0 && (
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-warning">
                        Missed Patterns:
                      </p>
                      {results[results.length - 1].missedPatterns.map(
                        (mp, i) => (
                          <div
                            key={i}
                            className="flex items-center gap-2 text-xs text-[var(--color-text-secondary)]"
                          >
                            <div className="w-1.5 h-1.5 rounded-full bg-warning" />
                            {mp}
                          </div>
                        )
                      )}
                    </div>
                  )}

                  {/* 次へボタン */}
                  <button
                    onClick={handleNext}
                    className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors"
                  >
                    {currentIndex + 1 < exercises.length
                      ? "Next Question"
                      : "See Results"}
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {/* 最終結果画面 */}
        {showFinalResult && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md space-y-6 text-center">
              <div className="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center mx-auto">
                <Trophy className="w-8 h-8 text-warning" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Results
                </h1>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  {exercises.length} exercises completed
                </p>
              </div>

              {/* 全体スコア */}
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 space-y-4">
                <div className="text-center">
                  <p className="text-5xl font-heading font-bold text-primary">
                    {overallScore}
                    <span className="text-lg text-[var(--color-text-muted)]">
                      %
                    </span>
                  </p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">
                    Overall Score
                  </p>
                </div>

                <div className="w-full h-3 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      overallScore >= 80
                        ? "bg-green-400"
                        : overallScore >= 50
                          ? "bg-warning"
                          : "bg-red-400"
                    }`}
                    style={{ width: `${overallScore}%` }}
                  />
                </div>
              </div>

              {/* パターン別スコア */}
              {patternScores.length > 0 && (
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
                  <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                    Accuracy by Pattern
                  </p>
                  {patternScores.map((ps) => (
                    <div key={ps.id} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-[var(--color-text-primary)]">
                          {ps.name}
                        </span>
                        <span
                          className={`font-semibold ${
                            (ps.avgScore ?? 0) >= 80
                              ? "text-green-400"
                              : (ps.avgScore ?? 0) >= 50
                                ? "text-warning"
                                : "text-red-400"
                          }`}
                        >
                          {ps.avgScore}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            (ps.avgScore ?? 0) >= 80
                              ? "bg-green-400"
                              : (ps.avgScore ?? 0) >= 50
                                ? "bg-warning"
                                : "bg-red-400"
                          }`}
                          style={{ width: `${ps.avgScore}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 各問の結果一覧 */}
              <div className="space-y-2 text-left">
                {results.map((result, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-3 p-3 rounded-xl text-xs ${
                      result.isCorrect
                        ? "bg-green-500/5 border border-green-500/10"
                        : "bg-red-500/5 border border-red-500/10"
                    }`}
                  >
                    <span
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        result.isCorrect
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[var(--color-text-secondary)] truncate">
                        {result.original}
                      </p>
                      <p
                        className={`truncate mt-0.5 ${
                          result.isCorrect ? "text-green-400" : "text-red-400"
                        }`}
                      >
                        {result.userText}
                      </p>
                    </div>
                    <span className="text-[var(--color-text-muted)] capitalize text-[10px]">
                      {result.pattern}
                    </span>
                  </div>
                ))}
              </div>

              {/* リスタートボタン */}
              <button
                onClick={handleRestart}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
