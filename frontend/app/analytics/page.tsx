"use client";

import { useState } from "react";
import {
  Clock,
  MessageCircle,
  BookOpen,
  Zap,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Target,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import SkillRadar from "@/components/analytics/SkillRadar";
import ProgressChart from "@/components/analytics/ProgressChart";
import RecommendationCard from "@/components/analytics/RecommendationCard";

/**
 * アナリティクスダッシュボードページ
 * 学習データの可視化と分析
 */

type Period = "week" | "month";
type Tab = "overview" | "skills" | "pronunciation" | "trends" | "recommendations";

// デモ用データ
const WEEKLY_STATS = {
  minutes: 145,
  minutesDelta: 12,
  sessions: 18,
  sessionsDelta: 3,
  reviews: 62,
  reviewsDelta: -5,
  expressions: 34,
  expressionsDelta: 8,
};

const MONTHLY_STATS = {
  minutes: 580,
  minutesDelta: 45,
  sessions: 72,
  sessionsDelta: 10,
  reviews: 248,
  reviewsDelta: 20,
  expressions: 136,
  expressionsDelta: 28,
};

const SKILL_SCORES = {
  speaking: 72,
  listening: 65,
  vocabulary: 78,
  grammar: 68,
  pronunciation: 55,
};

const WEEKLY_PROGRESS = [
  { date: "Mon", value: 25 },
  { date: "Tue", value: 18 },
  { date: "Wed", value: 32 },
  { date: "Thu", value: 15 },
  { date: "Fri", value: 28 },
  { date: "Sat", value: 12 },
  { date: "Sun", value: 15 },
];

const MONTHLY_PROGRESS = [
  { date: "W1", value: 120 },
  { date: "W2", value: 145 },
  { date: "W3", value: 130 },
  { date: "W4", value: 185 },
];

const PHONEME_PROGRESS = [
  { phoneme: "/r/-/l/", accuracy: 72, trend: "up" as const },
  { phoneme: "/θ/-/s/", accuracy: 58, trend: "up" as const },
  { phoneme: "/v/-/b/", accuracy: 85, trend: "stable" as const },
  { phoneme: "/f/-/h/", accuracy: 90, trend: "up" as const },
  { phoneme: "/æ/-/ʌ/", accuracy: 45, trend: "down" as const },
];

const TREND_DATA = [
  {
    label: "Speaking Fluency",
    current: 72,
    previous: 65,
    unit: "%",
  },
  {
    label: "Listening Accuracy",
    current: 65,
    previous: 62,
    unit: "%",
  },
  {
    label: "Grammar Accuracy",
    current: 68,
    previous: 70,
    unit: "%",
  },
  {
    label: "Vocabulary Range",
    current: 78,
    previous: 72,
    unit: "%",
  },
  {
    label: "Average Session",
    current: 8.2,
    previous: 7.5,
    unit: "min",
  },
];

const RECOMMENDATIONS = [
  {
    category: "pronunciation",
    title: "/æ/ vs /ʌ/ の区別練習",
    description:
      "この音素ペアの正答率が45%です。ミニマルペアを使った集中練習をお勧めします。",
    priority: "high",
    exercise_type: "pronunciation",
  },
  {
    category: "listening",
    title: "リダクション聞き取り強化",
    description:
      "会話中のリダクションの聞き取り精度を上げましょう。もごもごイングリッシュで練習できます。",
    priority: "medium",
    exercise_type: "mogomogo",
  },
  {
    category: "speaking",
    title: "ビジネスミーティング表現",
    description:
      "会議での表現バリエーションを増やしましょう。Meeting Facilitationモードで実践できます。",
    priority: "low",
    exercise_type: "talk",
  },
];

const TABS: { id: Tab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "skills", label: "Skills" },
  { id: "pronunciation", label: "Pronunciation" },
  { id: "trends", label: "Trends" },
  { id: "recommendations", label: "For You" },
];

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>("week");
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const stats = period === "week" ? WEEKLY_STATS : MONTHLY_STATS;
  const progressData = period === "week" ? WEEKLY_PROGRESS : MONTHLY_PROGRESS;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
              Learning Analytics
            </h1>
            <p className="text-sm text-[var(--color-text-muted)]">
              あなたの学習データを分析
            </p>
          </div>

          {/* 期間セレクタ */}
          <div className="flex bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-1">
            <button
              onClick={() => setPeriod("week")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                period === "week"
                  ? "bg-primary text-white"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              This Week
            </button>
            <button
              onClick={() => setPeriod("month")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                period === "month"
                  ? "bg-primary text-white"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              This Month
            </button>
          </div>
        </div>

        {/* タブナビ */}
        <div className="flex gap-1 overflow-x-auto pb-1 -mx-1 px-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? "bg-primary/10 text-primary"
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-card)]"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview タブ */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* サマリーカード */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                {
                  label: "Practice Time",
                  value: `${stats.minutes}`,
                  unit: "min",
                  delta: stats.minutesDelta,
                  icon: Clock,
                  color: "text-primary",
                  bgColor: "bg-primary/10",
                },
                {
                  label: "Sessions",
                  value: `${stats.sessions}`,
                  unit: "",
                  delta: stats.sessionsDelta,
                  icon: MessageCircle,
                  color: "text-accent",
                  bgColor: "bg-accent/10",
                },
                {
                  label: "Reviews",
                  value: `${stats.reviews}`,
                  unit: "",
                  delta: stats.reviewsDelta,
                  icon: BookOpen,
                  color: "text-warning",
                  bgColor: "bg-warning/10",
                },
                {
                  label: "New Expressions",
                  value: `${stats.expressions}`,
                  unit: "",
                  delta: stats.expressionsDelta,
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
                    <div className="flex items-center justify-between mb-3">
                      <div
                        className={`w-8 h-8 rounded-lg ${card.bgColor} flex items-center justify-center`}
                      >
                        <Icon className={`w-4 h-4 ${card.color}`} />
                      </div>
                      {card.delta !== 0 && (
                        <div
                          className={`flex items-center gap-0.5 text-[10px] font-medium ${
                            card.delta > 0
                              ? "text-green-400"
                              : "text-red-400"
                          }`}
                        >
                          {card.delta > 0 ? (
                            <TrendingUp className="w-3 h-3" />
                          ) : (
                            <TrendingDown className="w-3 h-3" />
                          )}
                          {card.delta > 0 ? "+" : ""}
                          {card.delta}
                        </div>
                      )}
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

            {/* 練習時間チャート */}
            <ProgressChart
              data={progressData}
              label={
                period === "week"
                  ? "Daily Practice (minutes)"
                  : "Weekly Practice (minutes)"
              }
            />
          </div>
        )}

        {/* Skills タブ */}
        {activeTab === "skills" && (
          <div className="space-y-6">
            <SkillRadar skills={SKILL_SCORES} />

            {/* スキル詳細バー */}
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Skill Breakdown
              </p>
              {Object.entries(SKILL_SCORES).map(([skill, score]) => (
                <div key={skill} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-[var(--color-text-primary)] capitalize">
                      {skill}
                    </span>
                    <span
                      className={`font-semibold ${
                        score >= 80
                          ? "text-green-400"
                          : score >= 60
                            ? "text-warning"
                            : "text-red-400"
                      }`}
                    >
                      {score}%
                    </span>
                  </div>
                  <div className="w-full h-2.5 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        score >= 80
                          ? "bg-green-400"
                          : score >= 60
                            ? "bg-warning"
                            : "bg-red-400"
                      }`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pronunciation タブ */}
        {activeTab === "pronunciation" && (
          <div className="space-y-4">
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Phoneme Progress
              </p>
              {PHONEME_PROGRESS.map((item) => (
                <div
                  key={item.phoneme}
                  className="flex items-center gap-4"
                >
                  <span className="text-sm font-mono text-[var(--color-text-primary)] w-16 shrink-0">
                    {item.phoneme}
                  </span>
                  <div className="flex-1">
                    <div className="w-full h-3 bg-[var(--color-bg-input)] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          item.accuracy >= 80
                            ? "bg-green-400"
                            : item.accuracy >= 50
                              ? "bg-warning"
                              : "bg-red-400"
                        }`}
                        style={{ width: `${item.accuracy}%` }}
                      />
                    </div>
                  </div>
                  <span
                    className={`text-xs font-semibold w-10 text-right ${
                      item.accuracy >= 80
                        ? "text-green-400"
                        : item.accuracy >= 50
                          ? "text-warning"
                          : "text-red-400"
                    }`}
                  >
                    {item.accuracy}%
                  </span>
                  <div className="w-5 flex justify-center">
                    {item.trend === "up" && (
                      <TrendingUp className="w-3.5 h-3.5 text-green-400" />
                    )}
                    {item.trend === "down" && (
                      <TrendingDown className="w-3.5 h-3.5 text-red-400" />
                    )}
                    {item.trend === "stable" && (
                      <div className="w-3 h-0.5 bg-[var(--color-text-muted)] rounded-full" />
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Target className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                    Focus Area
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    重点的に練習すべき音素
                  </p>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-red-500/5 border border-red-500/10">
                <p className="text-sm font-mono text-red-400 font-semibold">
                  /æ/ vs /ʌ/
                </p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                  正答率が45%と低下傾向です。cat/cut, bat/butなどのミニマルペアで練習しましょう。
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Trends タブ */}
        {activeTab === "trends" && (
          <div className="space-y-4">
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
              <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                Week-over-Week Changes
              </p>
              {TREND_DATA.map((trend) => {
                const delta = trend.current - trend.previous;
                const deltaPercent =
                  trend.previous > 0
                    ? Math.round((delta / trend.previous) * 100)
                    : 0;
                const isUp = delta > 0;
                const isDown = delta < 0;

                return (
                  <div
                    key={trend.label}
                    className="flex items-center justify-between p-3 rounded-xl bg-[var(--color-bg-primary)]/50"
                  >
                    <div>
                      <p className="text-sm font-medium text-[var(--color-text-primary)]">
                        {trend.label}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-[var(--color-text-muted)]">
                          {trend.previous}
                          {trend.unit}
                        </span>
                        <ArrowUpRight
                          className={`w-3 h-3 ${
                            isUp
                              ? "text-green-400"
                              : isDown
                                ? "text-red-400 rotate-90"
                                : "text-[var(--color-text-muted)]"
                          }`}
                        />
                        <span
                          className={`text-xs font-semibold ${
                            isUp
                              ? "text-green-400"
                              : isDown
                                ? "text-red-400"
                                : "text-[var(--color-text-muted)]"
                          }`}
                        >
                          {trend.current}
                          {trend.unit}
                        </span>
                      </div>
                    </div>
                    <div
                      className={`px-2 py-1 rounded-lg text-xs font-bold ${
                        isUp
                          ? "bg-green-500/10 text-green-400"
                          : isDown
                            ? "bg-red-500/10 text-red-400"
                            : "bg-[var(--color-bg-input)] text-[var(--color-text-muted)]"
                      }`}
                    >
                      {isUp ? "+" : ""}
                      {deltaPercent}%
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Recommendations タブ */}
        {activeTab === "recommendations" && (
          <div className="space-y-3">
            {RECOMMENDATIONS.map((rec, i) => (
              <RecommendationCard key={i} recommendation={rec} />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
