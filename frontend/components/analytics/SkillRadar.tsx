"use client";

/**
 * スキルレーダーチャート
 * SVGで五角形のレーダーチャートを描画
 */

interface SkillRadarProps {
  skills: {
    speaking: number;
    listening: number;
    vocabulary: number;
    grammar: number;
    pronunciation: number;
  };
}

const SKILL_LABELS = [
  { key: "speaking", label: "Speaking", angle: -90 },
  { key: "listening", label: "Listening", angle: -18 },
  { key: "vocabulary", label: "Vocabulary", angle: 54 },
  { key: "grammar", label: "Grammar", angle: 126 },
  { key: "pronunciation", label: "Pronunciation", angle: 198 },
] as const;

// 五角形の頂点を計算
function getPoint(
  centerX: number,
  centerY: number,
  radius: number,
  angleDeg: number
): [number, number] {
  const angleRad = (angleDeg * Math.PI) / 180;
  return [
    centerX + radius * Math.cos(angleRad),
    centerY + radius * Math.sin(angleRad),
  ];
}

// 五角形のパスを生成
function createPolygonPath(
  centerX: number,
  centerY: number,
  radius: number
): string {
  return SKILL_LABELS.map((s, i) => {
    const [x, y] = getPoint(centerX, centerY, radius, s.angle);
    return `${i === 0 ? "M" : "L"} ${x} ${y}`;
  }).join(" ") + " Z";
}

export default function SkillRadar({ skills }: SkillRadarProps) {
  const size = 280;
  const center = size / 2;
  const maxRadius = 100;
  const levels = [20, 40, 60, 80, 100];

  // スキルデータのポリゴンパス
  const dataPath =
    SKILL_LABELS.map((s, i) => {
      const score = skills[s.key as keyof typeof skills] ?? 0;
      const radius = (score / 100) * maxRadius;
      const [x, y] = getPoint(center, center, radius, s.angle);
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    }).join(" ") + " Z";

  return (
    <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-2xl p-5">
      <p className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-4">
        Skills Radar
      </p>
      <div className="flex justify-center">
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="overflow-visible"
        >
          {/* グリッドライン（同心五角形） */}
          {levels.map((level) => {
            const radius = (level / 100) * maxRadius;
            return (
              <path
                key={level}
                d={createPolygonPath(center, center, radius)}
                fill="none"
                stroke="var(--color-border)"
                strokeWidth="1"
                opacity={0.4}
              />
            );
          })}

          {/* 軸線 */}
          {SKILL_LABELS.map((s) => {
            const [x, y] = getPoint(center, center, maxRadius, s.angle);
            return (
              <line
                key={s.key}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="var(--color-border)"
                strokeWidth="1"
                opacity={0.3}
              />
            );
          })}

          {/* データポリゴン（塗りつぶし） */}
          <path
            d={dataPath}
            fill="rgb(99, 102, 241)"
            fillOpacity={0.2}
            stroke="rgb(99, 102, 241)"
            strokeWidth="2"
            strokeLinejoin="round"
          />

          {/* データポイント */}
          {SKILL_LABELS.map((s) => {
            const score = skills[s.key as keyof typeof skills] ?? 0;
            const radius = (score / 100) * maxRadius;
            const [x, y] = getPoint(center, center, radius, s.angle);
            return (
              <circle
                key={s.key}
                cx={x}
                cy={y}
                r="4"
                fill="rgb(99, 102, 241)"
                stroke="var(--color-bg-card)"
                strokeWidth="2"
              />
            );
          })}

          {/* ラベル */}
          {SKILL_LABELS.map((s) => {
            const score = skills[s.key as keyof typeof skills] ?? 0;
            const labelRadius = maxRadius + 28;
            const [x, y] = getPoint(center, center, labelRadius, s.angle);
            return (
              <g key={`label-${s.key}`}>
                <text
                  x={x}
                  y={y - 6}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="var(--color-text-secondary)"
                  fontSize="10"
                  fontWeight="600"
                >
                  {s.label}
                </text>
                <text
                  x={x}
                  y={y + 8}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill={
                    score >= 80
                      ? "rgb(74, 222, 128)"
                      : score >= 60
                        ? "rgb(251, 191, 36)"
                        : "rgb(248, 113, 113)"
                  }
                  fontSize="11"
                  fontWeight="700"
                >
                  {score}%
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
