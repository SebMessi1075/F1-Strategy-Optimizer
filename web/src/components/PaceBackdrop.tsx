"use client";

import { motion, useReducedMotion } from "framer-motion";

function smoothPath(pts: [number, number][]): string {
  if (pts.length < 2) return "";
  let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] ?? pts[i];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[i + 2] ?? p2;
    const c1x = p1[0] + (p2[0] - p0[0]) / 6;
    const c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6;
    const c2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += `C${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  return d;
}

function buildTrace(recommendedLap: number[], W = 1200, H = 420) {
  const positive = recommendedLap.filter(v => v > 0);
  if (positive.length === 0) return { d: "", area: "", W, H };
  const base = Math.min(...positive);
  const v = recommendedLap.map(x => Math.min(x, base + 16));
  const lo = Math.min(...v);
  const hi = Math.max(...v);
  const range = hi - lo || 1;
  const pts: [number, number][] = v.map((y, i) => [
    (i / (v.length - 1)) * W,
    (1 - (y - lo) / range) * (H * 0.7) + H * 0.16,
  ]);
  const d = smoothPath(pts);
  const last = pts[pts.length - 1];
  const area = d + ` L${last[0].toFixed(1)} ${H} L0 ${H} Z`;
  return { d, area, W, H };
}

interface Props {
  lapTimes: number[];
  circuitKey: string;
}

export default function PaceBackdrop({ lapTimes, circuitKey }: Props) {
  const prefersReduced = useReducedMotion();
  const { d, area, W, H } = buildTrace(lapTimes);

  if (!d) return null;

  return (
    <div
      className="absolute inset-0 pointer-events-none overflow-hidden"
      style={{
        zIndex: 0,
        maskImage:
          "radial-gradient(75% 60% at 50% 50%, #000 55%, transparent 100%)",
        WebkitMaskImage:
          "radial-gradient(75% 60% at 50% 50%, #000 55%, transparent 100%)",
      }}
      aria-hidden
    >
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id={`trace-grad-${circuitKey}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0" />
            <stop offset="12%" stopColor="var(--accent)" stopOpacity="1" />
            <stop offset="88%" stopColor="var(--accent)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Faint area fill */}
        <path d={area} fill="var(--accent)" opacity="0.04" />

        {/* Animated stroke line */}
        <motion.path
          key={circuitKey}
          d={d}
          fill="none"
          stroke={`url(#trace-grad-${circuitKey})`}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={prefersReduced ? false : { pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.45 }}
          transition={{ duration: 2.2, ease: "easeOut" }}
        />
      </svg>
    </div>
  );
}
