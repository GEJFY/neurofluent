"use client";

import { useState } from "react";
import { Play, Mic, Volume2 } from "lucide-react";

/**
 * ミニマルペアカード
 * 2つの似た単語を並べて表示し、発音の違いを練習
 */

interface MinimalPairCardProps {
  wordA: string;
  wordB: string;
  ipaA: string;
  ipaB: string;
  targetPhoneme: string;
  onRecord: () => void;
}

export default function MinimalPairCard({
  wordA,
  wordB,
  ipaA,
  ipaB,
  targetPhoneme,
  onRecord,
}: MinimalPairCardProps) {
  const [playingA, setPlayingA] = useState(false);
  const [playingB, setPlayingB] = useState(false);

  // 差分の音素をハイライト（デモ：最初の異なる文字を検出）
  const highlightDiff = (ipa: string, otherIpa: string) => {
    const chars = ipa.split("");
    const otherChars = otherIpa.split("");

    return chars.map((char, i) => {
      const isDiff = char !== otherChars[i];
      return (
        <span
          key={i}
          className={isDiff ? "text-primary font-bold" : ""}
        >
          {char}
        </span>
      );
    });
  };

  const handlePlayA = () => {
    setPlayingA(true);
    setTimeout(() => setPlayingA(false), 1000);
  };

  const handlePlayB = () => {
    setPlayingB(true);
    setTimeout(() => setPlayingB(false), 1000);
  };

  return (
    <div className="w-full max-w-lg">
      {/* ターゲット音素表示 */}
      <div className="text-center mb-4">
        <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-mono font-bold">
          {targetPhoneme}
        </span>
      </div>

      {/* 2つの単語カード */}
      <div className="grid grid-cols-2 gap-3">
        {/* Word A */}
        <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3 text-center">
          <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            {wordA}
          </p>
          <div className="text-sm font-mono text-accent">
            {highlightDiff(ipaA, ipaB)}
          </div>
          <button
            onClick={handlePlayA}
            disabled={playingA}
            className={`w-10 h-10 rounded-full flex items-center justify-center mx-auto transition-all ${
              playingA
                ? "bg-accent/20 border-2 border-accent animate-pulse"
                : "bg-accent/10 border-2 border-accent/30 hover:border-accent"
            }`}
          >
            {playingA ? (
              <Volume2 className="w-4 h-4 text-accent" />
            ) : (
              <Play className="w-4 h-4 text-accent ml-0.5" />
            )}
          </button>
        </div>

        {/* Word B */}
        <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-3 text-center">
          <p className="text-2xl font-heading font-bold text-[var(--color-text-primary)]">
            {wordB}
          </p>
          <div className="text-sm font-mono text-accent">
            {highlightDiff(ipaB, ipaA)}
          </div>
          <button
            onClick={handlePlayB}
            disabled={playingB}
            className={`w-10 h-10 rounded-full flex items-center justify-center mx-auto transition-all ${
              playingB
                ? "bg-accent/20 border-2 border-accent animate-pulse"
                : "bg-accent/10 border-2 border-accent/30 hover:border-accent"
            }`}
          >
            {playingB ? (
              <Volume2 className="w-4 h-4 text-accent" />
            ) : (
              <Play className="w-4 h-4 text-accent ml-0.5" />
            )}
          </button>
        </div>
      </div>

      {/* 差分の視覚的ガイド */}
      <div className="mt-4 p-3 rounded-xl bg-[var(--color-bg-primary)]/50 text-center">
        <p className="text-xs text-[var(--color-text-muted)]">
          Listen to both words and notice the difference in the{" "}
          <span className="text-primary font-semibold font-mono">
            {targetPhoneme}
          </span>{" "}
          sound. Then record your pronunciation.
        </p>
      </div>
    </div>
  );
}
