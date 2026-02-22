"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, CheckCircle2, XCircle, Lightbulb } from "lucide-react";
import type { FlashExercise, FlashCheckResponse } from "@/lib/api";

/**
 * Flash Translation カード
 * 日本語文を表示 → カウントダウン → 英訳入力 → 結果表示
 */
interface FlashCardProps {
  exercise: FlashExercise;
  onSubmit: (answer: string) => Promise<FlashCheckResponse>;
  onNext: () => void;
  questionNumber: number;
  totalQuestions: number;
}

type CardPhase = "countdown" | "input" | "result";

export default function FlashCard({
  exercise,
  onSubmit,
  onNext,
  questionNumber,
  totalQuestions,
}: FlashCardProps) {
  const [phase, setPhase] = useState<CardPhase>("countdown");
  const [countdown, setCountdown] = useState(3);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<FlashCheckResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // カウントダウンタイマー
  useEffect(() => {
    setPhase("countdown");
    setCountdown(3);
    setAnswer("");
    setResult(null);
  }, [exercise.exercise_id]);

  useEffect(() => {
    if (phase !== "countdown") return;

    if (countdown === 0) {
      setPhase("input");
      return;
    }

    const timer = setTimeout(() => {
      setCountdown((c) => c - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [countdown, phase]);

  // 入力フェーズになったらフォーカス
  useEffect(() => {
    if (phase === "input") {
      inputRef.current?.focus();
    }
  }, [phase]);

  // 回答送信
  const handleSubmit = useCallback(async () => {
    if (!answer.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await onSubmit(answer.trim());
      setResult(res);
      setPhase("result");
    } catch {
      // エラーの場合でもフェーズは変えない
    } finally {
      setIsSubmitting(false);
    }
  }, [answer, isSubmitting, onSubmit]);

  // Enterキーで送信
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-lg lg:max-w-2xl mx-auto">
      {/* 進捗バー */}
      <div className="flex items-center justify-between mb-4 text-xs text-[var(--color-text-muted)]">
        <span>
          {questionNumber} / {totalQuestions}
        </span>
        <span>{exercise.difficulty}</span>
      </div>
      <div className="w-full h-1.5 bg-[var(--color-bg-card)] rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-500"
          style={{
            width: `${(questionNumber / totalQuestions) * 100}%`,
          }}
        />
      </div>

      {/* メインカード */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 space-y-6">
        {/* 日本語テキスト */}
        <div className="text-center">
          <p className="text-xs text-[var(--color-text-muted)] mb-2 uppercase tracking-wider">
            Translate to English
          </p>
          <p className="text-xl md:text-2xl lg:text-3xl font-ja font-medium text-[var(--color-text-primary)] leading-relaxed">
            {exercise.japanese}
          </p>
          {exercise.key_pattern && (
            <p className="text-[11px] text-accent mt-2">
              Pattern: {exercise.key_pattern}
            </p>
          )}
        </div>

        {/* カウントダウンフェーズ */}
        {phase === "countdown" && (
          <div className="flex items-center justify-center py-8">
            <span
              key={countdown}
              className="text-6xl font-heading font-bold text-primary animate-countdown"
            >
              {countdown}
            </span>
          </div>
        )}

        {/* 入力フェーズ */}
        {phase === "input" && (
          <div className="space-y-4">
            {exercise.hints.length > 0 && (
              <div className="flex items-center gap-2 text-xs text-warning">
                <Lightbulb className="w-3.5 h-3.5" />
                <span>Hint: {exercise.hints.join(" / ")}</span>
              </div>
            )}
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer in English..."
                className="flex-1 px-4 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                disabled={isSubmitting}
              />
              <button
                onClick={handleSubmit}
                disabled={!answer.trim() || isSubmitting}
                className="px-4 py-3 rounded-xl bg-primary text-white hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* 結果フェーズ */}
        {phase === "result" && result && (
          <div className="space-y-4 animate-fade-in">
            {/* 正誤表示 */}
            <div
              className={`flex items-center gap-3 p-4 rounded-xl ${
                result.is_correct
                  ? "bg-green-500/10 border border-green-500/20"
                  : "bg-red-500/10 border border-red-500/20"
              }`}
            >
              {result.is_correct ? (
                <CheckCircle2 className="w-6 h-6 text-green-400 shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-red-400 shrink-0" />
              )}
              <div>
                <p
                  className={`text-sm font-semibold ${
                    result.is_correct ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {result.is_correct ? "Correct!" : "Not quite..."}
                </p>
                <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                  Score: {Math.round(result.score * 100)}%
                </p>
              </div>
            </div>

            {/* ユーザーの回答 vs 模範回答 */}
            <div className="space-y-2">
              <div className="flex items-start gap-2 text-sm">
                <span className="text-[var(--color-text-muted)] shrink-0 w-16">
                  You:
                </span>
                <span
                  className={
                    result.is_correct
                      ? "text-green-400"
                      : "text-red-400 line-through"
                  }
                >
                  {answer}
                </span>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <span className="text-[var(--color-text-muted)] shrink-0 w-16">
                  Model:
                </span>
                <span className="text-accent font-medium">
                  {result.corrected}
                </span>
              </div>
            </div>

            {/* 解説 */}
            {result.explanation && (
              <div className="p-3 rounded-lg bg-[var(--color-bg-primary)]/50">
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                  {result.explanation}
                </p>
              </div>
            )}

            {/* 復習アイテム作成通知 */}
            {result.review_item_created && (
              <p className="text-[11px] text-accent text-center">
                This item has been added to your review list
              </p>
            )}

            {/* 次へボタン */}
            <button
              onClick={onNext}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors"
            >
              {questionNumber < totalQuestions ? "Next Question" : "See Results"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
