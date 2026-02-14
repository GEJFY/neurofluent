"use client";

import Link from "next/link";
import {
  Headphones,
  AudioWaveform,
  BookOpenCheck,
  ChevronRight,
  Lock,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";

/**
 * リスニングメニューページ
 * Speed Shadowing / もごもごイングリッシュ / Listening Comprehension
 */

interface ListeningMenuItem {
  id: string;
  title: string;
  titleJa: string;
  description: string;
  href: string;
  icon: React.ElementType;
  available: boolean;
}

const MENU_ITEMS: ListeningMenuItem[] = [
  {
    id: "shadowing",
    title: "Speed Shadowing",
    titleJa: "スピードシャドーイング",
    description:
      "ネイティブ音声を聞いて即座に真似る練習。発音・イントネーション・リズムを同時に鍛えます。",
    href: "/listening/shadowing",
    icon: AudioWaveform,
    available: true,
  },
  {
    id: "mogomogo",
    title: "Mogomogo English",
    titleJa: "もごもごイングリッシュ",
    description:
      "崩れた発音・リンキング・リダクションを聞き取る実践的リスニング。リアルな英語に慣れましょう。",
    href: "/listening/mogomogo",
    icon: Headphones,
    available: false,
  },
  {
    id: "comprehension",
    title: "Listening Comprehension",
    titleJa: "リスニング理解",
    description:
      "ビジネスシーンの音声を聞いて要約・質問に答える総合的なリスニング力トレーニング。",
    href: "/listening/comprehension",
    icon: BookOpenCheck,
    available: false,
  },
];

export default function ListeningPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="space-y-1">
          <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            Listening Training
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            リスニング力を多角的に鍛えるトレーニングメニュー
          </p>
        </div>

        {/* メニューカード一覧 */}
        <div className="space-y-3">
          {MENU_ITEMS.map((item) => {
            const Icon = item.icon;
            const content = (
              <div
                className={`flex items-center gap-4 p-5 bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl transition-colors group ${
                  item.available
                    ? "hover:border-primary/40 cursor-pointer"
                    : "opacity-50 cursor-not-allowed"
                }`}
              >
                {/* アイコン */}
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                    item.available
                      ? "bg-primary/10"
                      : "bg-[var(--color-bg-primary)]"
                  }`}
                >
                  <Icon
                    className={`w-6 h-6 ${
                      item.available
                        ? "text-primary"
                        : "text-[var(--color-text-muted)]"
                    }`}
                  />
                </div>

                {/* テキスト */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      {item.title}
                    </p>
                    {!item.available && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-warning/15 text-warning">
                        <Lock className="w-2.5 h-2.5" />
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                    {item.titleJa}
                  </p>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed line-clamp-2">
                    {item.description}
                  </p>
                </div>

                {/* 右矢印 */}
                <ChevronRight
                  className={`w-5 h-5 shrink-0 transition-colors ${
                    item.available
                      ? "text-[var(--color-text-muted)] group-hover:text-primary"
                      : "text-[var(--color-text-muted)]"
                  }`}
                />
              </div>
            );

            if (item.available) {
              return (
                <Link key={item.id} href={item.href}>
                  {content}
                </Link>
              );
            }

            return (
              <div key={item.id} aria-disabled="true">
                {content}
              </div>
            );
          })}
        </div>

        {/* 補足メッセージ */}
        <div className="text-center py-4">
          <p className="text-xs text-[var(--color-text-muted)]">
            Coming Soon のトレーニングは今後のアップデートで追加されます
          </p>
        </div>
      </div>
    </AppShell>
  );
}
