"use client";

import { create } from "zustand";
import { api, type User, type ApiError } from "@/lib/api";

/**
 * 認証ストア
 * ユーザー情報・トークン管理、ログイン・ログアウト処理
 */

interface AuthState {
  user: User | null;
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;

  /** 初期化：localStorageからトークン復元＋ユーザー情報取得 */
  initialize: () => Promise<void>;

  /** ログイン */
  login: (email: string, password: string) => Promise<void>;

  /** ユーザー登録 */
  register: (email: string, password: string, name: string) => Promise<void>;

  /** ログアウト */
  logout: () => void;

  /** エラークリア */
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isInitialized: false,
  isLoading: false,
  error: null,

  initialize: async () => {
    if (get().isInitialized) return;

    const storedToken =
      typeof window !== "undefined"
        ? localStorage.getItem("fluentedge_token")
        : null;

    if (!storedToken) {
      set({ isInitialized: true });
      return;
    }

    try {
      const user = await api.getMe();
      set({ user, isInitialized: true });
    } catch {
      // トークンが無効な場合はクリア
      api.clearToken();
      set({ user: null, isInitialized: true });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.login(email, password);
      // トークン保存後、ユーザー情報を取得
      const user = await api.getMe();
      set({ user, isLoading: false });
    } catch (err) {
      const apiErr = err as ApiError;
      set({
        isLoading: false,
        error: apiErr.detail || "ログインに失敗しました",
      });
      throw err;
    }
  },

  register: async (email: string, password: string, name: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.register(email, password, name);
      // トークン保存後、ユーザー情報を取得
      const user = await api.getMe();
      set({ user, isLoading: false });
    } catch (err) {
      const apiErr = err as ApiError;
      set({
        isLoading: false,
        error: apiErr.detail || "登録に失敗しました",
      });
      throw err;
    }
  },

  logout: () => {
    api.clearToken();
    set({ user: null, error: null });
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  },

  clearError: () => set({ error: null }),
}));
