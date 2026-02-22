"use client";

import { useRef, useEffect } from "react";
import type { TalkMessageResponse } from "@/lib/api";
import MessageBubble from "./MessageBubble";

/**
 * チャットウィンドウ
 * スクロール可能なメッセージリスト + 自動スクロール
 */
interface ChatWindowProps {
  messages: TalkMessageResponse[];
  /** 送信中ローディング表示 */
  isSending?: boolean;
  /** フィードバックを常に展開表示するか（レビュー画面用） */
  expandFeedback?: boolean;
}

export default function ChatWindow({
  messages,
  isSending = false,
  expandFeedback = false,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // 新しいメッセージで自動スクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 lg:px-8">
      {/* メッセージが無い場合の表示 */}
      {messages.length === 0 && !isSending && (
        <div className="flex items-center justify-center h-full min-h-[200px]">
          <div className="text-center space-y-2">
            <p className="text-lg font-heading text-[var(--color-text-secondary)]">
              Start a conversation
            </p>
            <p className="text-sm text-[var(--color-text-muted)]">
              英語で何でも話してみましょう
            </p>
          </div>
        </div>
      )}

      {/* メッセージリスト */}
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          showFeedback={expandFeedback}
        />
      ))}

      {/* 送信中のインジケーター */}
      {isSending && (
        <div className="flex justify-start animate-fade-in">
          <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl rounded-bl-md px-4 py-3">
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full bg-[var(--color-text-muted)] animate-bounce" />
              <div
                className="w-2 h-2 rounded-full bg-[var(--color-text-muted)] animate-bounce"
                style={{ animationDelay: "0.15s" }}
              />
              <div
                className="w-2 h-2 rounded-full bg-[var(--color-text-muted)] animate-bounce"
                style={{ animationDelay: "0.3s" }}
              />
            </div>
          </div>
        </div>
      )}

      {/* スクロールターゲット */}
      <div ref={bottomRef} />
    </div>
  );
}
