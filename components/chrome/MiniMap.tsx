import { useEffect, useState } from "react";
import { WAYPOINTS } from "@/lib/pulseData";

export const MiniMap = () => {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      setPct(h > 0 ? window.scrollY / h : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // interpolate dot between waypoints
  const idxFloat = pct * (WAYPOINTS.length - 1);
  const i = Math.floor(idxFloat);
  const t = idxFloat - i;
  const a = WAYPOINTS[i];
  const b = WAYPOINTS[Math.min(i + 1, WAYPOINTS.length - 1)];
  const dx = a.x + (b.x - a.x) * t;
  const dy = a.y + (b.y - a.y) * t;

  return (
    <div className="hidden lg:block fixed left-6 bottom-6 z-30 w-44 border border-border bg-surface/80 backdrop-blur-md p-3">
      <div className="flex items-center justify-between font-mono text-[9px] uppercase tracking-wider text-3 mb-2">
        <span>Mini-map</span>
        <span className="text-vital">● live</span>
      </div>
      <div className="relative aspect-[4/3] bg-bg-deep border border-border overflow-hidden">
        <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
          <path
            d="M18 22 Q14 36 22 50 Q12 60 24 72 Q22 86 36 88 Q50 92 60 84 Q76 88 80 72 Q92 64 86 50 Q94 36 78 26 Q66 16 52 18 Q38 12 28 18 Z"
            fill="hsl(var(--surface-2))"
            stroke="hsl(var(--border))"
            strokeWidth="0.3"
          />
          {WAYPOINTS.map((w) => (
            <a key={w.id} href={`#${w.id}`}>
              <circle cx={w.x} cy={w.y} r="1.4" fill="hsl(var(--text-3))" />
              <text x={w.x + 2.5} y={w.y + 1.5} fontSize="3" fill="hsl(var(--text-3))" fontFamily="JetBrains Mono">{w.label}</text>
            </a>
          ))}
          <circle cx={dx} cy={dy} r="2" fill="hsl(var(--vital))" />
          <circle cx={dx} cy={dy} r="3.5" fill="none" stroke="hsl(var(--vital))" strokeWidth="0.4" opacity="0.6" />
        </svg>
      </div>
    </div>
  );
};
