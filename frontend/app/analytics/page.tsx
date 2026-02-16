"use client";

import { useState, useCallback } from "react";
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
import { useApiData } from "@/lib/hooks/useApiData";
import { api } from "@/lib/api";
import type {
  DashboardData,
  WeeklyReport,
  SkillBreakdown,
  Recommendation,
  PronunciationOverallProgress,
} from "@/lib/api";
import { StatsSkeleton, CardSkeleton, ListSkeleton } from "@/components/ui/Skeleton";

/**
 * アナリティクスダッシュボードページ
 * 学習データの可視化と分析
 * APIからリアルデータを取得し、失敗時はフォールバックデータを表示
 */

type Period = "week" | "month";
type Tab = "overview" | "skills" | "pronunciation" | "trends" | "recommendations";

// フォールバック用デモデータ
const FALLBACK_WEEKLY_STATS = {
  minutes: 145,
  minutesDelta: 12,
  sessions: 18,
  sessionsDelta: 3,
  reviews: 62,
  reviewsDelta: -5,
  expressions: 34,
  expressionsDelta: 8,
};

const FALLBACK_MONTHLY_STATS = {
  minutes: 580,
  minutesDelta: 45,
  sessions: 72,
  sessionsDelta: 10,
  reviews: 248,
  reviewsDelta: 20,
  expressions: 136,
  expressionsDelta: 28,
};

const FALLBACK_SKILL_SCORES = {
  speaking: 72,
  listening: 65,
  vocabulary: 78,
  grammar: 68,
  pronunciation: 55,
};

const FALLBACK_WEEKLY_PROGRESS = [
  { date: "Mon", value: 25 },
  { date: "Tue", value: 18 },
  { date: "Wed", value: 32 },
  { date: "Thu", value: 15 },
  { date: "Fri", value: 28 },
  { date: "Sat", value: 12 },
  { date: "Sun", value: 15 },
];

const FALLBACK_MONTHLY_PROGRESS = [
  { date: "W1", value: 120 },
  { date: "W2", value: 145 },
  { date: "W3", value: 130 },
  { date: "W4", value: 185 },
];

const FALLBACK_PHONEME_PROGRESS = [
  { phoneme: "/r/-/l/", accuracy: 72, trend: "up" as const },
  { phoneme: "/θ/-/s/", accuracy: 58, trend: "up" as const },
  { phoneme: "/v/-/b/", accuracy: 85, trend: "stable" as const },
  { phoneme: "/f/-/h/", accuracy: 90, trend: "up" as const },
  { phoneme: "/æ/-/ʌ/", accuracy: 45, trend: "down" as const },
];

const FALLBACK_TREND_DATA = [
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

const FALLBACK_RECOMMENDATIONS = [
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

// --- APIレスポンスをUI用データにマッピングする関数群 ---

/** DashboardData → 週間/概要統計 */
function mapDashboardToStats(dashboard: DashboardData) {
  // recent_daily_statsから直近7日のサマリーを算出
  const recentStats = dashboard.recent_daily_stats || [];
  const totalMinutes = dashboard.total_practice_minutes;
  const totalSessions = dashboard.total_sessions;
  const totalReviews = dashboard.total_reviews_completed;
  const totalExpressions = dashboard.total_expressions_learned;

  return {
    minutes: totalMinutes,
    minutesDelta: 0, // ダッシュボードAPIにはdelta情報がないため0
    sessions: totalSessions,
    sessionsDelta: 0,
    reviews: totalReviews,
    reviewsDelta: 0,
    expressions: totalExpressions,
    expressionsDelta: 0,
    recentStats,
  };
}

/** WeeklyReport → 週間統計 + 日次進捗チャートデータ */
function mapWeeklyReportToStats(report: WeeklyReport) {
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const improvement = report.improvement_vs_last_week || {};

  const weeklyStats = {
    minutes: report.total_minutes,
    minutesDelta: improvement.total_minutes ?? 0,
    sessions: report.total_sessions,
    sessionsDelta: improvement.total_sessions ?? 0,
    reviews: report.total_reviews,
    reviewsDelta: improvement.total_reviews ?? 0,
    expressions: report.new_expressions,
    expressionsDelta: improvement.new_expressions ?? 0,
  };

  const weeklyProgress = (report.daily_breakdown || []).map((day) => {
    const d = new Date(day.date);
    return {
      date: dayNames[d.getDay()] || day.date,
      value: day.practice_minutes,
    };
  });

  return { weeklyStats, weeklyProgress };
}

/** SkillBreakdown → スキルスコア (0-100) */
function mapSkillBreakdownToScores(skills: SkillBreakdown) {
  // speaking: grammar accuracyをベースに
  const speakingScore = skills.speaking?.grammar?.accuracy ?? 0;
  // listening: 通常速度の理解度をベースに
  const listeningScore = skills.listening?.comprehension_by_speed?.normal ?? 0;
  // vocabulary: sophistication scoreをベースに
  const vocabularyScore = skills.vocabulary?.sophistication?.score ?? 0;
  // grammar: speakingのgrammar accuracy
  const grammarScore = skills.speaking?.grammar?.accuracy ?? 0;
  // pronunciation: 手動スコアは別APIなのでデフォルト値
  const pronunciationScore = 55;

  return {
    speaking: Math.round(speakingScore),
    listening: Math.round(listeningScore),
    vocabulary: Math.round(vocabularyScore),
    grammar: Math.round(grammarScore),
    pronunciation: pronunciationScore,
  };
}

/** WeeklyReport → トレンドデータ */
function mapWeeklyReportToTrends(report: WeeklyReport) {
  const improvement = report.improvement_vs_last_week || {};
  const grammarAcc = report.avg_grammar_accuracy ?? 0;
  const pronScore = report.avg_pronunciation ?? 0;

  // improvement_vs_last_weekから前週値を逆算
  return [
    {
      label: "Grammar Accuracy",
      current: Math.round(grammarAcc),
      previous: Math.round(grammarAcc - (improvement.avg_grammar_accuracy ?? 0)),
      unit: "%",
    },
    {
      label: "Pronunciation Score",
      current: Math.round(pronScore),
      previous: Math.round(pronScore - (improvement.avg_pronunciation ?? 0)),
      unit: "%",
    },
    {
      label: "Total Sessions",
      current: report.total_sessions,
      previous: report.total_sessions - (improvement.total_sessions ?? 0),
      unit: "",
    },
    {
      label: "Practice Time",
      current: report.total_minutes,
      previous: report.total_minutes - (improvement.total_minutes ?? 0),
      unit: "min",
    },
    {
      label: "New Expressions",
      current: report.new_expressions,
      previous: report.new_expressions - (improvement.new_expressions ?? 0),
      unit: "",
    },
  ];
}

/** Recommendation[] → UI用レコメンド (priorityをnumber→stringにマッピング) */
function mapRecommendations(
  recs: Recommendation[]
): { category: string; title: string; description: string; priority: string; exercise_type: string }[] {
  return recs.map((rec) => ({
    category: rec.category,
    title: rec.title,
    description: rec.description,
    priority:
      rec.priority <= 1 ? "high" : rec.priority <= 3 ? "medium" : "low",
    exercise_type: rec.suggested_exercise_type,
  }));
}

/** PronunciationOverallProgress → 音素進捗データ */
function mapPronunciationProgress(
  progress: PronunciationOverallProgress
): { phoneme: string; accuracy: number; trend: "up" | "down" | "stable" }[] {
  return (progress.phoneme_progress || []).map((p) => ({
    phoneme: p.phoneme,
    accuracy: Math.round(p.accuracy),
    trend: (p.trend === "up" || p.trend === "down" || p.trend === "stable"
      ? p.trend
      : "stable") as "up" | "down" | "stable",
  }));
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>("week");
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  // --- API データ取得 ---

  const {
    data: dashboardData,
    isLoading: dashboardLoading,
  } = useApiData<DashboardData>({
    fetcher: useCallback(() => api.getDashboard(), []),
    fallback: undefined,
  });

  const {
    data: weeklyReport,
    isLoading: weeklyLoading,
  } = useApiData<WeeklyReport>({
    fetcher: useCallback(() => api.getWeeklyReport(), []),
    fallback: undefined,
  });

  const {
    data: skillBreakdown,
    isLoading: skillsLoading,
  } = useApiData<SkillBreakdown>({
    fetcher: useCallback(() => api.getSkillBreakdown(), []),
    fallback: undefined,
  });

  const {
    data: apiRecommendations,
    isLoading: recsLoading,
  } = useApiData<Recommendation[]>({
    fetcher: useCallback(() => api.getRecommendations(), []),
    fallback: undefined,
  });

  const {
    data: pronunciationData,
    isLoading: pronLoading,
  } = useApiData<PronunciationOverallProgress>({
    fetcher: useCallback(() => api.getPronunciationProgress(), []),
    fallback: undefined,
  });

  // --- APIデータ → UI用データ変換（フォールバック付き） ---

  // Overview: 週間統計
  const weeklyMapped = weeklyReport ? mapWeeklyReportToStats(weeklyReport) : null;
  const weeklyStats = weeklyMapped?.weeklyStats ?? FALLBACK_WEEKLY_STATS;
  const weeklyProgress = weeklyMapped?.weeklyProgress?.length
    ? weeklyMapped.weeklyProgress
    : FALLBACK_WEEKLY_PROGRESS;

  // Overview: 月間統計 (dashboardDataから生成、なければフォールバック)
  const monthlyStats = dashboardData
    ? {
        minutes: dashboardData.total_practice_minutes,
        minutesDelta: 0,
        sessions: dashboardData.total_sessions,
        sessionsDelta: 0,
        reviews: dashboardData.total_reviews_completed,
        reviewsDelta: 0,
        expressions: dashboardData.total_expressions_learned,
        expressionsDelta: 0,
      }
    : FALLBACK_MONTHLY_STATS;

  const monthlyProgress = FALLBACK_MONTHLY_PROGRESS; // 月次内訳はweekly APIに含まれないためフォールバック

  const stats = period === "week" ? weeklyStats : monthlyStats;
  const progressData = period === "week" ? weeklyProgress : monthlyProgress;

  // Skills: スキルスコア
  const skillScores = skillBreakdown
    ? mapSkillBreakdownToScores(skillBreakdown)
    : FALLBACK_SKILL_SCORES;

  // Pronunciation: 音素進捗
  const phonemeProgress = pronunciationData
    ? mapPronunciationProgress(pronunciationData)
    : FALLBACK_PHONEME_PROGRESS;

  // 最も弱い音素をフォーカスエリアとして表示
  const weakestPhoneme = pronunciationData?.weakest_phonemes?.[0] ?? "/æ/-/ʌ/";
  const weakestPhonemeData = phonemeProgress.reduce(
    (lowest, p) => (p.accuracy < lowest.accuracy ? p : lowest),
    phonemeProgress[0] || { phoneme: "/æ/-/ʌ/", accuracy: 45, trend: "down" as const }
  );

  // Trends: トレンドデータ
  const trendData = weeklyReport
    ? mapWeeklyReportToTrends(weeklyReport)
    : FALLBACK_TREND_DATA;

  // Recommendations: レコメンドデータ
  const recommendations = apiRecommendations
    ? mapRecommendations(apiRecommendations)
    : FALLBACK_RECOMMENDATIONS;

  // ローディング状態の判定
  const isOverviewLoading = dashboardLoading || weeklyLoading;
  const isSkillsLoading = skillsLoading;
  const isPronunciationLoading = pronLoading;
  const isTrendsLoading = weeklyLoading;
  const isRecsLoading = recsLoading;

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
            {isOverviewLoading ? (
              <>
                <StatsSkeleton count={4} />
                <CardSkeleton />
              </>
            ) : (
              <>
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
              </>
            )}
          </div>
        )}

        {/* Skills タブ */}
        {activeTab === "skills" && (
          <div className="space-y-6">
            {isSkillsLoading ? (
              <>
                <CardSkeleton />
                <ListSkeleton rows={5} />
              </>
            ) : (
              <>
                <SkillRadar skills={skillScores} />

                {/* スキル詳細バー */}
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
                  <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                    Skill Breakdown
                  </p>
                  {Object.entries(skillScores).map(([skill, score]) => (
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
              </>
            )}
          </div>
        )}

        {/* Pronunciation タブ */}
        {activeTab === "pronunciation" && (
          <div className="space-y-4">
            {isPronunciationLoading ? (
              <>
                <ListSkeleton rows={5} />
                <CardSkeleton />
              </>
            ) : (
              <>
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
                  <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                    Phoneme Progress
                  </p>
                  {phonemeProgress.map((item) => (
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
                      {weakestPhonemeData.phoneme}
                    </p>
                    <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                      正答率が{weakestPhonemeData.accuracy}%
                      {weakestPhonemeData.trend === "down" ? "と低下傾向です" : "です"}。
                      集中的な練習をお勧めします。
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Trends タブ */}
        {activeTab === "trends" && (
          <div className="space-y-4">
            {isTrendsLoading ? (
              <ListSkeleton rows={5} />
            ) : (
              <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Week-over-Week Changes
                </p>
                {trendData.map((trend) => {
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
            )}
          </div>
        )}

        {/* Recommendations タブ */}
        {activeTab === "recommendations" && (
          <div className="space-y-3">
            {isRecsLoading ? (
              <ListSkeleton rows={3} />
            ) : (
              recommendations.map((rec, i) => (
                <RecommendationCard key={i} recommendation={rec} />
              ))
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
