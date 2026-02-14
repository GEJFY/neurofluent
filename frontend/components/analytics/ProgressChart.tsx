"use client";

import { useState } from "react";

/**
 * 進捗チャート
 * Pure CSSによるバーチャート
 */

interface ProgressChartProps {
  data: { date: string; value: number }[];
  label: string;
  color?: string;
}

export default function ProgressChart({
  data,
  label,
  color = "bg-primary",
}: ProgressChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const maxValue = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider">
          {label}
        </p>
        {hoveredIndex !== null && (
          <span className="text-xs font-semibold text-primary animate-fade-in">
            {data[hoveredIndex].value}
          </span>
        )}
      </div>

      {/* バーチャート */}
      <div className="flex items-end gap-2 h-36">
        {data.map((item, index) => {
          const heightPercent = (item.value / maxValue) * 100;
          const isHovered = hoveredIndex === index;

          return (
            <div
              key={index}
              className="flex-1 flex flex-col items-center gap-1.5 group"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {/* 値表示（ホバー時） */}
              <div
                className={`text-[10px] font-semibold text-primary transition-opacity ${
                  isHovered ? "opacity-100" : "opacity-0"
                }`}
              >
                {item.value}
              </div>

              {/* バー */}
              <div className="w-full relative" style={{ height: "100px" }}>
                <div
                  className={`absolute bottom-0 w-full rounded-t-lg transition-all duration-300 ${
                    isHovered ? "bg-primary" : `${color}/30`
                  }`}
                  style={{
                    height: `${Math.max(heightPercent, 4)}%`,
                  }}
                >
                  {/* バー内部のグラデーション */}
                  {!isHovered && (
                    <div
                      className={`absolute bottom-0 w-full ${color} rounded-t-lg`}
                      style={{ height: "50%" }}
                    />
                  )}
                </div>
              </div>

              {/* ラベル */}
              <span
                className={`text-[10px] transition-colors ${
                  isHovered
                    ? "text-primary font-semibold"
                    : "text-[var(--color-text-muted)]"
                }`}
              >
                {item.date}
              </span>
            </div>
          );
        })}
      </div>

      {/* サマリー */}
      <div className="flex items-center justify-between pt-2 border-t border-[var(--color-border)]">
        <span className="text-[11px] text-[var(--color-text-muted)]">
          Total: {data.reduce((sum, d) => sum + d.value, 0)}
        </span>
        <span className="text-[11px] text-[var(--color-text-muted)]">
          Avg: {Math.round(data.reduce((sum, d) => sum + d.value, 0) / data.length)}
        </span>
      </div>
    </div>
  );
}
