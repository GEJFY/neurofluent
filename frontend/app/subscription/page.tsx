"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import PlanCard from "@/components/subscription/PlanCard";

/**
 * サブスクリプション管理ページ
 * プラン比較 / 請求情報 / FAQ
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

const PLANS: PlanInfo[] = [
  {
    id: "free",
    name: "Free",
    nameJa: "フリー",
    price: 0,
    priceLabel: "¥0/月",
    description: "英語学習を始めるための基本プラン",
    features: [
      { text: "1日5セッションまで", included: true },
      { text: "Casual Chatモード", included: true },
      { text: "Flash Translation (基本)", included: true },
      { text: "間隔反復レビュー", included: true },
      { text: "基本アナリティクス", included: true },
      { text: "全会話モード", included: false },
      { text: "Pronunciation Training", included: false },
      { text: "もごもごイングリッシュ", included: false },
      { text: "詳細レポート", included: false },
      { text: "優先サポート", included: false },
      { text: "API アクセス", included: false },
    ],
  },
  {
    id: "standard",
    name: "Standard",
    nameJa: "スタンダード",
    price: 1480,
    priceLabel: "¥1,480/月",
    description: "本格的な英語力アップのための推奨プラン",
    popular: true,
    features: [
      { text: "無制限セッション", included: true },
      { text: "全6つの会話モード", included: true },
      { text: "Flash Translation (全レベル)", included: true },
      { text: "間隔反復レビュー", included: true },
      { text: "詳細アナリティクス", included: true },
      { text: "Pronunciation Training", included: true },
      { text: "もごもごイングリッシュ", included: true },
      { text: "週次/月次レポート", included: true },
      { text: "優先サポート", included: true },
      { text: "API アクセス", included: false },
      { text: "チーム管理機能", included: false },
    ],
  },
  {
    id: "premium",
    name: "Premium",
    nameJa: "プレミアム",
    price: 2980,
    priceLabel: "¥2,980/月",
    description: "企業向けの全機能アクセスプラン",
    features: [
      { text: "無制限セッション", included: true },
      { text: "全6つの会話モード", included: true },
      { text: "Flash Translation (全レベル)", included: true },
      { text: "間隔反復レビュー", included: true },
      { text: "詳細アナリティクス", included: true },
      { text: "Pronunciation Training", included: true },
      { text: "もごもごイングリッシュ", included: true },
      { text: "週次/月次レポート", included: true },
      { text: "優先サポート", included: true },
      { text: "API アクセス", included: true },
      { text: "チーム管理機能", included: true },
    ],
  },
];

const FAQ_ITEMS = [
  {
    question: "プランはいつでも変更できますか？",
    answer:
      "はい、いつでもプランをアップグレードまたはダウングレードできます。アップグレードの場合は即座に適用され、差額が日割りで請求されます。ダウングレードは次の請求日から適用されます。",
  },
  {
    question: "無料トライアルはありますか？",
    answer:
      "Standardプランの7日間無料トライアルをご利用いただけます。トライアル期間中はいつでもキャンセル可能で、料金は発生しません。",
  },
  {
    question: "支払い方法は何が使えますか？",
    answer:
      "クレジットカード（Visa, Mastercard, AMEX, JCB）、デビットカード、およびPayPalに対応しています。",
  },
  {
    question: "解約するとデータはどうなりますか？",
    answer:
      "解約後もデータは30日間保持されます。この期間内に再加入すれば、すべての学習データが復元されます。30日を過ぎるとデータは完全に削除されます。",
  },
  {
    question: "法人契約は可能ですか？",
    answer:
      "はい、Premiumプランでは法人契約やチーム管理機能をご利用いただけます。詳細はお問い合わせください。",
  },
];

export default function SubscriptionPage() {
  const [currentPlan] = useState("free");
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  const handleSelectPlan = (planId: string) => {
    // デモ：プラン選択処理
    console.log("Selected plan:", planId);
  };

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
  };

  return (
    <AppShell>
      <div className="space-y-8">
        {/* ヘッダー */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            Subscription Plans
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            あなたの学習スタイルに合ったプランを選びましょう
          </p>
        </div>

        {/* プランカード */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {PLANS.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              isCurrent={currentPlan === plan.id}
              onSelect={() => handleSelectPlan(plan.id)}
            />
          ))}
        </div>

        {/* 請求情報（サブスクライブ中の場合） */}
        {currentPlan !== "free" && (
          <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
            <p className="text-sm font-semibold text-[var(--color-text-primary)]">
              Billing Information
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
                <p className="text-xs text-[var(--color-text-muted)]">
                  Next Billing Date
                </p>
                <p className="text-sm font-medium text-[var(--color-text-primary)] mt-0.5">
                  March 14, 2026
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
                <p className="text-xs text-[var(--color-text-muted)]">
                  Payment Method
                </p>
                <p className="text-sm font-medium text-[var(--color-text-primary)] mt-0.5">
                  **** **** **** 4242
                </p>
              </div>
            </div>
            <button className="px-4 py-2 rounded-xl border border-red-500/30 text-red-400 text-xs font-medium hover:bg-red-500/10 transition-colors">
              Cancel Subscription
            </button>
          </div>
        )}

        {/* FAQ */}
        <div className="space-y-3">
          <h2 className="text-lg font-heading font-bold text-[var(--color-text-primary)]">
            Frequently Asked Questions
          </h2>
          <div className="space-y-2">
            {FAQ_ITEMS.map((item, index) => (
              <div
                key={index}
                className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => toggleFaq(index)}
                  className="w-full flex items-center justify-between p-4 text-left"
                >
                  <span className="text-sm font-medium text-[var(--color-text-primary)]">
                    {item.question}
                  </span>
                  <ChevronDown
                    className={`w-4 h-4 text-[var(--color-text-muted)] transition-transform shrink-0 ml-2 ${
                      openFaqIndex === index ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {openFaqIndex === index && (
                  <div className="px-4 pb-4">
                    <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed">
                      {item.answer}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
