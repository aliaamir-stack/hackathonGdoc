import { motion } from "framer-motion";
import { useState } from "react";
import { FEATURES } from "@/lib/pulseData";
import { MapPin, accentColor, accentColorAlpha } from "@/components/primitives/MapPin";

const SectionTag = ({ index, label }: { index: string; label: string }) => (
  <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
    <span className="h-px w-8 bg-vital" />
    <span>{index}</span>
    <span className="text-3">·</span>
    <span className="text-2">{label}</span>
  </div>
);

export const FeaturesSection = () => {
  const [active, setActive] = useState<string>(FEATURES[0].id);
  const activeFeature = FEATURES.find((f) => f.id === active)!;

  return (
    <section id="features" className="relative border-t border-border py-24">
      <div className="container max-w-6xl">
        <SectionTag index="01" label="Modules" />
        <h2 className="mt-3 font-display text-4xl font-extrabold tracking-tight md:text-5xl">
          Seven pins. One operations map.
        </h2>
        <p className="mt-3 max-w-xl text-[15px] font-light text-2">
          Every module is geo-located on the map of what PULSE actually does.
          Hover or tap a pin to lock in its mission profile.
        </p>

        <div className="mt-12 grid grid-cols-1 gap-6 lg:grid-cols-[1fr_360px]">
          {/* MAP — left */}
          <div
            className="relative aspect-[4/3] border border-border bg-surface/40 backdrop-blur-sm overflow-hidden"
            style={{
              background:
                "radial-gradient(ellipse at center, hsl(var(--surface)) 0%, hsl(var(--bg-deep)) 100%)",
            }}
          >
            {/* faint Pakistan-shaped silhouette */}
            <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full" preserveAspectRatio="none" aria-hidden>
              <defs>
                <pattern id="featGrid" width="6" height="6" patternUnits="userSpaceOnUse">
                  <path d="M 6 0 L 0 0 0 6" fill="none" stroke="hsl(var(--grid))" strokeWidth="0.2" />
                </pattern>
              </defs>
              <rect width="100" height="100" fill="url(#featGrid)" />
              {/* abstract Pakistan blob */}
              <path
                d="M18 22 Q14 36 22 50 Q12 60 24 72 Q22 86 36 88 Q50 92 60 84 Q76 88 80 72 Q92 64 86 50 Q94 36 78 26 Q66 16 52 18 Q38 12 28 18 Z"
                fill="hsl(var(--surface-2))"
                stroke="hsl(var(--border))"
                strokeWidth="0.2"
                opacity="0.7"
              />
            </svg>

            {/* leader lines from active pin */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden>
              {FEATURES.filter((f) => f.id === active).map((f) => (
                <g key={f.id}>
                  <line
                    x1={f.x} y1={f.y} x2={f.x + 12} y2={f.y - 8}
                    stroke={accentColor(f.accent)} strokeWidth="0.15" strokeDasharray="0.5 0.5"
                  />
                </g>
              ))}
            </svg>

            {/* pins */}
            {FEATURES.map((f) => {
              const isActive = f.id === active;
              return (
                <button
                  key={f.id}
                  onClick={() => setActive(f.id)}
                  onMouseEnter={() => setActive(f.id)}
                  className="absolute group"
                  style={{
                    left: `${f.x}%`,
                    top: `${f.y}%`,
                    transform: "translate(-50%, -50%)",
                    opacity: isActive ? 1 : 0.55,
                    transition: "opacity 200ms",
                  }}
                  aria-label={f.title}
                >
                  <MapPin accent={f.accent} size={isActive ? 24 : 18} active={isActive} />
                  {/* coord chip */}
                  <span
                    className="absolute left-1/2 top-full mt-2 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] uppercase tracking-wider"
                    style={{ color: isActive ? accentColor(f.accent) : "hsl(var(--text-3))" }}
                  >
                    {f.num} · {f.title.split(" ")[0]}
                  </span>
                </button>
              );
            })}

            {/* radar sweep on active pin */}
            <div
              className="pointer-events-none absolute"
              style={{
                left: `${activeFeature.x}%`,
                top: `${activeFeature.y}%`,
                width: 240,
                height: 240,
                transform: "translate(-50%,-50%)",
                background: `conic-gradient(from 0deg, ${accentColorAlpha(activeFeature.accent, 0.18)}, transparent 30%)`,
                borderRadius: "50%",
                opacity: 0.4,
              }}
            >
              <div className="w-full h-full animate-radar" style={{
                background: `conic-gradient(from 0deg, ${accentColorAlpha(activeFeature.accent, 0.25)}, transparent 25%)`,
                borderRadius: "50%",
              }} />
            </div>

            {/* corner readouts */}
            <div className="absolute left-3 top-3 font-mono text-[9px] uppercase tracking-wider text-3">
              MAP · 1:50k · OSM
            </div>
            <div className="absolute right-3 top-3 font-mono text-[9px] uppercase tracking-wider text-3">
              REC · 7 PINS
            </div>
            <div className="absolute left-3 bottom-3 font-mono text-[9px] uppercase tracking-wider text-3">
              N ↑
            </div>
          </div>

          {/* CARD — right */}
          <motion.div
            key={activeFeature.id}
            initial={{ opacity: 0, x: 8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            className="relative border border-border bg-surface p-6 self-start"
            style={{
              boxShadow: `inset 2px 0 0 ${accentColor(activeFeature.accent)}`,
            }}
          >
            <div className="flex items-baseline justify-between font-mono text-[10px] uppercase tracking-wider text-3">
              <span>MODULE {activeFeature.num}</span>
              <span style={{ color: accentColor(activeFeature.accent) }}>● ACTIVE</span>
            </div>
            <div className="mt-3 flex items-center gap-3">
              <span
                className="grid size-10 place-items-center font-display text-xl"
                style={{
                  color: accentColor(activeFeature.accent),
                  background: accentColorAlpha(activeFeature.accent, 0.12),
                  border: `1px solid ${accentColorAlpha(activeFeature.accent, 0.3)}`,
                }}
              >
                {activeFeature.icon}
              </span>
              <h3 className="font-display text-2xl font-bold">{activeFeature.title}</h3>
            </div>
            <p className="mt-3 text-[14px] text-2">{activeFeature.desc}</p>
            <div
              className="mt-4 inline-block font-mono text-[10px] uppercase tracking-wider px-2 py-1"
              style={{
                color: accentColor(activeFeature.accent),
                background: accentColorAlpha(activeFeature.accent, 0.12),
              }}
            >
              {activeFeature.tech}
            </div>

            {/* mini pin selector */}
            <div className="mt-6 border-t border-border pt-4">
              <div className="font-mono text-[10px] uppercase tracking-wider text-3 mb-2">
                Switch module
              </div>
              <div className="flex flex-wrap gap-1.5">
                {FEATURES.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => setActive(f.id)}
                    className="font-mono text-[10px] px-2 py-1 border transition"
                    style={{
                      borderColor: f.id === active ? accentColor(f.accent) : "hsl(var(--border))",
                      color: f.id === active ? accentColor(f.accent) : "hsl(var(--text-2))",
                      background: f.id === active ? accentColorAlpha(f.accent, 0.1) : "transparent",
                    }}
                  >
                    {f.num}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
