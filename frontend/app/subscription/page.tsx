"use client";

import { useState, useCallback } from "react";
import { ChevronDown } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import PlanCard from "@/components/subscription/PlanCard";
import { useApiData } from "@/lib/hooks/useApiData";
import { api } from "@/lib/api";
import type {
  PlanInfo as ApiPlanInfo,
  SubscriptionInfo,
} from "@/lib/api";
import { useToastStore } from "@/lib/stores/toast-store";
import { CardSkeleton } from "@/components/ui/Skeleton";

/**
 * サブスクリプション管理ページ
 * プラン比較 / 請求情報 / FAQ
 * APIからプラン・サブスク情報を取得し、失敗時はフォールバックデータを表示
 */

// PlanCardコンポーネントが期待するUI用プラン型
interface UIPlanInfo {
  id: string;
  name: string;
  nameJa: string;
  price: number;
  priceLabel: string;
  description: string;
  features: { text: string; included: boolean }[];
  popular?: boolean;
}

// フォールバック用ハードコードデータ
const FALLBACK_PLANS: UIPlanInfo[] = [
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

// プラン名の日本語マッピング
const PLAN_NAME_JA: Record<string, string> = {
  free: "フリー",
  starter: "スターター",
  standard: "スタンダード",
  premium: "プレミアム",
  enterprise: "エンタープライズ",
};

// プラン説明のマッピング
const PLAN_DESCRIPTION: Record<string, string> = {
  free: "英語学習を始めるための基本プラン",
  starter: "英語学習を始めるための入門プラン",
  standard: "本格的な英語力アップのための推奨プラン",
  premium: "企業向けの全機能アクセスプラン",
  enterprise: "大規模チーム向けのカスタムプラン",
};

/** API PlanInfo → UI PlanInfo に変換 */
function mapApiPlanToUIPlan(apiPlan: ApiPlanInfo): UIPlanInfo {
  const planId = apiPlan.id.toLowerCase();
  return {
    id: apiPlan.id,
    name: apiPlan.name,
    nameJa: PLAN_NAME_JA[planId] || apiPlan.name,
    price: apiPlan.price_monthly,
    priceLabel:
      apiPlan.price_monthly === 0
        ? "¥0/月"
        : `¥${apiPlan.price_monthly.toLocaleString()}/月`,
    description: PLAN_DESCRIPTION[planId] || `${apiPlan.name}プラン`,
    features: apiPlan.features.map((f) => ({
      text: f.description || f.name,
      included: f.included,
    })),
    popular: planId === "standard",
  };
}

/** 日付文字列をフォーマット */
function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export default function SubscriptionPage() {
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);
  const [isCheckoutLoading, setIsCheckoutLoading] = useState(false);
  const [isCancelLoading, setIsCancelLoading] = useState(false);
  const addToast = useToastStore((s) => s.addToast);

  // --- API データ取得 ---

  const {
    data: apiPlans,
    isLoading: plansLoading,
  } = useApiData<ApiPlanInfo[]>({
    fetcher: useCallback(() => api.getSubscriptionPlans(), []),
    fallback: undefined,
  });

  const {
    data: currentSubscription,
    isLoading: subLoading,
    refetch: refetchSubscription,
  } = useApiData<SubscriptionInfo>({
    fetcher: useCallback(() => api.getCurrentSubscription(), []),
    fallback: undefined,
  });

  // --- APIデータ → UI用データ変換（フォールバック付き） ---

  const plans: UIPlanInfo[] = apiPlans
    ? apiPlans.map(mapApiPlanToUIPlan)
    : FALLBACK_PLANS;

  // 現在のプランID（APIから取得、フォールバックは "free"）
  const currentPlanId = currentSubscription?.plan?.toLowerCase() ?? "free";

  // is_currentフラグがAPIプランにある場合はそちらを優先
  const getCurrentPlanId = (): string => {
    if (apiPlans) {
      const currentFromApi = apiPlans.find((p) => p.is_current);
      if (currentFromApi) return currentFromApi.id;
    }
    return currentPlanId;
  };

  const activePlanId = getCurrentPlanId();

  // --- イベントハンドラ ---

  const handleSelectPlan = async (planId: string) => {
    if (planId === activePlanId) return;

    // Freeプランへのダウングレードの場合はキャンセルフローへ
    if (planId === "free") {
      handleCancelSubscription();
      return;
    }

    setIsCheckoutLoading(true);
    try {
      const checkout = await api.createCheckout(planId);
      if (checkout.checkout_url) {
        window.location.href = checkout.checkout_url;
      } else {
        addToast("error", "チェックアウトURLの取得に失敗しました。");
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "プラン変更に失敗しました。";
      addToast("error", message);
    } finally {
      setIsCheckoutLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (isCancelLoading) return;

    setIsCancelLoading(true);
    try {
      const result = await api.cancelSubscription();
      if (result.success) {
        addToast("success", "サブスクリプションのキャンセルが完了しました。");
        refetchSubscription();
      } else {
        addToast("error", result.message || "キャンセルに失敗しました。");
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "キャンセルに失敗しました。";
      addToast("error", message);
    } finally {
      setIsCancelLoading(false);
    }
  };

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
  };

  const isLoading = plansLoading || subLoading;

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
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {plans.map((plan) => (
              <PlanCard
                key={plan.id}
                plan={plan}
                isCurrent={activePlanId === plan.id}
                onSelect={() => handleSelectPlan(plan.id)}
              />
            ))}
          </div>
        )}

        {/* チェックアウトローディングオーバーレイ */}
        {isCheckoutLoading && (
          <div className="text-center py-4">
            <p className="text-sm text-[var(--color-text-muted)] animate-pulse">
              チェックアウトページに移動中...
            </p>
          </div>
        )}

        {/* 請求情報（サブスクライブ中の場合） */}
        {activePlanId !== "free" && (
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
                  {currentSubscription
                    ? formatDate(currentSubscription.current_period_end)
                    : "March 14, 2026"}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[var(--color-bg-primary)]/50">
                <p className="text-xs text-[var(--color-text-muted)]">
                  Status
                </p>
                <p className="text-sm font-medium text-[var(--color-text-primary)] mt-0.5">
                  {currentSubscription?.cancel_at_period_end
                    ? "Cancelling at period end"
                    : currentSubscription?.status === "active"
                      ? "Active"
                      : currentSubscription?.status ?? "Active"}
                </p>
              </div>
            </div>
            {!currentSubscription?.cancel_at_period_end && (
              <button
                onClick={handleCancelSubscription}
                disabled={isCancelLoading}
                className={`px-4 py-2 rounded-xl border border-red-500/30 text-red-400 text-xs font-medium transition-colors ${
                  isCancelLoading
                    ? "opacity-50 cursor-not-allowed"
                    : "hover:bg-red-500/10"
                }`}
              >
                {isCancelLoading ? "Processing..." : "Cancel Subscription"}
              </button>
            )}
            {currentSubscription?.cancel_at_period_end && (
              <p className="text-xs text-[var(--color-text-muted)]">
                現在の期間終了後にキャンセルされます。
              </p>
            )}
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
