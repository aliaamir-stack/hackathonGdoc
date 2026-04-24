import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { STACK } from "@/lib/pulseData";
import { accentColor, accentColorAlpha } from "@/components/primitives/MapPin";

export const StackSection = () => {
  const [open, setOpen] = useState<string | null>("backend");

  return (
    <section id="stack" className="relative border-t border-border py-24">
      <div className="container max-w-5xl">
        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
          <span className="h-px w-8 bg-vital" /> 02 · <span className="text-2">Architecture</span>
        </div>
        <h2 className="mt-3 font-display text-4xl font-extrabold tracking-tight md:text-5xl">
          The strata, top to bottom.
        </h2>
        <p className="mt-3 max-w-xl text-[15px] font-light text-2">
          Six layers. Every tool chosen to be free, fast, and demo-ready. Tap a layer to drill in.
        </p>

        <div className="mt-12 space-y-2">
          {STACK.map((layer, i) => {
            const isOpen = open === layer.id;
            const c = accentColor(layer.accent);
            return (
              <motion.div
                key={layer.id}
                layout
                transition={{ layout: { duration: 0.35, ease: [0.4, 0, 0.2, 1] } }}
                className="relative overflow-hidden border border-border bg-surface"
                style={{ boxShadow: isOpen ? `inset 3px 0 0 ${c}` : `inset 1px 0 0 ${c}` }}
              >
                <button
                  onClick={() => setOpen(isOpen ? null : layer.id)}
                  className="flex w-full items-center gap-4 p-5 text-left transition hover:bg-surface-2"
                >
                  {/* layer index */}
                  <span className="font-mono text-[10px] uppercase tracking-wider text-3 w-6">
                    L{(STACK.length - i).toString().padStart(2, "0")}
                  </span>
                  {/* pulsing node */}
                  <span className="relative grid place-items-center">
                    <span className="size-2.5 rounded-full" style={{ background: c }} />
                    {isOpen && (
                      <motion.span
                        className="absolute size-2.5 rounded-full"
                        style={{ border: `1px solid ${c}` }}
                        animate={{ scale: [1, 3], opacity: [0.6, 0] }}
                        transition={{ duration: 1.6, repeat: Infinity, ease: "easeOut" }}
                      />
                    )}
                  </span>
                  <span className="flex-1">
                    <span className="font-display text-base font-bold">{layer.label}</span>
                    <span className="ml-3 font-mono text-[11px] text-3 hidden sm:inline">
                      {layer.meta}
                    </span>
                  </span>
                  {/* live tag */}
                  <span
                    className="hidden md:inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider px-2 py-1"
                    style={{ color: c, background: accentColorAlpha(layer.accent, 0.1) }}
                  >
                    <span className="size-1 rounded-full animate-pulse-dot" style={{ background: c }} />
                    {layer.liveTag}
                  </span>
                  <span className="font-mono text-base text-3">{isOpen ? "−" : "+"}</span>
                </button>

                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      key="body"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
                      className="overflow-hidden border-t border-border"
                    >
                      <div className="p-5">
                        <div className="flex flex-wrap gap-2">
                          {layer.pills.map((p) => (
                            <span
                              key={p.name}
                              className="font-mono text-[11px] px-2.5 py-1 border"
                              style={{
                                borderColor: p.primary ? accentColorAlpha(layer.accent, 0.4) : "hsl(var(--border))",
                                color: p.primary ? c : "hsl(var(--text-2))",
                                background: p.primary ? accentColorAlpha(layer.accent, 0.08) : "hsl(var(--surface-2))",
                              }}
                            >
                              {p.name}
                            </span>
                          ))}
                        </div>
                        <p className="mt-4 italic text-[12px] text-3 leading-relaxed">
                          {layer.note}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
