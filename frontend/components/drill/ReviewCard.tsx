"use client";

import { useState } from "react";
import { Eye, RotateCcw, Frown, Smile, Star } from "lucide-react";
import type { ReviewItemResponse } from "@/lib/api";

/**
 * 復習カード（SRS）
 * 表: 復習内容のプレビュー + アイテムタイプバッジ
 * 裏: 詳細内容
 * 評価ボタン: Again(1), Hard(2), Good(3), Easy(4)
 */
interface ReviewCardProps {
  item: ReviewItemResponse;
  onRate: (rating: number) => void;
  isSubmitting?: boolean;
  currentIndex: number;
  totalItems: number;
}

/** 評価ボタン定義 */
const ratingButtons: {
  rating: number;
  label: string;
  color: string;
  icon: typeof Frown;
}[] = [
  { rating: 1, label: "Again", color: "bg-red-500/15 text-red-400 hover:bg-red-500/25", icon: RotateCcw },
  { rating: 2, label: "Hard", color: "bg-warning/15 text-warning hover:bg-warning/25", icon: Frown },
  { rating: 3, label: "Good", color: "bg-green-500/15 text-green-400 hover:bg-green-500/25", icon: Smile },
  { rating: 4, label: "Easy", color: "bg-accent/15 text-accent hover:bg-accent/25", icon: Star },
];

/** contentオブジェクトから表示用テキストを抽出 */
function getDisplayContent(content: Record<string, unknown>): {
  front: string;
  back: string;
  context?: string;
} {
  // flash_translation タイプの場合
  if (content.target && typeof content.target === "string") {
    return {
      front: content.target as string,
      back: (content.corrected as string) || (content.user_answer as string) || "",
      context: content.explanation as string,
    };
  }
  // expression_upgrade タイプの場合
  if (content.original && typeof content.original === "string") {
    return {
      front: content.original as string,
      back: (content.upgraded as string) || "",
      context: content.explanation as string,
    };
  }
  // フォールバック
  return {
    front: JSON.stringify(content).slice(0, 100),
    back: "",
  };
}

export default function ReviewCard({
  item,
  onRate,
  isSubmitting = false,
  currentIndex,
  totalItems,
}: ReviewCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);

  const display = getDisplayContent(item.content);

  /** アイテムタイプのバッジ色 */
  const typeBadgeClass =
    item.item_type === "flash_translation"
      ? "bg-primary/15 text-primary"
      : item.item_type === "expression_upgrade"
        ? "bg-warning/15 text-warning"
        : "bg-accent/15 text-accent";

  return (
    <div className="w-full max-w-lg lg:max-w-2xl mx-auto">
      {/* 進捗表示 */}
      <div className="flex items-center justify-between mb-4 text-xs text-[var(--color-text-muted)]">
        <span>
          {currentIndex + 1} / {totalItems}
        </span>
        <span>Rep #{item.repetitions}</span>
      </div>
      <div className="w-full h-1.5 bg-[var(--color-bg-card)] rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-500"
          style={{
            width: `${((currentIndex + 1) / totalItems) * 100}%`,
          }}
        />
      </div>

      {/* カード本体 */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
        {/* カード表面 */}
        <div className="p-6 md:p-8 text-center space-y-4">
          {/* タイプバッジ */}
          <span
            className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${typeBadgeClass}`}
          >
            {item.item_type.replace("_", " ")}
          </span>

          {/* メイン表現 */}
          <p className="text-xl md:text-2xl font-heading font-semibold text-[var(--color-text-primary)]">
            {display.front}
          </p>
        </div>

        {/* 答え表示ボタン / カード裏面 */}
        {!isFlipped ? (
          <div className="px-6 pb-6 md:px-8 md:pb-8">
            <button
              onClick={() => setIsFlipped(true)}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-primary)] transition-colors"
            >
              <Eye className="w-4 h-4" />
              <span>Show Answer</span>
            </button>
          </div>
        ) : (
          <div className="animate-fade-in">
            {/* 裏面コンテンツ */}
            <div className="px-6 md:px-8 space-y-3 border-t border-[var(--color-border)] pt-5">
              {display.back && (
                <div>
                  <p className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                    Answer
                  </p>
                  <p className="text-sm text-[var(--color-text-primary)]">
                    {display.back}
                  </p>
                </div>
              )}

              {display.context && (
                <div>
                  <p className="text-[11px] font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                    Explanation
                  </p>
                  <p className="text-sm text-accent italic">
                    {display.context}
                  </p>
                </div>
              )}
            </div>

            {/* 評価ボタン */}
            <div className="grid grid-cols-4 gap-2 p-4 md:p-6 mt-4">
              {ratingButtons.map(({ rating, label, color, icon: Icon }) => (
                <button
                  key={rating}
                  onClick={() => onRate(rating)}
                  disabled={isSubmitting}
                  className={`flex flex-col items-center gap-1.5 py-3 rounded-xl text-xs font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${color}`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
