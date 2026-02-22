"use client";

import { useState, useEffect, useCallback } from "react";
import { Loader2, CheckCircle2, Calendar, RotateCcw } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import ReviewCard from "@/components/drill/ReviewCard";
import { api, type ReviewItemResponse } from "@/lib/api";

/**
 * Spaced Repetition Review ページ
 * - 復習カード表示
 * - Show Answer → 4段階評価（1-4）
 * - 進捗インジケーター
 * - 次回復習日表示
 */

type PageState = "loading" | "reviewing" | "empty" | "finished" | "error";

export default function ReviewPage() {
  const [pageState, setPageState] = useState<PageState>("loading");
  const [items, setItems] = useState<ReviewItemResponse[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [completedCount, setCompletedCount] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<{
    next_review_at: string;
    new_interval_days: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 復習アイテム取得
  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const data = await api.getDueReviews();
        if (data.length === 0) {
          setPageState("empty");
        } else {
          setItems(data);
          setPageState("reviewing");
        }
      } catch (err) {
        console.error("Failed to fetch reviews:", err);
        setError("復習アイテムの読み込みに失敗しました");
        setPageState("error");
      }
    };

    fetchReviews();
  }, []);

  // 評価送信（rating: 1=Again, 2=Hard, 3=Good, 4=Easy）
  const handleRate = useCallback(
    async (rating: number) => {
      const currentItem = items[currentIndex];
      if (!currentItem || isSubmitting) return;

      setIsSubmitting(true);
      try {
        const result = await api.completeReview(currentItem.id, rating);
        setLastResult(result);
        setCompletedCount((prev) => prev + 1);

        // 短時間表示後に次のカードへ
        setTimeout(() => {
          if (currentIndex + 1 >= items.length) {
            setPageState("finished");
          } else {
            setCurrentIndex((prev) => prev + 1);
            setLastResult(null);
          }
          setIsSubmitting(false);
        }, 1500);
      } catch (err) {
        console.error("Failed to complete review:", err);
        setIsSubmitting(false);
      }
    },
    [items, currentIndex, isSubmitting]
  );

  // 再読み込み
  const handleReload = useCallback(() => {
    setPageState("loading");
    setItems([]);
    setCurrentIndex(0);
    setCompletedCount(0);
    setLastResult(null);
    setError(null);

    const fetchReviews = async () => {
      try {
        const data = await api.getDueReviews();
        if (data.length === 0) {
          setPageState("empty");
        } else {
          setItems(data);
          setPageState("reviewing");
        }
      } catch {
        setError("復習アイテムの読み込みに失敗しました");
        setPageState("error");
      }
    };

    fetchReviews();
  }, []);

  return (
    <AppShell>
      <div className="min-h-[70vh] flex flex-col">
        {/* ヘッダー */}
        <div className="mb-6">
          <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            Spaced Review
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1 leading-relaxed">
            間隔反復法で効率的に記憶を定着させましょう
          </p>
        </div>

        {/* ローディング */}
        {pageState === "loading" && (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        )}

        {/* エラー */}
        {pageState === "error" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-3">
              <p className="text-sm text-red-400">{error}</p>
              <button
                onClick={handleReload}
                className="text-xs text-primary hover:underline"
              >
                再読み込み
              </button>
            </div>
          </div>
        )}

        {/* 復習アイテムなし */}
        {pageState === "empty" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h2 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                  All caught up!
                </h2>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  今日の復習アイテムはすべて完了です
                </p>
              </div>
              <button
                onClick={handleReload}
                className="px-6 py-2.5 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border)] text-sm text-[var(--color-text-secondary)] hover:border-primary/30 transition-colors flex items-center gap-2 mx-auto"
              >
                <RotateCcw className="w-4 h-4" />
                再チェック
              </button>
            </div>
          </div>
        )}

        {/* 復習中 */}
        {pageState === "reviewing" && items[currentIndex] && (
          <div className="flex-1 flex flex-col items-center justify-center py-4 relative">
            {/* 次回復習日のトースト */}
            {lastResult && (
              <div className="absolute top-0 left-1/2 -translate-x-1/2 animate-slide-up z-10">
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-accent/10 border border-accent/20 text-xs text-accent">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>
                    Next review: {lastResult.new_interval_days} day
                    {lastResult.new_interval_days !== 1 ? "s" : ""} later
                  </span>
                </div>
              </div>
            )}

            <ReviewCard
              item={items[currentIndex]}
              onRate={handleRate}
              isSubmitting={isSubmitting}
              currentIndex={currentIndex}
              totalItems={items.length}
            />
          </div>
        )}

        {/* 完了画面 */}
        {pageState === "finished" && (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md text-center space-y-6">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h2 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  Session Complete!
                </h2>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  お疲れさまでした
                </p>
              </div>

              {/* 統計 */}
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-3xl font-heading font-bold text-primary">
                      {completedCount}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Items Reviewed
                    </p>
                  </div>
                  <div>
                    <p className="text-3xl font-heading font-bold text-accent">
                      {items.length}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      Total Due
                    </p>
                  </div>
                </div>
              </div>

              {/* アクション */}
              <div className="space-y-2">
                <button
                  onClick={handleReload}
                  className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 transition-colors flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Check for More
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
