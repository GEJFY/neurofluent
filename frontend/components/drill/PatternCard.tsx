"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Send,
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  ArrowRight,
} from "lucide-react";

/**
 * PatternCard - パターンプラクティス用カード
 * テンプレート表示 → 入力 → 結果表示
 */

/** パターン練習問題の型（ページから受け取る） */
interface PatternExercise {
  exercise_id: string;
  category: string;
  template: string;
  blank_prompt: string;
  japanese_hint: string;
  example_answer: string;
  difficulty: string;
}

/** パターン回答チェック結果の型（ページから受け取る） */
interface PatternCheckResult {
  is_correct: boolean;
  score: number;
  corrected: string;
  explanation: string;
  usage_tip: string;
}

interface PatternCardProps {
  exercise: PatternExercise;
  onSubmit: (answer: string) => Promise<PatternCheckResult>;
  onNext: () => void;
  questionNumber: number;
  totalQuestions: number;
}

type CardPhase = "input" | "result";

// カテゴリーバッジの色マッピング
const CATEGORY_COLORS: Record<string, string> = {
  meeting: "bg-primary/15 text-primary",
  negotiation: "bg-red-500/15 text-red-400",
  presentation: "bg-accent/15 text-accent",
  email: "bg-green-500/15 text-green-400",
  discussion: "bg-warning/15 text-warning",
  general: "bg-[var(--color-text-muted)]/15 text-[var(--color-text-muted)]",
};

export default function PatternCard({
  exercise,
  onSubmit,
  onNext,
  questionNumber,
  totalQuestions,
}: PatternCardProps) {
  const [phase, setPhase] = useState<CardPhase>("input");
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<PatternCheckResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // 新しい問題の時にリセット
  useEffect(() => {
    setPhase("input");
    setAnswer("");
    setResult(null);
    setShowHint(false);
    inputRef.current?.focus();
  }, [exercise.exercise_id]);

  // 回答送信
  const handleSubmit = useCallback(async () => {
    if (!answer.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await onSubmit(answer.trim());
      setResult(res);
      setPhase("result");
    } catch {
      // エラー時はフェーズ変更しない
    } finally {
      setIsSubmitting(false);
    }
  }, [answer, isSubmitting, onSubmit]);

  // Enterで送信
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // テンプレート内の___をハイライト表示
  const renderTemplate = (template: string) => {
    const parts = template.split("_____");
    if (parts.length === 1) {
      // _____がない場合は___で分割
      const altParts = template.split(/_{2,}/);
      if (altParts.length <= 1) return <span>{template}</span>;
      return (
        <>
          {altParts.map((part, i) => (
            <span key={i}>
              {part}
              {i < altParts.length - 1 && (
                <span className="inline-block min-w-[80px] mx-1 border-b-2 border-dashed border-primary/50 text-primary font-semibold">
                  {phase === "result" && result ? result.corrected : "\u00A0\u00A0\u00A0\u00A0\u00A0"}
                </span>
              )}
            </span>
          ))}
        </>
      );
    }
    return (
      <>
        {parts.map((part, i) => (
          <span key={i}>
            {part}
            {i < parts.length - 1 && (
              <span className="inline-block min-w-[80px] mx-1 border-b-2 border-dashed border-primary/50 text-primary font-semibold">
                {phase === "result" && result ? result.corrected : "\u00A0\u00A0\u00A0\u00A0\u00A0"}
              </span>
            )}
          </span>
        ))}
      </>
    );
  };

  const categoryColor = CATEGORY_COLORS[exercise.category] || CATEGORY_COLORS.general;

  return (
    <div className="w-full max-w-lg lg:max-w-2xl mx-auto">
      {/* 進捗バー */}
      <div className="flex items-center justify-between mb-4 text-xs text-[var(--color-text-muted)]">
        <span>
          {questionNumber} / {totalQuestions}
        </span>
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${categoryColor}`}>
          {exercise.category}
        </span>
      </div>
      <div className="w-full h-1.5 bg-[var(--color-bg-card)] rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-500"
          style={{
            width: `${(questionNumber / totalQuestions) * 100}%`,
          }}
        />
      </div>

      {/* メインカード */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 space-y-6">
        {/* テンプレート表示 */}
        <div>
          <p className="text-xs text-[var(--color-text-muted)] mb-3 uppercase tracking-wider">
            Fill in the blank
          </p>
          <p className="text-base md:text-lg lg:text-xl text-[var(--color-text-primary)] leading-relaxed">
            {renderTemplate(exercise.template)}
          </p>
        </div>

        {/* ブランクプロンプト（ヒントワード） */}
        <div className="flex items-center gap-2 text-xs text-accent">
          <Lightbulb className="w-3.5 h-3.5 shrink-0" />
          <span>Options: {exercise.blank_prompt}</span>
        </div>

        {/* 入力フェーズ */}
        {phase === "input" && (
          <div className="space-y-4">
            {/* 日本語ヒント（折りたたみ） */}
            <button
              onClick={() => setShowHint(!showHint)}
              className="flex items-center gap-1.5 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
            >
              {showHint ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
              Japanese Hint
            </button>
            {showHint && (
              <div className="p-3 rounded-lg bg-[var(--color-bg-primary)]/50 animate-fade-in">
                <p className="text-sm text-[var(--color-text-secondary)] font-ja">
                  {exercise.japanese_hint}
                </p>
              </div>
            )}

            {/* テキスト入力 */}
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer..."
                className="flex-1 px-4 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] text-sm focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
                disabled={isSubmitting}
                autoComplete="off"
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
            {/* 正誤インジケーター */}
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
                  Score: {Math.round(result.score)}%
                </p>
              </div>
            </div>

            {/* ユーザー回答 vs 模範解答 */}
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
              {!result.is_correct && (
                <div className="flex items-start gap-2 text-sm">
                  <span className="text-[var(--color-text-muted)] shrink-0 w-16">
                    Answer:
                  </span>
                  <span className="text-accent font-medium">
                    {result.corrected}
                  </span>
                </div>
              )}
            </div>

            {/* 解説 */}
            {result.explanation && (
              <div className="p-3 rounded-lg bg-[var(--color-bg-primary)]/50">
                <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                  {result.explanation}
                </p>
              </div>
            )}

            {/* 使い方のヒント */}
            {result.usage_tip && (
              <div className="p-3 rounded-lg bg-accent/5 border border-accent/10">
                <div className="flex items-start gap-2">
                  <Lightbulb className="w-3.5 h-3.5 text-accent mt-0.5 shrink-0" />
                  <p className="text-[11px] text-accent/80 leading-relaxed">
                    {result.usage_tip}
                  </p>
                </div>
              </div>
            )}

            {/* 次へボタン */}
            <button
              onClick={onNext}
              className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
            >
              {questionNumber < totalQuestions ? (
                <>
                  Next Pattern
                  <ArrowRight className="w-4 h-4" />
                </>
              ) : (
                "See Results"
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
