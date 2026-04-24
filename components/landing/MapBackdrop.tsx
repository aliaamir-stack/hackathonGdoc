import { motion } from "framer-motion";
import { useReducedMotion } from "@/hooks/use-reduced-motion";

/**
 * Persistent cartographic backdrop: faint grid, contour lines, lat/lng ticks,
 * and slowly drifting cluster dots. Sits behind every section.
 */
export const MapBackdrop = () => {
  const reduced = useReducedMotion();

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* base grid */}
      <div className="absolute inset-0 map-grid opacity-70" />
      {/* fine grid layered on */}
      <div className="absolute inset-0 map-grid-fine opacity-30" />

      {/* radial vignette to keep edges dark */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 30%, hsl(var(--bg-deep)) 90%)",
        }}
      />

      {/* contour lines, drawn as concentric organic blobs */}
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden
      >
        <defs>
          <radialGradient id="contourFade" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="hsl(var(--vital))" stopOpacity="0.18" />
            <stop offset="60%" stopColor="hsl(var(--vital))" stopOpacity="0.04" />
            <stop offset="100%" stopColor="hsl(var(--vital))" stopOpacity="0" />
          </radialGradient>
        </defs>
        {/* contour rings around two "outbreak centers" */}
        {[180, 240, 320, 420, 540].map((r, i) => (
          <circle
            key={`c1-${i}`}
            cx="320"
            cy="640"
            r={r}
            fill="none"
            stroke="hsl(var(--vital))"
            strokeOpacity={0.06 - i * 0.008}
            strokeWidth={1}
          />
        ))}
        {[140, 200, 280, 360, 460].map((r, i) => (
          <circle
            key={`c2-${i}`}
            cx="1140"
            cy="280"
            r={r}
            fill="none"
            stroke="hsl(var(--map-blue))"
            strokeOpacity={0.06 - i * 0.008}
            strokeWidth={1}
          />
        ))}
        {/* lat/lng tick marks along edges */}
        {Array.from({ length: 12 }).map((_, i) => (
          <text
            key={`lat-${i}`}
            x={8}
            y={70 + i * 70}
            fill="hsl(var(--text-3))"
            fontSize="9"
            fontFamily="JetBrains Mono, monospace"
            opacity="0.45"
          >
            {(33 - i * 0.5).toFixed(1)}°N
          </text>
        ))}
        {Array.from({ length: 12 }).map((_, i) => (
          <text
            key={`lng-${i}`}
            x={60 + i * 110}
            y={892}
            fill="hsl(var(--text-3))"
            fontSize="9"
            fontFamily="JetBrains Mono, monospace"
            opacity="0.45"
          >
            {(67 + i * 0.5).toFixed(1)}°E
          </text>
        ))}

        {/* drifting cluster dots */}
        {[
          { cx: 320, cy: 640, c: "vital", d: 0 },
          { cx: 1140, cy: 280, c: "map-blue", d: 1 },
          { cx: 760, cy: 480, c: "alert-amber", d: 2 },
          { cx: 540, cy: 220, c: "alert-red", d: 0.5 },
          { cx: 980, cy: 700, c: "signal-teal", d: 1.5 },
        ].map((p, i) => (
          <g key={`dot-${i}`}>
            <motion.circle
              cx={p.cx}
              cy={p.cy}
              r={3}
              fill={`hsl(var(--${p.c}))`}
              animate={reduced ? undefined : { opacity: [0.9, 0.3, 0.9] }}
              transition={{ duration: 3, delay: p.d, repeat: Infinity, ease: "easeInOut" }}
            />
            {!reduced && (
              <motion.circle
                cx={p.cx}
                cy={p.cy}
                r={3}
                fill="none"
                stroke={`hsl(var(--${p.c}))`}
                strokeOpacity={0.6}
                animate={{ r: [4, 40], opacity: [0.6, 0] }}
                transition={{ duration: 4, delay: p.d, repeat: Infinity, ease: "easeOut" }}
              />
            )}
          </g>
        ))}
      </svg>

      {/* film grain */}
      <div className="absolute inset-0 noise" />
    </div>
  );
};
