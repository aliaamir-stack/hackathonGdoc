import { motion, useAnimationControls } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "@/hooks/use-reduced-motion";

type AmbulanceProps = {
  scale?: number;
  /** Drives wheel rotation when the ambulance is moving */
  rolling: boolean;
  /** Whether the lightbar should strobe */
  strobing: boolean;
};

/**
 * Side-profile ambulance, hand-built SVG. Geometric and clean, not cartoony.
 * Wheels rotate when `rolling` is true; light bar strobes when `strobing` true.
 */
export const Ambulance = ({ scale = 1, rolling, strobing }: AmbulanceProps) => {
  const reduced = useReducedMotion();
  return (
    <svg
      viewBox="0 0 320 140"
      width={320 * scale}
      height={140 * scale}
      aria-hidden
    >
      <defs>
        <linearGradient id="ambBody" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="hsl(200 20% 96%)" />
          <stop offset="1" stopColor="hsl(200 18% 84%)" />
        </linearGradient>
        <linearGradient id="ambCab" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="hsl(200 18% 90%)" />
          <stop offset="1" stopColor="hsl(200 16% 78%)" />
        </linearGradient>
        <linearGradient id="ambWindow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="hsl(210 60% 25%)" />
          <stop offset="1" stopColor="hsl(210 80% 12%)" />
        </linearGradient>
        <radialGradient id="headlight" cx="0%" cy="50%" r="100%">
          <stop offset="0" stopColor="hsl(50 100% 80%)" stopOpacity="1" />
          <stop offset="1" stopColor="hsl(50 100% 80%)" stopOpacity="0" />
        </radialGradient>
        <filter id="ambShadow" x="-20%" y="-20%" width="140%" height="160%">
          <feGaussianBlur stdDeviation="3" />
        </filter>
      </defs>

      {/* ground shadow */}
      <ellipse cx="160" cy="128" rx="130" ry="6" fill="hsl(210 80% 2%)" opacity="0.6" filter="url(#ambShadow)" />

      {/* main box body */}
      <rect x="80" y="40" width="190" height="60" rx="3" fill="url(#ambBody)" />
      {/* roof shadow line */}
      <rect x="80" y="40" width="190" height="3" fill="hsl(200 14% 70%)" />
      {/* belt line */}
      <rect x="80" y="76" width="190" height="2" fill="hsl(200 14% 72%)" />
      {/* red service stripe */}
      <rect x="80" y="78" width="190" height="6" fill="hsl(var(--alert-red))" opacity="0.85" />
      {/* cab */}
      <path d="M40 60 L80 60 L80 100 L40 100 Z" fill="url(#ambCab)" />
      <path d="M40 60 L80 60 L80 100 L52 100 Q40 100 40 88 Z" fill="url(#ambCab)" />
      {/* windshield */}
      <path d="M44 64 L78 64 L78 76 L44 76 Z" fill="url(#ambWindow)" stroke="hsl(200 14% 60%)" strokeWidth="0.5" />
      {/* side window of cab */}
      <rect x="56" y="80" width="22" height="14" fill="url(#ambWindow)" />
      {/* rear window squares */}
      {[110, 140, 170, 200, 230].map((x) => (
        <rect key={x} x={x} y="50" width="22" height="20" fill="url(#ambWindow)" stroke="hsl(200 14% 60%)" strokeWidth="0.5" />
      ))}
      {/* rear door split */}
      <line x1="262" y1="40" x2="262" y2="100" stroke="hsl(200 14% 60%)" strokeWidth="0.5" />

      {/* big medical cross */}
      <g transform="translate(168 56)">
        <rect x="-2" y="-12" width="4" height="24" fill="hsl(var(--alert-red))" />
        <rect x="-12" y="-2" width="24" height="4" fill="hsl(var(--alert-red))" />
      </g>
      {/* "PULSE" wordmark on side */}
      <text x="105" y="96" fontFamily="Syne, sans-serif" fontWeight="800" fontSize="9" fill="hsl(210 40% 20%)" letterSpacing="2">
        PULSE · MEDIC
      </text>

      {/* light bar on roof */}
      <g transform="translate(140 32)">
        <rect x="0" y="0" width="80" height="8" rx="1.5" fill="hsl(210 14% 30%)" />
        <rect
          x="2" y="1.5" width="36" height="5" rx="1"
          fill="hsl(var(--alert-red))"
          className={strobing ? "strobe-red" : ""}
          style={{ filter: strobing ? "drop-shadow(0 0 6px hsl(var(--alert-red)))" : undefined, opacity: strobing ? undefined : 0.4 }}
        />
        <rect
          x="42" y="1.5" width="36" height="5" rx="1"
          fill="hsl(var(--map-blue))"
          className={strobing ? "strobe-blue" : ""}
          style={{ filter: strobing ? "drop-shadow(0 0 6px hsl(var(--map-blue)))" : undefined, opacity: strobing ? undefined : 0.4 }}
        />
      </g>

      {/* headlight glow */}
      {!reduced && (
        <g transform="translate(40 84)">
          <ellipse cx="-30" cy="0" rx="40" ry="12" fill="url(#headlight)" opacity="0.5" />
        </g>
      )}
      {/* headlight bulb */}
      <circle cx="42" cy="84" r="2.2" fill="hsl(50 100% 80%)" />

      {/* door handles */}
      <rect x="58" y="84" width="6" height="1.5" fill="hsl(200 14% 50%)" />

      {/* wheels */}
      <Wheel cx={94} cy={104} rolling={rolling} />
      <Wheel cx={236} cy={104} rolling={rolling} />
    </svg>
  );
};

const Wheel = ({ cx, cy, rolling }: { cx: number; cy: number; rolling: boolean }) => {
  const reduced = useReducedMotion();
  const spin = rolling && !reduced;
  return (
    <g transform={`translate(${cx} ${cy})`}>
      <circle r="14" fill="hsl(210 14% 10%)" />
      <circle r="9" fill="hsl(210 14% 18%)" />
      <motion.g
        animate={spin ? { rotate: 360 } : { rotate: 0 }}
        transition={spin ? { duration: 0.6, repeat: Infinity, ease: "linear" } : undefined}
        style={{ transformOrigin: "0 0" }}
      >
        <rect x="-1" y="-9" width="2" height="18" fill="hsl(210 14% 32%)" />
        <rect x="-9" y="-1" width="18" height="2" fill="hsl(210 14% 32%)" />
        <rect x="-1" y="-9" width="2" height="18" fill="hsl(210 14% 32%)" transform="rotate(45)" />
        <rect x="-1" y="-9" width="2" height="18" fill="hsl(210 14% 32%)" transform="rotate(-45)" />
      </motion.g>
      <circle r="2" fill="hsl(210 14% 50%)" />
    </g>
  );
};

type Props = { onComplete: () => void };

/**
 * The full landing scene. Storyboard:
 * t=0     Quiet map, "ALERT INBOUND" mono caption fades in
 * t=0.6s  Ambulance enters from right, headlight cone sweeping
 * t=2.4s  Ambulance decelerates to center
 * t=3.0s  Lightbar starts strobing, suspension dip
 * t=3.6s  Pulse ring drops, expands outward
 * t=4.6s  PULSE wordmark assembles inside the ring
 * t=5.4s  Scene fades up & completes; ambulance shrinks into corner motif via parent
 */
export const AmbulanceIntro = ({ onComplete }: Props) => {
  const reduced = useReducedMotion();
  const [phase, setPhase] = useState<"driving" | "stopping" | "stopped" | "pulsing" | "branding" | "done">(
    "driving",
  );
  const ambControls = useAnimationControls();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (reduced) {
      // Skip the cinematic for accessibility — just fade out fast.
      const t = setTimeout(onComplete, 250);
      return () => clearTimeout(t);
    }
    let cancelled = false;
    (async () => {
      // Drive in fast from off-right (relative center anchor)
      await ambControls.start({
        x: 0,
        transition: { duration: 2.2, ease: [0.16, 0.4, 0.2, 1] },
      });
      if (cancelled) return;
      setPhase("stopping");
      // Suspension dip
      await ambControls.start({
        y: [0, 4, -2, 0],
        transition: { duration: 0.6, ease: "easeOut" },
      });
      if (cancelled) return;
      setPhase("stopped");
      await new Promise((r) => setTimeout(r, 350));
      if (cancelled) return;
      setPhase("pulsing");
      await new Promise((r) => setTimeout(r, 1100));
      if (cancelled) return;
      setPhase("branding");
      await new Promise((r) => setTimeout(r, 1400));
      if (cancelled) return;
      setPhase("done");
      await new Promise((r) => setTimeout(r, 400));
      if (cancelled) return;
      onComplete();
    })();
    return () => {
      cancelled = true;
    };
  }, [ambControls, onComplete, reduced]);

  return (
    <motion.div
      ref={containerRef}
      className="fixed inset-0 z-50 overflow-hidden bg-bg-deep"
      initial={{ opacity: 1 }}
      animate={phase === "done" ? { opacity: 0 } : { opacity: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {/* backdrop: faint map */}
      <div className="absolute inset-0 map-grid opacity-50" />
      <div className="absolute inset-0 map-grid-fine opacity-25" />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 20%, hsl(var(--bg-deep)) 80%)",
        }}
      />
      {/* horizon line — the road */}
      <div className="absolute left-0 right-0" style={{ top: "calc(50% + 70px)" }}>
        <div className="h-px w-full bg-gradient-to-r from-transparent via-border to-transparent" />
        <div className="mt-1 h-px w-full bg-gradient-to-r from-transparent via-border to-transparent opacity-50" />
      </div>

      {/* mono caption top-left */}
      <motion.div
        className="absolute left-6 top-6 font-mono text-[11px] uppercase tracking-[0.18em] text-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <div className="flex items-center gap-2">
          <span className="size-1.5 rounded-full bg-alert-red animate-pulse-dot" />
          <span>Karachi · 03:42 LOCAL · Alert inbound</span>
        </div>
        <div className="mt-1 text-3 text-[10px]">24.8607°N · 67.0011°E</div>
      </motion.div>

      {/* skip button */}
      <button
        onClick={onComplete}
        className="absolute right-6 top-6 z-10 rounded border border-border bg-surface/60 px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-2 backdrop-blur transition hover:bg-surface-2 hover:text-foreground"
      >
        Skip intro →
      </button>

      {/* the ambulance — anchored center, slides x:0 from off-right */}
      <motion.div
        className="absolute left-1/2 top-1/2"
        style={{ translateX: "-50%", translateY: "-50%" }}
      >
        <motion.div
          initial={{ x: typeof window !== "undefined" ? Math.max(900, window.innerWidth) : 1200 }}
          animate={ambControls}
          style={{ willChange: "transform" }}
        >
          {/* motion blur trail (pre-stop) */}
          {phase === "driving" && (
            <div
              className="absolute right-full top-1/2 h-12 w-64 -translate-y-1/2"
              style={{
                background:
                  "linear-gradient(90deg, transparent, hsl(var(--vital) / 0.18), hsl(200 20% 96% / 0.05))",
                filter: "blur(8px)",
              }}
            />
          )}
          <Ambulance
            scale={1.1}
            rolling={phase === "driving" || phase === "stopping"}
            strobing={phase === "stopped" || phase === "pulsing" || phase === "branding"}
          />
        </motion.div>
      </motion.div>

      {/* dropped pulse ring + wordmark, centered */}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        {(phase === "pulsing" || phase === "branding") && !reduced && (
          <>
            {[0, 0.25, 0.5].map((d, i) => (
              <motion.div
                key={i}
                className="absolute left-1/2 top-1/2 rounded-full"
                style={{
                  border: "1.5px solid hsl(var(--vital))",
                  translateX: "-50%",
                  translateY: "-50%",
                }}
                initial={{ width: 8, height: 8, opacity: 0.9 }}
                animate={{ width: 520, height: 520, opacity: 0 }}
                transition={{ duration: 1.6, delay: d, ease: "easeOut" }}
              />
            ))}
            <motion.div
              className="absolute left-1/2 top-1/2 rounded-full"
              style={{
                background: "radial-gradient(circle, hsl(var(--vital) / 0.5), transparent 70%)",
                translateX: "-50%",
                translateY: "-50%",
              }}
              initial={{ width: 0, height: 0, opacity: 1 }}
              animate={{ width: 240, height: 240, opacity: 0 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </>
        )}

        {phase === "branding" && (
          <motion.div
            className="relative text-center"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-vital">
              Situation Report · v1.0
            </div>
            <div className="mt-2 font-display text-[64px] font-extrabold leading-none tracking-tight text-foreground">
              PULSE
            </div>
            <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.24em] text-2">
              Public-health operations map
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
