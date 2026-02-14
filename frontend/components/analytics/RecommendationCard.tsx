"use client";

import Link from "next/link";
import { ChevronRight, Mic, Headphones, MessageCircle, BookOpen } from "lucide-react";

/**
 * レコメンドカード
 * AI推薦の学習エクササイズカード
 */

interface Recommendation {
  category: string;
  title: string;
  description: string;
  priority: string;
  exercise_type: string;
}

interface RecommendationCardProps {
  recommendation: Recommendation;
}

const CATEGORY_CONFIG: Record<
  string,
  { color: string; bgColor: string; borderColor: string; icon: React.ElementType }
> = {
  pronunciation: {
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/20",
    icon: Mic,
  },
  listening: {
    color: "text-accent",
    bgColor: "bg-accent/10",
    borderColor: "border-accent/20",
    icon: Headphones,
  },
  speaking: {
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/20",
    icon: MessageCircle,
  },
  vocabulary: {
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/20",
    icon: BookOpen,
  },
  grammar: {
    color: "text-warning",
    bgColor: "bg-warning/10",
    borderColor: "border-warning/20",
    icon: BookOpen,
  },
};

const PRIORITY_CONFIG: Record<string, { color: string; bgColor: string; label: string }> = {
  high: { color: "text-red-400", bgColor: "bg-red-500/10", label: "High" },
  medium: { color: "text-warning", bgColor: "bg-warning/10", label: "Medium" },
  low: { color: "text-green-400", bgColor: "bg-green-500/10", label: "Low" },
};

const EXERCISE_HREF: Record<string, string> = {
  pronunciation: "/speaking/pronunciation",
  mogomogo: "/listening/mogomogo",
  talk: "/talk",
  flash: "/speaking/flash",
  review: "/review",
  comprehension: "/listening/comprehension",
};

export default function RecommendationCard({
  recommendation,
}: RecommendationCardProps) {
  const categoryConfig = CATEGORY_CONFIG[recommendation.category] || {
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/20",
    icon: BookOpen,
  };
  const priorityConfig = PRIORITY_CONFIG[recommendation.priority] || PRIORITY_CONFIG.medium;
  const href = EXERCISE_HREF[recommendation.exercise_type] || "/";
  const CategoryIcon = categoryConfig.icon;

  return (
    <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
      {/* ヘッダー：カテゴリバッジ + 優先度 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-lg ${categoryConfig.bgColor} flex items-center justify-center`}
          >
            <CategoryIcon className={`w-4 h-4 ${categoryConfig.color}`} />
          </div>
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${categoryConfig.bgColor} ${categoryConfig.color}`}
          >
            {recommendation.category}
          </span>
        </div>
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${priorityConfig.bgColor} ${priorityConfig.color}`}
        >
          {priorityConfig.label}
        </span>
      </div>

      {/* タイトルと説明 */}
      <div>
        <p className="text-sm font-semibold text-[var(--color-text-primary)]">
          {recommendation.title}
        </p>
        <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed">
          {recommendation.description}
        </p>
      </div>

      {/* 開始ボタン */}
      <Link
        href={href}
        className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-primary/10 text-primary text-xs font-semibold hover:bg-primary/20 transition-colors"
      >
        Start Practice
        <ChevronRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
}
