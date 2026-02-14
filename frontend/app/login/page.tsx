"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap, Mail, Lock, User, Loader2 } from "lucide-react";
import { useAuthStore } from "@/lib/stores/auth-store";

/**
 * ログイン/登録ページ
 * メールアドレス + パスワードのシンプルなフォーム
 */
export default function LoginPage() {
  const router = useRouter();
  const { login, register, isLoading, error, clearError } = useAuthStore();

  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      if (isRegister) {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
      router.replace("/");
    } catch {
      // エラーはストアで管理される
    }
  };

  const toggleMode = () => {
    setIsRegister(!isRegister);
    clearError();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-primary)] px-4">
      <div className="w-full max-w-sm space-y-8">
        {/* ロゴ・タイトル */}
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-primary flex items-center justify-center mx-auto">
            <Zap className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
              FluentEdge AI
            </h1>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              AI英語トレーニング
            </p>
          </div>
        </div>

        {/* フォーム */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 登録時: 表示名 */}
          {isRegister && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--color-text-secondary)]">
                表示名
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  required={isRegister}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                />
              </div>
            </div>
          )}

          {/* メールアドレス */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[var(--color-text-secondary)]">
              メールアドレス
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>
          </div>

          {/* パスワード */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[var(--color-text-secondary)]">
              パスワード
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>
          </div>

          {/* エラーメッセージ */}
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400">
              {error}
            </div>
          )}

          {/* 送信ボタン */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            {isRegister ? "アカウント作成" : "ログイン"}
          </button>
        </form>

        {/* モード切り替えリンク */}
        <p className="text-center text-sm text-[var(--color-text-muted)]">
          {isRegister ? "既にアカウントをお持ちですか？" : "アカウントをお持ちでないですか？"}{" "}
          <button
            onClick={toggleMode}
            className="text-primary hover:underline font-medium"
          >
            {isRegister ? "ログイン" : "新規登録"}
          </button>
        </p>
      </div>
    </div>
  );
}
