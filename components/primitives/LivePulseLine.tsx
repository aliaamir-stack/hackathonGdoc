import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useReducedMotion } from "@/hooks/use-reduced-motion";

type Props = {
  width?: number;
  height?: number;
  className?: string;
  color?: string;
  /** Set true for the hero — runs through PULSE wordmark */
  hero?: boolean;
};

/**
 * Animated ECG / vital-sign waveform. Driven by a state counter so the
 * stroke phase advances over time — not a CSS animation, so it's predictable
 * and respects reduced motion.
 */
export const LivePulseLine = ({
  width = 800,
  height = 80,
  className = "",
  color = "hsl(var(--vital))",
  hero = false,
}: Props) => {
  const reduced = useReducedMotion();
  const [t, setT] = useState(0);

  useEffect(() => {
    if (reduced) return;
    let raf: number;
    const tick = () => {
      setT((v) => (v + 1) % 10000);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [reduced]);

  // Build a waveform path. Mostly flat with periodic QRS-style spikes.
  const buildPath = (offset: number) => {
    const w = width;
    const h = height;
    const mid = h / 2;
    const step = 4;
    let d = `M0 ${mid}`;
    for (let x = 0; x <= w; x += step) {
      const phase = (x + offset) % 180;
      let y = mid;
      if (phase > 60 && phase < 78) {
        // P wave
        y = mid - Math.sin(((phase - 60) / 18) * Math.PI) * 6;
      } else if (phase >= 90 && phase < 96) {
        y = mid + 6; // Q
      } else if (phase >= 96 && phase < 102) {
        y = mid - (hero ? 32 : 26); // R spike
      } else if (phase >= 102 && phase < 108) {
        y = mid + 12; // S
      } else if (phase >= 120 && phase < 140) {
        // T wave
        y = mid - Math.sin(((phase - 120) / 20) * Math.PI) * 8;
      }
      d += ` L${x} ${y.toFixed(2)}`;
    }
    return d;
  };

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      preserveAspectRatio="none"
      aria-hidden
    >
      <defs>
        <linearGradient id="pulseFade" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor={color} stopOpacity="0" />
          <stop offset="0.15" stopColor={color} stopOpacity="0.9" />
          <stop offset="0.85" stopColor={color} stopOpacity="0.9" />
          <stop offset="1" stopColor={color} stopOpacity="0" />
        </linearGradient>
        <filter id="pulseGlow">
          <feGaussianBlur stdDeviation={hero ? 3 : 1.5} result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {/* faint trailing ghost */}
      <path d={buildPath(t * 2)} stroke={color} strokeOpacity="0.18" strokeWidth={hero ? 2 : 1} fill="none" />
      {/* main bright line */}
      <motion.path
        d={buildPath(t * 2 + 4)}
        stroke="url(#pulseFade)"
        strokeWidth={hero ? 2.5 : 1.5}
        fill="none"
        filter="url(#pulseGlow)"
      />
    </svg>
  );
};
