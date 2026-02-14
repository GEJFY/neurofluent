"use client";

import { Check, X, Crown, Star } from "lucide-react";

/**
 * プランカード
 * サブスクリプションプランの表示カード
 */

interface PlanInfo {
  id: string;
  name: string;
  nameJa: string;
  price: number;
  priceLabel: string;
  description: string;
  features: { text: string; included: boolean }[];
  popular?: boolean;
}

interface PlanCardProps {
  plan: PlanInfo;
  isCurrent: boolean;
  onSelect: () => void;
}

export default function PlanCard({ plan, isCurrent, onSelect }: PlanCardProps) {
  return (
    <div
      className={`relative bg-[var(--color-bg-card)] border rounded-2xl p-5 flex flex-col transition-colors ${
        isCurrent
          ? "border-primary ring-1 ring-primary/30"
          : plan.popular
            ? "border-warning/40"
            : "border-[var(--color-border)]"
      }`}
    >
      {/* バッジ */}
      {isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[10px] font-bold bg-primary text-white">
            <Star className="w-3 h-3" />
            Current Plan
          </span>
        </div>
      )}
      {plan.popular && !isCurrent && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[10px] font-bold bg-warning text-black">
            <Crown className="w-3 h-3" />
            Most Popular
          </span>
        </div>
      )}

      {/* プラン名 */}
      <div className="text-center pt-2 mb-4">
        <p className="text-lg font-heading font-bold text-[var(--color-text-primary)]">
          {plan.name}
        </p>
        <p className="text-xs text-[var(--color-text-muted)]">{plan.nameJa}</p>
      </div>

      {/* 価格 */}
      <div className="text-center mb-4">
        <p className="text-3xl font-heading font-bold text-[var(--color-text-primary)]">
          {plan.price === 0 ? (
            "Free"
          ) : (
            <>
              <span className="text-base align-top">¥</span>
              {plan.price.toLocaleString()}
            </>
          )}
        </p>
        {plan.price > 0 && (
          <p className="text-xs text-[var(--color-text-muted)]">/月 (税込)</p>
        )}
      </div>

      {/* 説明 */}
      <p className="text-xs text-[var(--color-text-secondary)] text-center mb-5 leading-relaxed">
        {plan.description}
      </p>

      {/* 機能一覧 */}
      <div className="flex-1 space-y-2 mb-5">
        {plan.features.map((feature, i) => (
          <div key={i} className="flex items-center gap-2">
            {feature.included ? (
              <Check className="w-4 h-4 text-green-400 shrink-0" />
            ) : (
              <X className="w-4 h-4 text-[var(--color-text-muted)] shrink-0 opacity-40" />
            )}
            <span
              className={`text-xs ${
                feature.included
                  ? "text-[var(--color-text-secondary)]"
                  : "text-[var(--color-text-muted)] opacity-50"
              }`}
            >
              {feature.text}
            </span>
          </div>
        ))}
      </div>

      {/* CTAボタン */}
      <button
        onClick={onSelect}
        disabled={isCurrent}
        className={`w-full py-3 rounded-xl text-sm font-semibold transition-colors ${
          isCurrent
            ? "bg-[var(--color-bg-input)] text-[var(--color-text-muted)] cursor-not-allowed"
            : plan.popular
              ? "bg-primary text-white hover:bg-primary-500"
              : "bg-[var(--color-bg-input)] border border-[var(--color-border)] text-[var(--color-text-primary)] hover:border-primary/30 hover:text-primary"
        }`}
      >
        {isCurrent
          ? "Current Plan"
          : plan.price === 0
            ? "Get Started"
            : "Upgrade Now"}
      </button>
    </div>
  );
}
