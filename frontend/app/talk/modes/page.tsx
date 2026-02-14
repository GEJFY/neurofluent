"use client";

import Link from "next/link";
import {
  MessageCircle,
  Users,
  Swords,
  Presentation,
  Handshake,
  Coffee,
  ChevronRight,
} from "lucide-react";
import AppShell from "@/components/layout/AppShell";

/**
 * 会話モード一覧ページ
 * 6つの会話モードを選択して練習開始
 */

interface TalkMode {
  id: string;
  name: string;
  nameJa: string;
  description: string;
  icon: React.ElementType;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  difficultyColor: string;
  href: string;
}

const TALK_MODES: TalkMode[] = [
  {
    id: "casual_chat",
    name: "Casual Chat",
    nameJa: "日常英会話",
    description:
      "友人や同僚とのカジュアルな英語会話を練習。日常的なトピックでリラックスしながら話す力を鍛えます。",
    icon: MessageCircle,
    difficulty: "Beginner",
    difficultyColor: "bg-green-500/10 text-green-400",
    href: "/talk?mode=casual_chat",
  },
  {
    id: "meeting",
    name: "Meeting Facilitation",
    nameJa: "会議進行",
    description:
      "英語での会議を進行する力を養います。議題の提示、意見の集約、結論のまとめなどのスキルを練習します。",
    icon: Users,
    difficulty: "Intermediate",
    difficultyColor: "bg-warning/10 text-warning",
    href: "/talk?mode=meeting",
  },
  {
    id: "debate",
    name: "Debate & Discussion",
    nameJa: "ディベート",
    description:
      "論理的に意見を述べ、反論する練習。ビジネスや社会問題について、説得力のある議論ができるようになります。",
    icon: Swords,
    difficulty: "Advanced",
    difficultyColor: "bg-red-500/10 text-red-400",
    href: "/talk?mode=debate",
  },
  {
    id: "presentation",
    name: "Presentation Q&A",
    nameJa: "プレゼン質疑",
    description:
      "プレゼンテーション後の質疑応答を練習。鋭い質問への対応力、的確な回答力を鍛えます。",
    icon: Presentation,
    difficulty: "Intermediate",
    difficultyColor: "bg-warning/10 text-warning",
    href: "/talk?mode=presentation",
  },
  {
    id: "negotiation",
    name: "Client Negotiation",
    nameJa: "クライアント交渉",
    description:
      "クライアントとの交渉シーンを実践。条件の提示、妥協点の模索、合意形成までのプロセスを体験します。",
    icon: Handshake,
    difficulty: "Advanced",
    difficultyColor: "bg-red-500/10 text-red-400",
    href: "/talk?mode=negotiation",
  },
  {
    id: "small_talk",
    name: "Small Talk",
    nameJa: "ビジネスカジュアル",
    description:
      "ビジネスシーンでの雑談力を磨きます。初対面の挨拶、天気の話、週末の予定など、関係構築に必要なスキルです。",
    icon: Coffee,
    difficulty: "Beginner",
    difficultyColor: "bg-green-500/10 text-green-400",
    href: "/talk?mode=small_talk",
  },
];

export default function TalkModesPage() {
  return (
    <AppShell>
      <div className="space-y-6">
        {/* ヘッダー */}
        <div className="space-y-1">
          <h1 className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            Conversation Modes
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            シーン別の英語会話練習モードを選択
          </p>
        </div>

        {/* モードグリッド */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {TALK_MODES.map((mode) => {
            const Icon = mode.icon;
            return (
              <Link key={mode.id} href={mode.href}>
                <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 hover:border-primary/40 transition-colors group h-full">
                  <div className="flex items-start gap-4">
                    {/* アイコン */}
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>

                    {/* コンテンツ */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-semibold text-[var(--color-text-primary)]">
                          {mode.name}
                        </p>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${mode.difficultyColor}`}
                        >
                          {mode.difficulty}
                        </span>
                      </div>
                      <p className="text-xs text-[var(--color-text-muted)] mb-2">
                        {mode.nameJa}
                      </p>
                      <p className="text-xs text-[var(--color-text-secondary)] leading-relaxed line-clamp-2">
                        {mode.description}
                      </p>
                    </div>

                    {/* 矢印 */}
                    <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-primary transition-colors shrink-0 mt-1" />
                  </div>

                  {/* 開始ボタン */}
                  <div className="mt-4 flex justify-end">
                    <span className="px-4 py-1.5 rounded-lg bg-primary/10 text-primary text-xs font-semibold group-hover:bg-primary/20 transition-colors">
                      Start Session
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* 補足 */}
        <div className="text-center py-4">
          <p className="text-xs text-[var(--color-text-muted)]">
            各モードではAIが相手役となって実践的な会話練習ができます。
            フィードバックはリアルタイムで提供されます。
          </p>
        </div>
      </div>
    </AppShell>
  );
}
