"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";
import { useAuthStore } from "@/lib/stores/auth-store";

/**
 * AppShell - アプリケーション全体のレイアウトラッパー
 * サイドバー（デスクトップ）+ ボトムナビ（モバイル）+ メインコンテンツ
 * 認証チェック付き
 */
export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isInitialized, initialize } = useAuthStore();

  // 初期化：localStorageからトークン復元
  useEffect(() => {
    initialize();
  }, [initialize]);

  // 未認証ならログインページへリダイレクト
  useEffect(() => {
    if (isInitialized && !user && pathname !== "/login") {
      router.replace("/login");
    }
  }, [isInitialized, user, pathname, router]);

  // ログインページの場合はシェルなしで表示
  if (pathname === "/login") {
    return <>{children}</>;
  }

  // 初期化中のローディング表示
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-primary)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-3 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-[var(--color-text-muted)]">読み込み中...</p>
        </div>
      </div>
    );
  }

  // 未認証でリダイレクト待ちの場合
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-primary)]">
      <Sidebar />
      {/* メインコンテンツエリア */}
      <main className="md:ml-64 min-h-screen pb-20 md:pb-0">
        <div className="max-w-7xl mx-auto px-5 py-6 md:px-8 md:py-10 lg:px-12 xl:px-16">
          {children}
        </div>
      </main>
      <BottomNav />
    </div>
  );
}
