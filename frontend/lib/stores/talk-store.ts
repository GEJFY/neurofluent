"use client";

import { create } from "zustand";
import {
  api,
  type TalkMessageResponse,
  type SessionResponse,
  type ApiError,
} from "@/lib/api";

/**
 * トークストア
 * チャットメッセージ・セッション管理
 */

interface TalkState {
  currentSession: SessionResponse | null;
  messages: TalkMessageResponse[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;

  /** 新しいトークセッション開始 */
  startSession: (mode?: string, scenarioId?: string) => Promise<void>;

  /** メッセージ送信 */
  sendMessage: (content: string) => Promise<void>;

  /** 既存セッション読み込み */
  loadSession: (sessionId: string) => Promise<void>;

  /** ストアリセット */
  reset: () => void;

  /** エラークリア */
  clearError: () => void;
}

export const useTalkStore = create<TalkState>((set, get) => ({
  currentSession: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,

  startSession: async (mode: string = "casual_chat", scenarioId?: string) => {
    set({ isLoading: true, error: null, messages: [] });
    try {
      const session = await api.startTalk(mode, undefined, scenarioId);
      set({
        currentSession: session,
        messages: session.messages,
        isLoading: false,
      });
    } catch (err) {
      const apiErr = err as ApiError;
      set({
        isLoading: false,
        error: apiErr.detail || "セッションの開始に失敗しました",
      });
    }
  },

  sendMessage: async (content: string) => {
    const { currentSession, messages } = get();
    if (!currentSession) return;

    // ユーザーメッセージを楽観的に追加
    const userMessage: TalkMessageResponse = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      feedback: null,
      created_at: new Date().toISOString(),
    };

    set({ messages: [...messages, userMessage], isSending: true, error: null });

    try {
      // APIからAIレスポンス取得（フィードバック付き）
      const aiResponse = await api.sendMessage(currentSession.id, content);

      set((state) => ({
        messages: [...state.messages, aiResponse],
        isSending: false,
      }));
    } catch (err) {
      const apiErr = err as ApiError;
      set({
        isSending: false,
        error: apiErr.detail || "メッセージの送信に失敗しました",
      });
    }
  },

  loadSession: async (sessionId: string) => {
    set({ isLoading: true, error: null });
    try {
      const sessionData = await api.getSession(sessionId);
      set({
        currentSession: sessionData,
        messages: sessionData.messages,
        isLoading: false,
      });
    } catch (err) {
      const apiErr = err as ApiError;
      set({
        isLoading: false,
        error: apiErr.detail || "セッションの読み込みに失敗しました",
      });
    }
  },

  reset: () => {
    set({
      currentSession: null,
      messages: [],
      isLoading: false,
      isSending: false,
      error: null,
    });
  },

  clearError: () => set({ error: null }),
}));
