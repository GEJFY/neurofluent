"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Clock,
  Loader2,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";
import ChatWindow from "@/components/chat/ChatWindow";
import { api, type SessionResponse } from "@/lib/api";

/**
 * セッションレビューページ
 * - 全メッセージのリプレイ表示
 * - 各メッセージのフィードバック展開
 */
export default function TalkReviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [session, setSession] = useState<SessionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSession = async () => {
      try {
        const data = await api.getSession(sessionId);
        setSession(data);
      } catch (err) {
        console.error("Failed to load session:", err);
        setError("セッションの読み込みに失敗しました");
      } finally {
        setIsLoading(false);
      }
    };

    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  /** セッションの所要時間を計算 */
  const getDuration = (s: SessionResponse): string => {
    if (s.duration_seconds != null) {
      return `${Math.round(s.duration_seconds / 60)} min`;
    }
    if (!s.started_at) return "-";
    const start = new Date(s.started_at);
    const end = s.ended_at ? new Date(s.ended_at) : new Date();
    const diffMin = Math.round(
      (end.getTime() - start.getTime()) / (1000 * 60)
    );
    return `${diffMin} min`;
  };

  return (
    <AppShell>
      {isLoading ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : error ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-2">
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={() => router.back()}
              className="text-xs text-primary hover:underline"
            >
              戻る
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* ヘッダー */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-2 rounded-lg hover:bg-[var(--color-bg-card)] transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-[var(--color-text-secondary)]" />
            </button>
            <div>
              <h1 className="text-xl font-heading font-bold text-[var(--color-text-primary)]">
                Session Review
              </h1>
              <p className="text-xs text-[var(--color-text-muted)]">
                {session?.started_at
                  ? new Date(session.started_at).toLocaleDateString("ja-JP", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : ""}
              </p>
            </div>
          </div>

          {/* セッション情報 */}
          <div className="flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
            <span>Mode: {session?.mode || "-"}</span>
            <span>Messages: {session?.messages.length || 0}</span>
            {session && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {getDuration(session)}
              </span>
            )}
          </div>

          {/* メッセージリプレイ */}
          <div>
            <h2 className="text-lg font-heading font-semibold text-[var(--color-text-primary)] mb-3">
              Conversation
            </h2>
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-4 max-h-[60vh] overflow-y-auto">
              <ChatWindow
                messages={session?.messages || []}
                expandFeedback={true}
              />
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
