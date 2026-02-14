"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  AlertCircle,
  ArrowUpCircle,
  CheckCircle2,
  BookOpen,
} from "lucide-react";
import type { FeedbackData } from "@/lib/api";

/**
 * フィードバックパネル
 * メッセージの下に表示される折りたたみ可能なフィードバック
 * - 文法エラー（赤→緑）
 * - 表現アップグレード（before→after）
 * - ポジティブフィードバック（緑チェック）
 * - 語彙レベルバッジ
 */
interface FeedbackPanelProps {
  feedback: FeedbackData;
  defaultExpanded?: boolean;
}

export default function FeedbackPanel({
  feedback,
  defaultExpanded = false,
}: FeedbackPanelProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const hasContent =
    feedback.grammar_errors.length > 0 ||
    feedback.expression_upgrades.length > 0 ||
    feedback.positive_feedback.length > 0;

  if (!hasContent) return null;

  return (
    <div className="mt-2 rounded-xl border border-[var(--color-border)] overflow-hidden bg-[var(--color-bg-primary)]/50">
      {/* ヘッダー（トグルボタン） */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-card)] transition-colors"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Feedback</span>
          {/* 語彙レベルバッジ */}
          {feedback.vocabulary_level && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-accent/20 text-accent">
              {feedback.vocabulary_level}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-3.5 h-3.5" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5" />
        )}
      </button>

      {/* 展開コンテンツ */}
      {isExpanded && (
        <div className="px-3 pb-3 space-y-3 animate-fade-in">
          {/* 文法エラー */}
          {feedback.grammar_errors.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-1.5 text-red-400">
                <AlertCircle className="w-3.5 h-3.5" />
                <span className="text-[11px] font-semibold">Grammar</span>
              </div>
              {feedback.grammar_errors.map((error, i) => (
                <div key={i} className="pl-5 space-y-0.5">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="line-through text-red-400/80">
                      {error.original}
                    </span>
                    <span className="text-[var(--color-text-muted)]">&rarr;</span>
                    <span className="text-green-400 font-medium">
                      {error.corrected}
                    </span>
                  </div>
                  <p className="text-[11px] text-[var(--color-text-muted)]">
                    {error.explanation}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* 表現アップグレード */}
          {feedback.expression_upgrades.length > 0 && (
            <div className="space-y-2">
              <div className="flex items-center gap-1.5 text-primary">
                <ArrowUpCircle className="w-3.5 h-3.5" />
                <span className="text-[11px] font-semibold">
                  Expression Upgrade
                </span>
              </div>
              {feedback.expression_upgrades.map((upgrade, i) => (
                <div key={i} className="pl-5 space-y-0.5">
                  <div className="flex items-center gap-2 text-xs flex-wrap">
                    <span className="text-[var(--color-text-secondary)]">
                      {upgrade.original}
                    </span>
                    <span className="text-[var(--color-text-muted)]">&rarr;</span>
                    <span className="text-primary font-medium">
                      {upgrade.upgraded}
                    </span>
                  </div>
                  <p className="text-[11px] text-[var(--color-text-muted)]">
                    {upgrade.context}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* ポジティブフィードバック */}
          {feedback.positive_feedback && (
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5 text-green-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span className="text-[11px] font-semibold">Good Points</span>
              </div>
              <p className="pl-5 text-xs text-green-400/80">
                {feedback.positive_feedback}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
