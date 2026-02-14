"use client";

import { useState, useCallback } from "react";
import { Loader2, Trophy, RotateCcw } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import FlashCard from "@/components/drill/FlashCard";
import { api, type FlashExercise, type FlashCheckResponse } from "@/lib/api";

/**
 * Flash Translation（瞬間英作文）ページ
 * - 問題表示 → カウントダウン → 入力 → 結果
 * - スコアトラッカー
 * - 全問終了後のリザルト画面
 */

type PageState = "setup" | "playing" | "finished";

export default function FlashPage() {
  const [pageState, setPageState] = useState<PageState>("setup");
  const [exercises, setExercises] = useState<FlashExercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<FlashCheckResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 問題を取得して開始
  const handleStart = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getFlashExercises(10);
      if (data.length === 0) {
        setError("問題が見つかりませんでした。");
        return;
      }
      setExercises(data);
      setCurrentIndex(0);
      setResults([]);
      setPageState("playing");
    } catch (err) {
      console.error("Flash exercises fetch failed:", err);
      setError("問題の読み込みに失敗しました");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 回答送信
  const handleSubmit = useCallback(
    async (answer: string): Promise<FlashCheckResponse> => {
      const exercise = exercises[currentIndex];
      const result = await api.checkFlashAnswer(
        exercise.exercise_id,
        answer,
        exercise.english_target
      );
      setResults((prev) => [...prev, result]);
      return result;
    },
    [exercises, currentIndex]
  );

  // 次の問題へ
  const handleNext = useCallback(() => {
    if (currentIndex + 1 >= exercises.length) {
      setPageState("finished");
    } else {
      setCurrentIndex((prev) => prev + 1);
    }
  }, [currentIndex, exercises.length]);

  // リスタート
  const handleRestart = useCallback(() => {
    setPageState("setup");
    setExercises([]);
    setCurrentIndex(0);
    setResults([]);
  }, []);

  // 正解数カウント
  const correctCount = results.filter((r) => r.is_correct).length;
  const totalScore = results.reduce((sum, r) => sum + r.score, 0);

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* セットアップ画面 */}
        {pageState === "setup" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md space-y-6 text-center">
              <div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Flash Translation
                </h1>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  日本語を見て、瞬時に英語に訳す練習です
                </p>
              </div>

              {/* エラー */}
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400">
                  {error}
                </div>
              )}

              {/* 開始ボタン */}
              <button
                onClick={handleStart}
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Start (10 Questions)
              </button>
            </div>
          </div>
        )}

        {/* プレイ中 */}
        {pageState === "playing" && exercises[currentIndex] && (
          <div className="flex-1 flex flex-col items-center justify-center py-4">
            {/* スコア表示 */}
            <div className="flex items-center gap-4 mb-6 text-sm">
              <span className="text-green-400 font-semibold">
                {correctCount} correct
              </span>
              <span className="text-[var(--color-text-muted)]">
                / {results.length} answered
              </span>
            </div>

            <FlashCard
              exercise={exercises[currentIndex]}
              onSubmit={handleSubmit}
              onNext={handleNext}
              questionNumber={currentIndex + 1}
              totalQuestions={exercises.length}
            />
          </div>
        )}

        {/* リザルト画面 */}
        {pageState === "finished" && (
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
                  {exercises.length} questions
                </p>
              </div>

              {/* スコア */}
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 space-y-4">
                <div className="text-center">
                  <p className="text-5xl font-heading font-bold text-primary">
                    {correctCount}
                    <span className="text-lg text-[var(--color-text-muted)]">
                      /{exercises.length}
                    </span>
                  </p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">
                    Correct Answers
                  </p>
                </div>

                <div className="w-full h-3 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      correctCount / exercises.length >= 0.8
                        ? "bg-green-400"
                        : correctCount / exercises.length >= 0.5
                          ? "bg-warning"
                          : "bg-red-400"
                    }`}
                    style={{
                      width: `${(correctCount / exercises.length) * 100}%`,
                    }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div>
                    <p className="text-xl font-bold text-[var(--color-text-primary)]">
                      {Math.round(totalScore * 10) / 10}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Total Score
                    </p>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-[var(--color-text-primary)]">
                      {Math.round((correctCount / exercises.length) * 100)}%
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Accuracy
                    </p>
                  </div>
                </div>
              </div>

              {/* 各問の結果一覧 */}
              <div className="space-y-2 text-left">
                {results.map((result, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-3 p-3 rounded-xl text-xs ${
                      result.is_correct
                        ? "bg-green-500/5 border border-green-500/10"
                        : "bg-red-500/5 border border-red-500/10"
                    }`}
                  >
                    <span
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                        result.is_correct
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[var(--color-text-secondary)] truncate">
                        {exercises[i]?.japanese}
                      </p>
                      <p className="text-accent truncate mt-0.5">
                        {result.corrected}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* アクションボタン */}
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
