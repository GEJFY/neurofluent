"use client";

import type { TalkMessageResponse } from "@/lib/api";
import FeedbackPanel from "./FeedbackPanel";

/**
 * チャットメッセージバブル
 * ユーザー: 右寄せ・Indigo背景
 * AI: 左寄せ・ダークグレー背景
 */
interface MessageBubbleProps {
  message: TalkMessageResponse;
  /** フィードバックパネルの初期表示状態 */
  showFeedback?: boolean;
}

export default function MessageBubble({
  message,
  showFeedback = false,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  // タイムスタンプフォーマット
  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString("ja-JP", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
    >
      <div className={`max-w-[85%] md:max-w-[70%] lg:max-w-[60%] ${isUser ? "order-1" : ""}`}>
        {/* メッセージバブル */}
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? "bg-primary text-white rounded-br-md"
              : "bg-[var(--color-bg-card)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-bl-md"
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* タイムスタンプ */}
        <p
          className={`text-[10px] text-[var(--color-text-muted)] mt-1 ${
            isUser ? "text-right" : "text-left"
          }`}
        >
          {formatTime(message.created_at)}
        </p>

        {/* ユーザーメッセージにフィードバックパネルを表示 */}
        {isUser && message.feedback && (
          <FeedbackPanel
            feedback={message.feedback}
            defaultExpanded={showFeedback}
          />
        )}
      </div>
    </div>
  );
}
