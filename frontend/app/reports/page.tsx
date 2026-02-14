"use client";

import { useState } from "react";
import {
  Clock,
  MessageCircle,
  Flame,
  Zap,
  TrendingUp,
  TrendingDown,
  Flag,
  Award,
  Download,
  Share2,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";

/**
 * レポートページ
 * 週次/月次の学習レポート表示
 */

type ReportType = "weekly" | "monthly";

// デモ用データ
const WEEKLY_REPORT = {
  summary: {
    minutes: 145,
    sessions: 18,
    streak: 5,
    newExpressions: 34,
  },
  dailyBreakdown: [
    { day: "Mon", minutes: 25 },
    { day: "Tue", minutes: 18 },
    { day: "Wed", minutes: 32 },
    { day: "Thu", minutes: 15 },
    { day: "Fri", minutes: 28 },
    { day: "Sat", minutes: 12 },
    { day: "Sun", minutes: 15 },
  ],
  improvements: [
    { area: "Speaking fluency", delta: "+8%" },
    { area: "Vocabulary range", delta: "+12 words" },
    { area: "Linking recognition", delta: "+15%" },
  ],
  areasForImprovement: [
    { area: "/æ/ vs /ʌ/ pronunciation", note: "正答率が45%に低下" },
    { area: "Grammar in formal contexts", note: "ビジネスモードでの文法エラー増加" },
    { area: "Listening speed adaptation", note: "高速音声の理解度が不足" },
  ],
  comparedToLastWeek: {
    minutesDelta: 12,
    sessionsDelta: 3,
    percentChange: "+9%",
  },
};

const MONTHLY_REPORT = {
  summary: {
    minutes: 580,
    sessions: 72,
    streak: 14,
    newExpressions: 136,
  },
  weeklyBreakdown: [
    { week: "Week 1", minutes: 120 },
    { week: "Week 2", minutes: 145 },
    { week: "Week 3", minutes: 130 },
    { week: "Week 4", minutes: 185 },
  ],
  monthOverMonth: {
    minutesDelta: 45,
    sessionsDelta: 10,
    percentChange: "+8%",
  },
  achievements: [
    { badge: "Consistent Learner", description: "14日連続学習達成", earned: true },
    { badge: "Vocabulary Builder", description: "100表現以上習得", earned: true },
    { badge: "Pronunciation Pro", description: "発音スコア80%以上", earned: false },
    { badge: "Session Master", description: "月50セッション達成", earned: true },
  ],
  trends: [
    { metric: "Speaking", current: 72, previous: 65 },
    { metric: "Listening", current: 65, previous: 62 },
    { metric: "Vocabulary", current: 78, previous: 70 },
    { metric: "Grammar", current: 68, previous: 70 },
    { metric: "Pronunciation", current: 55, previous: 50 },
  ],
};

export default function ReportsPage() {
  const [reportType, setReportType] = useState<ReportType>("weekly");

  const maxDailyMinutes = Math.max(
    ...WEEKLY_REPORT.dailyBreakdown.map((d) => d.minutes)
  );
  const maxWeeklyMinutes = Math.max(
    ...MONTHLY_REPORT.weeklyBreakdown.map((w) => w.minutes)
  );

  return (
    <AppShell>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
              Learning Reports
            </h1>
            <p className="text-sm text-[var(--color-text-muted)]">
              学習の振り返りと成果の確認
            </p>
          </div>

          {/* レポートタイプ切り替え */}
          <div className="flex bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-1">
            <button
              onClick={() => setReportType("weekly")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                reportType === "weekly"
                  ? "bg-primary text-white"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Weekly
            </button>
            <button
              onClick={() => setReportType("monthly")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                reportType === "monthly"
                  ? "bg-primary text-white"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              Monthly
            </button>
          </div>
        </div>

        {/* Weekly Report */}
        {reportType === "weekly" && (
          <div className="space-y-4">
            {/* サマリー統計 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                {
                  label: "Practice Time",
                  value: `${WEEKLY_REPORT.summary.minutes}`,
                  unit: "min",
                  icon: Clock,
                  color: "text-primary",
                  bgColor: "bg-primary/10",
                },
                {
                  label: "Sessions",
                  value: `${WEEKLY_REPORT.summary.sessions}`,
                  unit: "",
                  icon: MessageCircle,
                  color: "text-accent",
                  bgColor: "bg-accent/10",
                },
                {
                  label: "Streak",
                  value: `${WEEKLY_REPORT.summary.streak}`,
                  unit: "days",
                  icon: Flame,
                  color: "text-warning",
                  bgColor: "bg-warning/10",
                },
                {
                  label: "New Expressions",
                  value: `${WEEKLY_REPORT.summary.newExpressions}`,
                  unit: "",
                  icon: Zap,
                  color: "text-green-400",
                  bgColor: "bg-green-500/10",
                },
              ].map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.label}
                    className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-4"
                  >
                    <div
                      className={`w-8 h-8 rounded-lg ${card.bgColor} flex items-center justify-center mb-2`}
                    >
                      <Icon className={`w-4 h-4 ${card.color}`} />
                    </div>
                    <p className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                      {card.value}
                      {card.unit && (
                        <span className="text-xs text-[var(--color-text-muted)] ml-1">
                          {card.unit}
                        </span>
                      )}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
                      {card.label}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* 日別ブレイクダウン */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Daily Breakdown
              </p>
              <div className="flex items-end gap-2 h-40">
                {WEEKLY_REPORT.dailyBreakdown.map((day) => (
                  <div
                    key={day.day}
                    className="flex-1 flex flex-col items-center gap-1"
                  >
                    <span className="text-[10px] font-semibold text-[var(--color-text-primary)]">
                      {day.minutes}m
                    </span>
                    <div className="w-full relative" style={{ height: "120px" }}>
                      <div
                        className="absolute bottom-0 w-full bg-primary/20 rounded-t-lg transition-all duration-700 hover:bg-primary/30"
                        style={{
                          height: `${(day.minutes / maxDailyMinutes) * 100}%`,
                        }}
                      >
                        <div
                          className="absolute bottom-0 w-full bg-primary rounded-t-lg"
                          style={{ height: "40%" }}
                        />
                      </div>
                    </div>
                    <span className="text-[10px] text-[var(--color-text-muted)]">
                      {day.day}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 先週との比較 */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  vs. Last Week
                </p>
                <span
                  className={`text-sm font-bold ${
                    WEEKLY_REPORT.comparedToLastWeek.minutesDelta >= 0
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {WEEKLY_REPORT.comparedToLastWeek.percentChange}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                {WEEKLY_REPORT.comparedToLastWeek.minutesDelta >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-400" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-400" />
                )}
                <span className="text-xs text-[var(--color-text-secondary)]">
                  先週より{Math.abs(WEEKLY_REPORT.comparedToLastWeek.minutesDelta)}分多く学習しました
                </span>
              </div>
            </div>

            {/* Top Improvements */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Top Improvements
              </p>
              {WEEKLY_REPORT.improvements.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 rounded-xl bg-green-500/5 border border-green-500/10"
                >
                  <TrendingUp className="w-4 h-4 text-green-400 shrink-0" />
                  <span className="text-sm text-[var(--color-text-primary)] flex-1">
                    {item.area}
                  </span>
                  <span className="text-xs font-semibold text-green-400">
                    {item.delta}
                  </span>
                </div>
              ))}
            </div>

            {/* Areas for Improvement */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Areas for Improvement
              </p>
              {WEEKLY_REPORT.areasForImprovement.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-3 rounded-xl bg-warning/5 border border-warning/10"
                >
                  <Flag className="w-4 h-4 text-warning shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-[var(--color-text-primary)]">
                      {item.area}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)]">
                      {item.note}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Monthly Report */}
        {reportType === "monthly" && (
          <div className="space-y-4">
            {/* サマリー統計 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                {
                  label: "Total Time",
                  value: `${MONTHLY_REPORT.summary.minutes}`,
                  unit: "min",
                  icon: Clock,
                  color: "text-primary",
                  bgColor: "bg-primary/10",
                },
                {
                  label: "Sessions",
                  value: `${MONTHLY_REPORT.summary.sessions}`,
                  unit: "",
                  icon: MessageCircle,
                  color: "text-accent",
                  bgColor: "bg-accent/10",
                },
                {
                  label: "Best Streak",
                  value: `${MONTHLY_REPORT.summary.streak}`,
                  unit: "days",
                  icon: Flame,
                  color: "text-warning",
                  bgColor: "bg-warning/10",
                },
                {
                  label: "Expressions",
                  value: `${MONTHLY_REPORT.summary.newExpressions}`,
                  unit: "",
                  icon: Zap,
                  color: "text-green-400",
                  bgColor: "bg-green-500/10",
                },
              ].map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.label}
                    className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-4"
                  >
                    <div
                      className={`w-8 h-8 rounded-lg ${card.bgColor} flex items-center justify-center mb-2`}
                    >
                      <Icon className={`w-4 h-4 ${card.color}`} />
                    </div>
                    <p className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                      {card.value}
                      {card.unit && (
                        <span className="text-xs text-[var(--color-text-muted)] ml-1">
                          {card.unit}
                        </span>
                      )}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
                      {card.label}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* 週別ブレイクダウン */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Weekly Breakdown
              </p>
              <div className="flex items-end gap-3 h-40">
                {MONTHLY_REPORT.weeklyBreakdown.map((week) => (
                  <div
                    key={week.week}
                    className="flex-1 flex flex-col items-center gap-1"
                  >
                    <span className="text-[10px] font-semibold text-[var(--color-text-primary)]">
                      {week.minutes}m
                    </span>
                    <div className="w-full relative" style={{ height: "120px" }}>
                      <div
                        className="absolute bottom-0 w-full bg-primary/20 rounded-t-lg transition-all duration-700 hover:bg-primary/30"
                        style={{
                          height: `${(week.minutes / maxWeeklyMinutes) * 100}%`,
                        }}
                      >
                        <div
                          className="absolute bottom-0 w-full bg-primary rounded-t-lg"
                          style={{ height: "40%" }}
                        />
                      </div>
                    </div>
                    <span className="text-[10px] text-[var(--color-text-muted)]">
                      {week.week}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 月間比較 */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  vs. Last Month
                </p>
                <span
                  className={`text-sm font-bold ${
                    MONTHLY_REPORT.monthOverMonth.minutesDelta >= 0
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {MONTHLY_REPORT.monthOverMonth.percentChange}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-xs text-[var(--color-text-secondary)]">
                  先月より{Math.abs(MONTHLY_REPORT.monthOverMonth.minutesDelta)}分多く学習しました
                </span>
              </div>
            </div>

            {/* Month-over-month Trends */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Skill Trends
              </p>
              {MONTHLY_REPORT.trends.map((trend) => {
                const delta = trend.current - trend.previous;
                return (
                  <div
                    key={trend.metric}
                    className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-[var(--color-text-primary)] w-28">
                        {trend.metric}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-[var(--color-text-muted)]">
                          {trend.previous}%
                        </span>
                        <span className="text-[var(--color-text-muted)]">
                          &rarr;
                        </span>
                        <span className="text-xs font-semibold text-[var(--color-text-primary)]">
                          {trend.current}%
                        </span>
                      </div>
                    </div>
                    <span
                      className={`text-xs font-bold px-2 py-0.5 rounded-lg ${
                        delta > 0
                          ? "bg-green-500/10 text-green-400"
                          : delta < 0
                            ? "bg-red-500/10 text-red-400"
                            : "bg-[var(--color-bg-input)] text-[var(--color-text-muted)]"
                      }`}
                    >
                      {delta > 0 ? "+" : ""}
                      {delta}%
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Achievement Badges */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Achievement Badges
              </p>
              <div className="grid grid-cols-2 gap-2">
                {MONTHLY_REPORT.achievements.map((achievement, i) => (
                  <div
                    key={i}
                    className={`p-3 rounded-xl border text-center ${
                      achievement.earned
                        ? "bg-warning/5 border-warning/20"
                        : "bg-[var(--color-bg-primary)]/50 border-[var(--color-border)] opacity-50"
                    }`}
                  >
                    <Award
                      className={`w-6 h-6 mx-auto mb-1.5 ${
                        achievement.earned
                          ? "text-warning"
                          : "text-[var(--color-text-muted)]"
                      }`}
                    />
                    <p
                      className={`text-xs font-semibold ${
                        achievement.earned
                          ? "text-[var(--color-text-primary)]"
                          : "text-[var(--color-text-muted)]"
                      }`}
                    >
                      {achievement.badge}
                    </p>
                    <p className="text-[10px] text-[var(--color-text-muted)] mt-0.5">
                      {achievement.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Export/Share ボタン */}
        <div className="flex gap-3 justify-center pb-4">
          <button className="px-5 py-2.5 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border)] text-sm text-[var(--color-text-secondary)] hover:border-primary/30 transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </button>
          <button className="px-5 py-2.5 rounded-xl bg-[var(--color-bg-card)] border border-[var(--color-border)] text-sm text-[var(--color-text-secondary)] hover:border-primary/30 transition-colors flex items-center gap-2">
            <Share2 className="w-4 h-4" />
            Share
          </button>
        </div>
      </div>
    </AppShell>
  );
}
