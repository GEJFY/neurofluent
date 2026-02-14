"use client";

/**
 * 音素グリッド
 * 音素ペアのマスター度をカラーコードで表示
 */

interface PhonemeData {
  pair: string;
  accuracy: number;
  practiced: boolean;
}

interface PhonemeGridProps {
  phonemes: PhonemeData[];
  onSelect: (pair: string) => void;
}

function getAccuracyStyle(accuracy: number, practiced: boolean) {
  if (!practiced) {
    return {
      bg: "bg-[var(--color-bg-input)]",
      border: "border-[var(--color-border)]",
      text: "text-[var(--color-text-muted)]",
      badgeBg: "bg-[var(--color-bg-primary)]",
      badgeText: "text-[var(--color-text-muted)]",
    };
  }
  if (accuracy >= 80) {
    return {
      bg: "bg-green-500/5",
      border: "border-green-500/20",
      text: "text-green-400",
      badgeBg: "bg-green-500/10",
      badgeText: "text-green-400",
    };
  }
  if (accuracy >= 50) {
    return {
      bg: "bg-warning/5",
      border: "border-warning/20",
      text: "text-warning",
      badgeBg: "bg-warning/10",
      badgeText: "text-warning",
    };
  }
  return {
    bg: "bg-red-500/5",
    border: "border-red-500/20",
    text: "text-red-400",
    badgeBg: "bg-red-500/10",
    badgeText: "text-red-400",
  };
}

export default function PhonemeGrid({ phonemes, onSelect }: PhonemeGridProps) {
  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
        Select Phoneme Pair
      </p>

      {/* 凡例 */}
      <div className="flex items-center gap-4 text-[10px] text-[var(--color-text-muted)]">
        <div className="flex items-center gap-1">
          <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
          <span>Mastered (80%+)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2.5 h-2.5 rounded-full bg-warning" />
          <span>Learning (50-80%)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
          <span>Needs Work (&lt;50%)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2.5 h-2.5 rounded-full bg-[var(--color-text-muted)] opacity-40" />
          <span>Not practiced</span>
        </div>
      </div>

      {/* グリッド */}
      <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
        {phonemes.map((phoneme) => {
          const style = getAccuracyStyle(phoneme.accuracy, phoneme.practiced);
          return (
            <button
              key={phoneme.pair}
              onClick={() => onSelect(phoneme.pair)}
              className={`p-3 rounded-xl border transition-all hover:scale-[1.02] active:scale-[0.98] ${style.bg} ${style.border} hover:border-primary/40`}
            >
              <p
                className={`text-sm font-mono font-bold ${style.text} text-center`}
              >
                {phoneme.pair}
              </p>
              <div className="mt-1.5 flex justify-center">
                {phoneme.practiced ? (
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${style.badgeBg} ${style.badgeText}`}
                  >
                    {phoneme.accuracy}%
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[var(--color-bg-primary)] text-[var(--color-text-muted)]">
                    New
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
