import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { MEMBERS, type Member } from "@/lib/pulseData";
import { accentColor, accentColorAlpha } from "@/components/primitives/MapPin";

export const TeamSection = () => {
  const [activeId, setActiveId] = useState<number>(2);
  const active = MEMBERS.find((m) => m.id === activeId)!;

  // war-room circle layout
  const RADIUS = 150;
  const positions = MEMBERS.map((m) => {
    const rad = (m.angle - 90) * (Math.PI / 180);
    return {
      m,
      x: 50 + (RADIUS / 380) * 100 * Math.cos(rad),
      y: 50 + (RADIUS / 380) * 100 * Math.sin(rad),
    };
  });

  const activePos = positions.find((p) => p.m.id === activeId)!;

  return (
    <section id="team" className="relative border-t border-border py-24">
      <div className="container max-w-6xl">
        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
          <span className="h-px w-8 bg-vital" /> 05 · <span className="text-2">Operations roster</span>
        </div>
        <h2 className="mt-3 font-display text-4xl font-extrabold tracking-tight md:text-5xl">
          The six who ship it.
        </h2>
        <p className="mt-3 max-w-xl text-[15px] font-light text-2">
          15 hours. Each station has a role, a timeline, and a list of dependencies on the others.
        </p>

        <div className="mt-12 grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-8">
          {/* WAR ROOM */}
          <div className="relative aspect-square border border-border bg-surface/40 overflow-hidden">
            <div className="absolute inset-0 map-grid-fine opacity-30" />
            {/* center label */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
              <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-3">War room</div>
              <div className="mt-1 font-display text-2xl font-extrabold text-vital">15h</div>
              <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-3">to demo</div>
            </div>
            {/* pulsing center ring */}
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-32 rounded-full border border-vital/20" />
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 size-48 rounded-full border border-border" />

            {/* dependency lines from active */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
              {active.deps.map((depId) => {
                const dep = positions.find((p) => p.m.id === depId);
                if (!dep) return null;
                return (
                  <line
                    key={depId}
                    x1={activePos.x} y1={activePos.y}
                    x2={dep.x} y2={dep.y}
                    stroke={accentColor(active.accent)}
                    strokeWidth="0.2"
                    strokeDasharray="0.6 0.6"
                    opacity="0.7"
                  />
                );
              })}
            </svg>

            {/* member dots */}
            {positions.map(({ m, x, y }) => {
              const isActive = m.id === activeId;
              const isDep = active.deps.includes(m.id);
              const c = accentColor(m.accent);
              return (
                <button
                  key={m.id}
                  onClick={() => setActiveId(m.id)}
                  className="absolute"
                  style={{
                    left: `${x}%`, top: `${y}%`,
                    transform: "translate(-50%, -50%)",
                  }}
                >
                  <div
                    className="grid size-12 place-items-center font-display font-bold text-sm transition"
                    style={{
                      background: isActive ? c : accentColorAlpha(m.accent, 0.12),
                      color: isActive ? "hsl(var(--bg-deep))" : c,
                      border: `1px solid ${c}`,
                      boxShadow: isActive ? `0 0 24px ${c}` : isDep ? `0 0 0 2px ${c}` : "none",
                    }}
                  >
                    {m.code}
                  </div>
                  <div
                    className="absolute left-1/2 top-full mt-1 -translate-x-1/2 whitespace-nowrap font-mono text-[9px] uppercase tracking-wider"
                    style={{ color: isActive ? c : "hsl(var(--text-3))" }}
                  >
                    {m.role}
                  </div>
                </button>
              );
            })}
          </div>

          {/* DETAIL PANEL */}
          <AnimatePresence mode="wait">
            <motion.div
              key={active.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.25 }}
              className="border border-border bg-surface"
              style={{ boxShadow: `inset 3px 0 0 ${accentColor(active.accent)}` }}
            >
              {/* header */}
              <div className="border-b border-border p-5">
                <div className="flex items-baseline justify-between font-mono text-[10px] uppercase tracking-wider text-3">
                  <span>Station {active.code} · operator profile</span>
                  <span style={{ color: accentColor(active.accent) }}>● ON DUTY</span>
                </div>
                <h3 className="mt-2 font-display text-2xl font-bold">
                  {active.code} — {active.name}
                </h3>
                <div className="font-mono text-[11px] text-2 mt-1">{active.stack}</div>
              </div>

              {/* warn */}
              <MemberWarn member={active} />

              {/* timeline ribbon */}
              <div className="p-5">
                <div className="font-mono text-[10px] uppercase tracking-wider text-3 mb-3">
                  Hour-by-hour timeline
                </div>
                <div className="space-y-1.5">
                  {active.tasks.map((t, i) => (
                    <div
                      key={i}
                      className="grid grid-cols-[110px_1fr] gap-3 border-l-2 border-border pl-3 py-2"
                      style={{ borderColor: i === 0 ? accentColor(active.accent) : undefined }}
                    >
                      <div className="font-mono text-[10px] uppercase tracking-wider text-2 pt-0.5">
                        {t.time}
                      </div>
                      <div>
                        <div className="text-[13px] text-foreground leading-relaxed">{t.text}</div>
                        {t.cmd && (
                          <div className="mt-1.5 font-mono text-[11px] text-vital bg-bg-deep border border-border p-2 overflow-x-auto">
                            $ {t.cmd}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* needs */}
              <div className="border-t border-border p-5">
                <div className="font-mono text-[10px] uppercase tracking-wider text-3 mb-3">
                  What you need to collect
                </div>
                <div className="grid gap-2 sm:grid-cols-2">
                  {active.needs.map((n) => (
                    <div key={n.name} className="border border-border bg-surface-2 p-3">
                      <div className="text-[12px] font-medium text-foreground">{n.name}</div>
                      <div className="mt-1 text-[11px] text-3 leading-relaxed">{n.how}</div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

const MemberWarn = ({ member }: { member: Member }) => {
  const c = accentColor(member.accent);
  return (
    <div
      className="m-5 mt-0 border-l-2 p-3 text-[12px] leading-relaxed"
      style={{
        borderColor: c,
        background: accentColorAlpha(member.accent, 0.08),
        color: "hsl(var(--text-1))",
      }}
    >
      <span className="font-mono text-[10px] uppercase tracking-wider mr-2" style={{ color: c }}>
        ⚡ Brief
      </span>
      {member.warn}
    </div>
  );
};
