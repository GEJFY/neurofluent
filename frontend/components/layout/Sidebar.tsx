"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageCircle,
  Zap,
  RotateCcw,
  Headphones,
  Mic,
  BarChart3,
  Settings,
  Sun,
  Moon,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useState, useEffect } from "react";

/** ナビゲーションリンク定義 */
const navLinks = [
  { href: "/", label: "Dashboard", labelJa: "ダッシュボード", icon: LayoutDashboard },
  { href: "/talk", label: "Talk", labelJa: "AIトーク", icon: MessageCircle },
  { href: "/listening", label: "Listening", labelJa: "リスニング", icon: Headphones },
  { href: "/speaking", label: "Speaking", labelJa: "スピーキング", icon: Mic },
  { href: "/review", label: "Review", labelJa: "復習", icon: RotateCcw },
  { href: "/analytics", label: "Analytics", labelJa: "分析", icon: BarChart3 },
  { href: "/settings", label: "Settings", labelJa: "設定", icon: Settings },
];

/**
 * デスクトップサイドバーナビゲーション
 * md以上の画面で表示
 */
export default function Sidebar() {
  const pathname = usePathname();
  const logout = useAuthStore((s) => s.logout);
  const [isDark, setIsDark] = useState(true);

  // テーマ切り替え
  useEffect(() => {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
  }, [isDark]);

  return (
    <aside className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 z-40 bg-[var(--color-bg-secondary)] border-r border-[var(--color-border)]">
      {/* ロゴエリア */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-[var(--color-border)]">
        <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-heading text-lg font-bold text-[var(--color-text-primary)]">
            FluentEdge
          </h1>
          <p className="text-xs text-[var(--color-text-muted)]">AI English Training</p>
        </div>
      </div>

      {/* ナビゲーションリンク */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navLinks.map((link) => {
          const isActive = pathname === link.href;
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-primary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              <Icon className="w-5 h-5" />
              <div>
                <span className="block">{link.label}</span>
                <span className="block text-xs text-[var(--color-text-muted)]">
                  {link.labelJa}
                </span>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* フッター：テーマ切り替え＋ログアウト */}
      <div className="px-3 py-4 border-t border-[var(--color-border)] space-y-1">
        <button
          onClick={() => setIsDark(!isDark)}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-primary)] hover:text-[var(--color-text-primary)] w-full"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          <span>{isDark ? "ライトモード" : "ダークモード"}</span>
        </button>
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm text-[var(--color-text-secondary)] hover:bg-red-500/10 hover:text-red-400 w-full"
        >
          <LogOut className="w-5 h-5" />
          <span>ログアウト</span>
        </button>
      </div>
    </aside>
  );
}
