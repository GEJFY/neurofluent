"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Send, Loader2, MessageCircle, Mic, MessageSquare } from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import ChatWindow from "@/components/chat/ChatWindow";
import VoiceChat from "@/components/talk/VoiceChat";
import { useTalkStore } from "@/lib/stores/talk-store";
import { api } from "@/lib/api";

/**
 * AI Free Talk ページ
 * - モードセレクター
 * - シナリオ選択（モード別）
 * - チャットウィンドウ
 * - テキスト入力 + 送信ボタン
 */

interface TalkScenario {
  id: string;
  mode: string;
  title: string;
  description: string;
  difficulty: string;
  accent_context?: string;
}

const TALK_MODES = [
  { id: "casual_chat", label: "Casual Chat", description: "自由に英会話を楽しもう", disabled: false },
  { id: "meeting", label: "Business Meeting", description: "ビジネス会議のシミュレーション", disabled: false },
  { id: "interview", label: "Interview", description: "面接対策の練習", disabled: false },
  { id: "presentation", label: "Presentation", description: "プレゼンの練習", disabled: false },
  { id: "negotiation", label: "Negotiation", description: "交渉スキルを磨く", disabled: false },
  { id: "phone_call", label: "Phone Call", description: "電話対応の練習", disabled: false },
] as const;

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "text-green-400 bg-green-500/15",
  intermediate: "text-warning bg-warning/15",
  advanced: "text-red-400 bg-red-500/15",
};

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
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [selectedMode, setSelectedMode] = useState("casual_chat");
  const [scenarios, setScenarios] = useState<TalkScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [isLoadingScenarios, setIsLoadingScenarios] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // モード変更時にシナリオを取得
  useEffect(() => {
    setSelectedScenarioId(null);
    if (selectedMode === "casual_chat") {
      setScenarios([]);
      return;
    }
    let cancelled = false;
    setIsLoadingScenarios(true);
    api.getScenarios(selectedMode).then((data) => {
      if (!cancelled) {
        setScenarios(data);
        setIsLoadingScenarios(false);
      }
    }).catch(() => {
      if (!cancelled) {
        setScenarios([]);
        setIsLoadingScenarios(false);
      }
    });
    return () => { cancelled = true; };
  }, [selectedMode]);

  // セッション開始
  const handleStartSession = useCallback(async () => {
    clearError();
    await startSession(selectedMode, selectedScenarioId ?? undefined);
  }, [selectedMode, selectedScenarioId, startSession, clearError]);

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
            <div className="w-full max-w-md lg:max-w-4xl space-y-6 text-center lg:text-left">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto lg:mx-0">
                <MessageCircle className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-heading font-bold text-[var(--color-text-primary)]">
                  AI Free Talk
                </h1>
                <p className="text-sm text-[var(--color-text-secondary)] mt-1 leading-relaxed">
                  AIと英語で自由に会話しましょう。文法・表現のフィードバックが即座にもらえます。
                </p>
              </div>

              {/* デスクトップ: 2パネルレイアウト */}
              <div className="lg:flex lg:gap-8">
              {/* 左パネル: モード選択 + シナリオ */}
              <div className="lg:flex-1 space-y-4">

              {/* モード選択 */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                  Select Mode
                </p>
                <div className="grid gap-2 lg:grid-cols-2">
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
                        </p>
                        <p className="text-xs text-[var(--color-text-muted)]">
                          {mode.description}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* シナリオ選択（casual_chat以外） */}
              {scenarios.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                    Scenario <span className="text-[var(--color-text-muted)] font-normal normal-case">(optional)</span>
                  </p>
                  <div className="grid gap-2 max-h-48 lg:max-h-64 overflow-y-auto">
                    {scenarios.map((scenario) => (
                      <button
                        key={scenario.id}
                        onClick={() =>
                          setSelectedScenarioId(
                            selectedScenarioId === scenario.id ? null : scenario.id
                          )
                        }
                        className={`flex items-start gap-3 p-3 rounded-xl border text-left transition-colors ${
                          selectedScenarioId === scenario.id
                            ? "border-primary bg-primary/5"
                            : "border-[var(--color-border)] hover:border-primary/30"
                        }`}
                      >
                        <div
                          className={`w-4 h-4 mt-0.5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                            selectedScenarioId === scenario.id
                              ? "border-primary"
                              : "border-[var(--color-text-muted)]"
                          }`}
                        >
                          {selectedScenarioId === scenario.id && (
                            <div className="w-2 h-2 rounded-full bg-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                              {scenario.title}
                            </p>
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold shrink-0 ${
                                DIFFICULTY_COLORS[scenario.difficulty] || "text-[var(--color-text-muted)] bg-[var(--color-bg-input)]"
                              }`}
                            >
                              {scenario.difficulty}
                            </span>
                          </div>
                          <p className="text-[11px] text-[var(--color-text-muted)] line-clamp-2">
                            {scenario.description}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {isLoadingScenarios && (
                <div className="flex items-center justify-center gap-2 py-3 text-xs text-[var(--color-text-muted)]">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Loading scenarios...
                </div>
              )}

              </div>{/* 左パネル終了 */}

              {/* 右パネル: プレビュー + 開始ボタン */}
              <div className="lg:w-72 lg:shrink-0 space-y-4">
                {/* 選択モードプレビュー */}
                <div className="hidden lg:block bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3">
                  <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
                    Selected
                  </p>
                  <div>
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                      {TALK_MODES.find(m => m.id === selectedMode)?.label}
                    </p>
                    <p className="text-xs text-[var(--color-text-muted)] mt-1">
                      {TALK_MODES.find(m => m.id === selectedMode)?.description}
                    </p>
                  </div>
                  {selectedScenarioId && scenarios.find(s => s.id === selectedScenarioId) && (
                    <div className="pt-3 border-t border-[var(--color-border)]">
                      <p className="text-xs text-[var(--color-text-muted)]">Scenario</p>
                      <p className="text-sm text-[var(--color-text-primary)] mt-0.5">
                        {scenarios.find(s => s.id === selectedScenarioId)?.title}
                      </p>
                    </div>
                  )}
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
              </div>{/* 2パネルレイアウト終了 */}
            </div>
          </div>
        ) : (
          <>
            {/* セッションヘッダー */}
            <div className="flex items-center justify-between pb-3 border-b border-[var(--color-border)]">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse-slow" />
                <span className="text-sm font-medium text-[var(--color-text-secondary)]">
                  {TALK_MODES.find(m => m.id === currentSession.mode)?.label ?? currentSession.mode}{" "}
                  Session
                </span>
              </div>
              <div className="flex items-center gap-2">
                {/* Voice/Text切り替え */}
                <button
                  onClick={() => setIsVoiceMode(!isVoiceMode)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    isVoiceMode
                      ? "bg-accent/10 text-accent hover:bg-accent/20"
                      : "bg-[var(--color-bg-card)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] border border-[var(--color-border)]"
                  }`}
                >
                  {isVoiceMode ? <MessageSquare className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
                  {isVoiceMode ? "Text" : "Voice"}
                </button>
                <button
                  onClick={handleNewSession}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  New Session
                </button>
              </div>
            </div>

            {/* Voice/Chat切り替え */}
            {isVoiceMode ? (
              <VoiceChat
                sessionId={currentSession.id}
                mode={currentSession.mode}
                onEnd={handleNewSession}
              />
            ) : (
              <ChatWindow messages={messages} isSending={isSending} />
            )}

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
