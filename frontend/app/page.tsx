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
        <div className="space-y-8">
          {/* 挨拶セクション */}
          <div className="space-y-2">
            <h1 className="text-2xl md:text-3xl font-heading font-bold text-[var(--color-text-primary)] leading-tight">
              {getGreeting()},{" "}
              <span className="text-primary">
                {user?.name || "User"}
              </span>
            </h1>
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              今日も英語力を磨きましょう
            </p>
          </div>

          {/* 上段: 統計サマリー + ストリーク */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {/* 学習統計 */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
              <h3 className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-4">
                Learning Stats
              </h3>
              <div className="grid grid-cols-2 gap-x-4 gap-y-5">
                <div className="space-y-1">
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)] leading-none">
                    {dashboard?.total_practice_minutes || 0}
                  </p>
                  <p className="text-[11px] text-[var(--color-text-muted)] leading-snug">
                    Total Minutes
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)] leading-none">
                    {dashboard?.total_sessions || 0}
                  </p>
                  <p className="text-[11px] text-[var(--color-text-muted)] leading-snug">
                    Sessions
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)] leading-none">
                    {dashboard?.total_expressions_learned || 0}
                  </p>
                  <p className="text-[11px] text-[var(--color-text-muted)] leading-snug">
                    Expressions
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)] leading-none">
                    {dashboard?.pending_reviews || 0}
                  </p>
                  <p className="text-[11px] text-[var(--color-text-muted)] leading-snug">
                    Pending Reviews
                  </p>
                </div>
              </div>
            </div>

            {/* ストリーク */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
              <div className="flex items-center gap-5">
                <div className="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center">
                  <Flame className="w-8 h-8 text-warning" />
                </div>
                <div className="space-y-1">
                  <p className="text-4xl font-heading font-bold text-[var(--color-text-primary)] leading-none">
                    {dashboard?.streak_days || 0}
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)]">
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
            <h2 className="text-base font-heading font-semibold text-[var(--color-text-primary)] mb-4">
              Quick Start
            </h2>
            <div className="space-y-3 lg:grid lg:grid-cols-3 lg:gap-4 lg:space-y-0">
              <Link
                href="/review"
                className="flex items-center gap-4 p-4 md:p-5 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl hover:border-primary/30 transition-all group"
              >
                <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                  <RotateCcw className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)] leading-snug">
                      Spaced Review
                    </p>
                    {(dashboard?.pending_reviews || 0) > 0 && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-500/15 text-red-400">
                        {dashboard?.pending_reviews} due
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                    復習アイテムを確認しましょう
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-primary transition-colors shrink-0" />
              </Link>

              <Link
                href="/speaking/flash"
                className="flex items-center gap-4 p-4 md:p-5 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl hover:border-primary/30 transition-all group"
              >
                <div className="w-11 h-11 rounded-xl bg-accent/10 flex items-center justify-center shrink-0">
                  <Zap className="w-5 h-5 text-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)] leading-snug">
                    Flash Translation
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                    瞬間英作文で反射力を鍛えよう
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-primary transition-colors shrink-0" />
              </Link>

              <Link
                href="/talk"
                className="flex items-center gap-4 p-4 md:p-5 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl hover:border-primary/30 transition-all group"
              >
                <div className="w-11 h-11 rounded-xl bg-warning/10 flex items-center justify-center shrink-0">
                  <MessageCircle className="w-5 h-5 text-warning" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-[var(--color-text-primary)] leading-snug">
                    AI Free Talk
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                    AIと自由に英会話を練習しよう
                  </p>
                </div>
                <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-primary transition-colors shrink-0" />
              </Link>
            </div>
          </div>

          {/* 直近の学習統計 */}
          {dashboard?.recent_daily_stats && dashboard.recent_daily_stats.length > 0 && (
            <div>
              <h2 className="text-base font-heading font-semibold text-[var(--color-text-primary)] mb-4">
                Recent Activity
              </h2>
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
                <div className="space-y-4">
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
