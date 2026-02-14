"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send, Loader2, MessageCircle } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import ChatWindow from "@/components/chat/ChatWindow";
import { useTalkStore } from "@/lib/stores/talk-store";

/**
 * AI Free Talk ページ
 * - モードセレクター（MVP: Casual Chat のみ）
 * - チャットウィンドウ
 * - テキスト入力 + 送信ボタン
 */

const TALK_MODES = [
  { id: "casual_chat", label: "Casual Chat", description: "自由に英会話を楽しもう" },
  { id: "business", label: "Business", description: "ビジネス英語の練習", disabled: true },
  { id: "interview", label: "Interview", description: "面接対策", disabled: true },
] as const;

export default function TalkPage() {
  const {
    currentSession,
    messages,
    isLoading,
    isSending,
    error,
    startSession,
    sendMessage,
    reset,
    clearError,
  } = useTalkStore();

  const [input, setInput] = useState("");
  const [selectedMode, setSelectedMode] = useState("casual_chat");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // セッション開始
  const handleStartSession = useCallback(async () => {
    clearError();
    await startSession(selectedMode);
  }, [selectedMode, startSession, clearError]);

  // メッセージ送信
  const handleSend = useCallback(async () => {
    if (!input.trim() || isSending) return;
    const content = input.trim();
    setInput("");
    await sendMessage(content);
  }, [input, isSending, sendMessage]);

  // Enter送信（Shift+Enterは改行）
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 新しいセッション開始
  const handleNewSession = useCallback(() => {
    reset();
  }, [reset]);

  // テキストエリアの自動リサイズ
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  return (
    <AppShell>
      <div className="flex flex-col h-[calc(100vh-7rem)] md:h-[calc(100vh-5rem)]">
        {/* セッション未開始 */}
        {!currentSession ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-md space-y-6 text-center">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
                <MessageCircle className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
                  AI Free Talk
                </h1>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">
                  AIと英語で自由に会話しましょう。文法・表現のフィードバックが即座にもらえます。
                </p>
              </div>

              {/* モード選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Select Mode
                </p>
                <div className="grid gap-2">
                  {TALK_MODES.map((mode) => (
                    <button
                      key={mode.id}
                      onClick={() => !mode.disabled && setSelectedMode(mode.id)}
                      disabled={mode.disabled}
                      className={`flex items-center gap-3 p-3 rounded-xl border text-left transition-colors ${
                        selectedMode === mode.id
                          ? "border-primary bg-primary/5"
                          : mode.disabled
                            ? "border-[var(--color-border)] opacity-40 cursor-not-allowed"
                            : "border-[var(--color-border)] hover:border-primary/30"
                      }`}
                    >
                      <div
                        className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                          selectedMode === mode.id
                            ? "border-primary"
                            : "border-[var(--color-text-muted)]"
                        }`}
                      >
                        {selectedMode === mode.id && (
                          <div className="w-2 h-2 rounded-full bg-primary" />
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--color-text-primary)]">
                          {mode.label}
                          {mode.disabled && (
                            <span className="ml-2 text-[10px] text-[var(--color-text-muted)]">
                              (Coming Soon)
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-[var(--color-text-muted)]">
                          {mode.description}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* エラー表示 */}
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400">
                  {error}
                </div>
              )}

              {/* 開始ボタン */}
              <button
                onClick={handleStartSession}
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-500 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
              >
                {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Start Talking
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* セッションヘッダー */}
            <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border)]">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse-slow" />
                <span className="text-sm font-medium text-[var(--color-text-secondary)]">
                  {currentSession.mode === "casual_chat"
                    ? "Casual Chat"
                    : currentSession.mode}{" "}
                  Session
                </span>
              </div>
              <button
                onClick={handleNewSession}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
              >
                New Session
              </button>
            </div>

            {/* チャットウィンドウ */}
            <ChatWindow messages={messages} isSending={isSending} />

            {/* エラー表示 */}
            {error && (
              <div className="px-2 py-2">
                <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400 flex items-center justify-between">
                  <span>{error}</span>
                  <button onClick={clearError} className="text-red-400 hover:text-red-300 underline text-xs">
                    閉じる
                  </button>
                </div>
              </div>
            )}

            {/* 入力エリア */}
            <div className="pt-3 border-t border-[var(--color-border)]">
              <div className="flex items-end gap-2">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message in English..."
                  rows={1}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-[var(--color-bg-input)] border border-[var(--color-border)] text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors resize-none"
                  disabled={isSending}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isSending}
                  className="px-4 py-2.5 rounded-xl bg-primary text-white hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0"
                >
                  {isSending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
              <p className="text-[10px] text-[var(--color-text-muted)] mt-1.5 text-center">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
