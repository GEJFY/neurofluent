"use client";

import {
  MessageCircle,
  Briefcase,
  Swords,
  Presentation,
  Handshake,
  Coffee,
  Lock,
} from "lucide-react";

/**
 * ModeSelector - 会話モード選択コンポーネント
 * - Casual Chat, Meeting, Debate (available)
 * - Presentation Q&A, Negotiation, Small Talk (coming soon - Phase 3)
 */

export interface ConversationMode {
  id: string;
  label: string;
  labelJa: string;
  description: string;
  icon: React.ElementType;
  available: boolean;
  phase?: string;
}

interface ModeSelectorProps {
  /** モード選択時のコールバック */
  onSelectMode: (mode: ConversationMode) => void;
  /** 現在選択されているモードID */
  selectedMode?: string;
}

const CONVERSATION_MODES: ConversationMode[] = [
  {
    id: "casual_chat",
    label: "Casual Chat",
    labelJa: "カジュアルトーク",
    description: "自由に英語で会話を楽しもう。文法・表現のフィードバック付き。",
    icon: MessageCircle,
    available: true,
  },
  {
    id: "meeting",
    label: "Meeting",
    labelJa: "ミーティング",
    description: "ビジネス会議のシミュレーション。議論・合意形成の練習。",
    icon: Briefcase,
    available: true,
  },
  {
    id: "debate",
    label: "Debate",
    labelJa: "ディベート",
    description: "AIと論理的な議論をしよう。論点整理・反論の練習に。",
    icon: Swords,
    available: true,
  },
  {
    id: "presentation_qa",
    label: "Presentation Q&A",
    labelJa: "プレゼンQ&A",
    description: "プレゼン後の質疑応答を練習。即興での回答力を鍛えます。",
    icon: Presentation,
    available: false,
    phase: "Phase 3",
  },
  {
    id: "negotiation",
    label: "Negotiation",
    labelJa: "ネゴシエーション",
    description: "価格交渉や条件折衝のシミュレーション。説得力を磨きます。",
    icon: Handshake,
    available: false,
    phase: "Phase 3",
  },
  {
    id: "small_talk",
    label: "Small Talk",
    labelJa: "スモールトーク",
    description: "ビジネスの場での雑談力。アイスブレイクや社交的な会話の練習。",
    icon: Coffee,
    available: false,
    phase: "Phase 3",
  },
];

export default function ModeSelector({
  onSelectMode,
  selectedMode,
}: ModeSelectorProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
          Select Conversation Mode
        </p>
        <p className="text-[11px] text-[var(--color-text-muted)]">
          シチュエーションに応じた会話モードを選択してください
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {CONVERSATION_MODES.map((mode) => {
          const Icon = mode.icon;
          const isSelected = selectedMode === mode.id;

          return (
            <button
              key={mode.id}
              onClick={() => mode.available && onSelectMode(mode)}
              disabled={!mode.available}
              className={`relative flex items-start gap-3 p-4 rounded-xl border text-left transition-all ${
                !mode.available
                  ? "opacity-45 cursor-not-allowed border-[var(--color-border)]"
                  : isSelected
                    ? "border-primary bg-primary/5 ring-1 ring-primary/30"
                    : "border-[var(--color-border)] hover:border-primary/30 hover:bg-[var(--color-bg-card)]"
              }`}
            >
              {/* アイコン */}
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                  !mode.available
                    ? "bg-[var(--color-bg-primary)]"
                    : isSelected
                      ? "bg-primary/15"
                      : "bg-[var(--color-bg-primary)]"
                }`}
              >
                {mode.available ? (
                  <Icon
                    className={`w-5 h-5 ${
                      isSelected
                        ? "text-primary"
                        : "text-[var(--color-text-secondary)]"
                    }`}
                  />
                ) : (
                  <Lock className="w-4 h-4 text-[var(--color-text-muted)]" />
                )}
              </div>

              {/* テキスト */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <p
                    className={`text-sm font-semibold ${
                      isSelected
                        ? "text-primary"
                        : "text-[var(--color-text-primary)]"
                    }`}
                  >
                    {mode.label}
                  </p>
                  {mode.phase && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-warning/15 text-warning">
                      {mode.phase}
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-[var(--color-text-muted)]">
                  {mode.labelJa}
                </p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1 leading-relaxed line-clamp-2">
                  {mode.description}
                </p>
              </div>

              {/* 選択インジケーター */}
              {mode.available && (
                <div
                  className={`w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 mt-1 ${
                    isSelected
                      ? "border-primary"
                      : "border-[var(--color-text-muted)]"
                  }`}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-primary" />
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
