"use client";

import Link from "next/link";
import {
  Zap,
  Repeat2,
  AudioLines,
  ChevronRight,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";

/**
 * スピーキングメニューページ
 * Flash Translation / Pattern Practice / Pronunciation Training
 */

interface SpeakingMenuItem {
  id: string;
  title: string;
  titleJa: string;
  description: string;
  href: string;
  icon: React.ElementType;
  available: boolean;
  isNew?: boolean;
}

const MENU_ITEMS: SpeakingMenuItem[] = [
  {
    id: "flash",
    title: "Flash Translation",
    titleJa: "瞬間英作文",
    description:
      "日本語を見て瞬時に英訳する練習。反射的に英語が出てくる力を鍛えます。",
    href: "/speaking/flash",
    icon: Zap,
    available: true,
  },
  {
    id: "pattern",
    title: "Pattern Practice",
    titleJa: "パターンプラクティス",
    description:
      "ビジネスでよく使うフレーズパターンを繰り返し練習。定型表現を体に染み込ませます。",
    href: "/speaking/pattern",
    icon: Repeat2,
    available: true,
    isNew: true,
  },
  {
    id: "pronunciation",
    title: "Pronunciation Training",
    titleJa: "発音トレーニング",
    description:
      "音素レベルで発音を矯正。リンキング・リダクション・イントネーションを集中的に練習します。",
    href: "/speaking/pronunciation",
    icon: AudioLines,
    available: true,
  },
];

export default function SpeakingPage() {
  return (
    <AppShell>
      <div className="space-y-8">
        {/* ヘッダー */}
        <div className="space-y-2">
          <h1 className="text-2xl md:text-3xl font-heading font-bold text-[var(--color-text-primary)] leading-tight">
            Speaking Drills
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
            アウトプット力を鍛えるスピーキング練習メニュー
          </p>
        </div>

        {/* メニューカード一覧 */}
        <div className="space-y-3 lg:grid lg:grid-cols-2 lg:gap-4 lg:space-y-0">
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
                      ? item.isNew
                        ? "bg-accent/10"
                        : "bg-primary/10"
                      : "bg-[var(--color-bg-primary)]"
                  }`}
                >
                  <Icon
                    className={`w-6 h-6 ${
                      item.available
                        ? item.isNew
                          ? "text-accent"
                          : "text-primary"
                        : "text-[var(--color-text-muted)]"
                    }`}
                  />
                </div>

                {/* テキスト */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      {item.title}
                    </p>
                    {item.isNew && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-accent/15 text-accent">
                        NEW
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
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

      </div>
    </AppShell>
  );
}
