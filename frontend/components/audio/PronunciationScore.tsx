"use client";

import { useState } from "react";

/**
 * PronunciationScore - 発音スコア表示コンポーネント
 * - 4つの円形プログレスインジケーター（accuracy, fluency, prosody, completeness）
 * - 色分け: green >80, yellow >60, red <60
 * - 単語レベル表示: 各単語を精度に応じて色分け
 */

interface PronunciationScoreProps {
  /** 各カテゴリのスコア（0-100） */
  scores: {
    accuracy: number;
    fluency: number;
    prosody: number;
    completeness: number;
  };
  /** 単語ごとのスコア */
  wordScores?: WordScore[];
}

export interface WordScore {
  word: string;
  accuracy: number;
  error?: string;
}

/** 円形プログレスインジケーター */
function CircularProgress({
  value,
  label,
  size = 90,
}: {
  value: number;
  label: string;
  size?: number;
}) {
  const normalizedValue = Math.min(100, Math.max(0, Math.round(value)));
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedValue / 100) * circumference;

  // スコアに応じた色
  const getColor = (score: number) => {
    if (score >= 80) return { stroke: "#4ade80", text: "text-green-400", bg: "bg-green-500/10" };
    if (score >= 60) return { stroke: "#fbbf24", text: "text-warning", bg: "bg-warning/10" };
    return { stroke: "#f87171", text: "text-red-400", bg: "bg-red-500/10" };
  };

  const color = getColor(normalizedValue);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* 背景リング */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth={strokeWidth}
          />
          {/* プログレスリング */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* 中心のスコア数値 */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-lg font-heading font-bold ${color.text}`}>
            {normalizedValue}
          </span>
        </div>
      </div>
      <span className="text-[11px] text-[var(--color-text-muted)] font-medium text-center">
        {label}
      </span>
    </div>
  );
}

export default function PronunciationScore({
  scores,
  wordScores,
}: PronunciationScoreProps) {
  const [selectedWord, setSelectedWord] = useState<WordScore | null>(null);

  // 総合スコアの計算
  const overallScore = Math.round(
    (scores.accuracy + scores.fluency + scores.prosody + scores.completeness) / 4
  );

  // 総合スコアの色
  const getOverallColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-warning";
    return "text-red-400";
  };

  // 単語の色を取得
  const getWordColor = (accuracy: number) => {
    if (accuracy >= 80) return "text-green-400";
    if (accuracy >= 60) return "text-warning";
    return "text-red-400";
  };

  const getWordBg = (accuracy: number) => {
    if (accuracy >= 80) return "bg-green-500/10 hover:bg-green-500/20";
    if (accuracy >= 60) return "bg-warning/10 hover:bg-warning/20";
    return "bg-red-500/10 hover:bg-red-500/20";
  };

  return (
    <div className="space-y-6">
      {/* 総合スコア */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6 text-center">
        <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
          Overall Score
        </p>
        <p className={`text-5xl font-heading font-bold ${getOverallColor(overallScore)}`}>
          {overallScore}
          <span className="text-lg text-[var(--color-text-muted)]">/100</span>
        </p>
      </div>

      {/* 4つのスコアインジケーター */}
      <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
        <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-4">
          Detailed Scores
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 justify-items-center">
          <CircularProgress value={scores.accuracy} label="Accuracy" />
          <CircularProgress value={scores.fluency} label="Fluency" />
          <CircularProgress value={scores.prosody} label="Prosody" />
          <CircularProgress value={scores.completeness} label="Completeness" />
        </div>

        {/* スコアの解説 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4 pt-4 border-t border-[var(--color-border)]">
          <div className="text-center">
            <p className="text-[10px] text-[var(--color-text-muted)]">
              発音の正確さ
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-[var(--color-text-muted)]">
              流暢さ・滑らかさ
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-[var(--color-text-muted)]">
              抑揚・リズム
            </p>
          </div>
          <div className="text-center">
            <p className="text-[10px] text-[var(--color-text-muted)]">
              完成度
            </p>
          </div>
        </div>
      </div>

      {/* 単語レベルスコア */}
      {wordScores && wordScores.length > 0 && (
        <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-6">
          <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-4">
            Word-Level Analysis
          </p>

          {/* 単語一覧（クリック可能） */}
          <div className="flex flex-wrap gap-1.5">
            {wordScores.map((ws, index) => (
              <button
                key={`${ws.word}-${index}`}
                onClick={() => setSelectedWord(selectedWord?.word === ws.word && selectedWord === ws ? null : ws)}
                className={`px-2 py-1 rounded-lg text-sm font-medium transition-colors cursor-pointer ${getWordBg(ws.accuracy)} ${getWordColor(ws.accuracy)}`}
              >
                {ws.word}
              </button>
            ))}
          </div>

          {/* 選択された単語の詳細 */}
          {selectedWord && (
            <div className="mt-4 p-3 rounded-xl bg-[var(--color-bg-primary)] border border-[var(--color-border)] animate-fade-in">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-sm font-semibold ${getWordColor(selectedWord.accuracy)}`}>
                  &ldquo;{selectedWord.word}&rdquo;
                </span>
                <span className={`text-xs font-bold ${getWordColor(selectedWord.accuracy)}`}>
                  {Math.round(selectedWord.accuracy)}%
                </span>
              </div>
              {selectedWord.error && (
                <p className="text-[11px] text-[var(--color-text-muted)]">
                  Issue: {selectedWord.error}
                </p>
              )}
              {!selectedWord.error && selectedWord.accuracy >= 80 && (
                <p className="text-[11px] text-green-400/80">
                  Good pronunciation!
                </p>
              )}
            </div>
          )}

          {/* 凡例 */}
          <div className="flex items-center gap-4 mt-4 pt-3 border-t border-[var(--color-border)]">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-green-500/20" />
              <span className="text-[10px] text-[var(--color-text-muted)]">Good (80+)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-warning/20" />
              <span className="text-[10px] text-[var(--color-text-muted)]">Fair (60-79)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded bg-red-500/20" />
              <span className="text-[10px] text-[var(--color-text-muted)]">Needs Work (&lt;60)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
