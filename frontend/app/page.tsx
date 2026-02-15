"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Flame,
  MessageCircle,
  Zap,
  RotateCcw,
  ChevronRight,
  Loader2,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import { api, type DashboardData } from "@/lib/api";
import { useAuthStore } from "@/lib/stores/auth-store";

/**
 * ダッシュボードページ
 * - 時間帯に応じた挨拶
 * - ストリークカウンター
 * - 主要統計サマリー
 * - クイックアクセスメニュー
 */

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 6) return "Good night";
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setIsLoading(false);
      return;
    }

    const fetchDashboard = async () => {
      try {
        const data = await api.getDashboard();
        setDashboard(data);
      } catch (err) {
        console.error("Dashboard fetch failed:", err);
        setError("ダッシュボードの読み込みに失敗しました");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, [user]);

  return (
    <AppShell>
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-2">
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="text-xs text-primary hover:underline"
            >
              再読み込み
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* 挨拶セクション */}
          <div className="space-y-1">
            <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
              {getGreeting()},{" "}
              <span className="text-primary">
                {user?.name || "User"}
              </span>
            </h1>
            <p className="text-sm text-[var(--color-text-muted)]">
              今日も英語力を磨きましょう
            </p>
          </div>

          {/* 上段: 統計サマリー + ストリーク */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 学習統計 */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-[var(--color-text-secondary)] mb-3">
                Learning Stats
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                    {dashboard?.total_practice_minutes || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    Total Minutes
                  </p>
                </div>
                <div>
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                    {dashboard?.total_sessions || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    Sessions
                  </p>
                </div>
                <div>
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                    {dashboard?.total_expressions_learned || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    Expressions
                  </p>
                </div>
                <div>
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                    {dashboard?.pending_reviews || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    Pending Reviews
                  </p>
                </div>
              </div>
            </div>

            {/* ストリーク */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-warning/10 flex items-center justify-center">
                  <Flame className="w-7 h-7 text-warning" />
                </div>
                <div>
                  <p className="text-3xl font-heading font-bold text-[var(--color-text-primary)]">
                    {dashboard?.streak_days || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    Day Streak
                  </p>
                </div>
              </div>
              {dashboard?.avg_grammar_accuracy != null && (
                <div className="mt-4 pt-3 border-t border-[var(--color-border)]">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--color-text-muted)]">
                      Grammar Accuracy
                    </span>
                    <span className="text-green-400 font-semibold">
                      {Math.round(dashboard.avg_grammar_accuracy * 100)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* クイックアクセスメニュー */}
          <div>
            <h2 className="text-lg font-heading font-semibold text-[var(--color-text-primary)] mb-3">
              Quick Start
            </h2>
            <div className="space-y-2">
              <Link
                href="/review"
                className="flex items-center gap-4 p-4 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl hover:border-primary/30 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <RotateCcw className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      Spaced Review
                    </p>
                    {(dashboard?.pending_reviews || 0) > 0 && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-500/15 text-red-400">
                        {dashboard?.pending_reviews} due
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    復習アイテムを確認しましょう
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)] group-hover:text-primary transition-colors" />
              </Link>

              <Link
                href="/speaking/flash"
                className="flex items-center gap-4 p-4 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl hover:border-primary/30 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-accent" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                    Flash Translation
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    瞬間英作文で反射力を鍛えよう
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)] group-hover:text-primary transition-colors" />
              </Link>

              <Link
                href="/talk"
                className="flex items-center gap-4 p-4 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl hover:border-primary/30 transition-colors group"
              >
                <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-warning" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                    AI Free Talk
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    AIと自由に英会話を練習しよう
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)] group-hover:text-primary transition-colors" />
              </Link>
            </div>
          </div>

          {/* 直近の学習統計 */}
          {dashboard?.recent_daily_stats && dashboard.recent_daily_stats.length > 0 && (
            <div>
              <h2 className="text-lg font-heading font-semibold text-[var(--color-text-primary)] mb-3">
                Recent Activity
              </h2>
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
                <div className="space-y-3">
                  {dashboard.recent_daily_stats.slice(0, 5).map((stat, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-[var(--color-text-muted)]">
                        {stat.date}
                      </span>
                      <div className="flex items-center gap-4">
                        <span className="text-[var(--color-text-secondary)]">
                          {stat.practice_minutes}min
                        </span>
                        <span className="text-accent text-xs">
                          +{stat.new_expressions_learned} expr
                        </span>
                        {stat.reviews_completed > 0 && (
                          <span className="text-green-400 text-xs">
                            {stat.reviews_completed} reviews
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
