import { startTransition, useEffect, useState } from "react";
import { SETUP_GROUPS } from "@/lib/pulseData";

const STORAGE_KEY = "pulse:setup-checked";

export const SetupSection = () => {
  const [checked, setChecked] = useState<Set<string>>(new Set());

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) startTransition(() => setChecked(new Set(JSON.parse(raw))));
    } catch {
      /* ignore */
    }
  }, []);

  const toggle = (id: string) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
      } catch {
        /* ignore */
      }
      return next;
    });
  };

  const total = SETUP_GROUPS.reduce((s, g) => s + g.items.length, 0);
  const done = SETUP_GROUPS.reduce(
    (s, g) => s + g.items.filter((it) => checked.has(it.id)).length, 0,
  );
  const pct = (done / total) * 100;

  return (
    <section id="setup" className="relative border-t border-border py-24">
      <div className="container max-w-5xl">
        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
          <span className="h-px w-8 bg-vital" /> 03 · <span className="text-2">Field setup</span>
        </div>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h2 className="font-display text-4xl font-extrabold tracking-tight md:text-5xl">
              Field operations checklist.
            </h2>
            <p className="mt-3 max-w-xl text-[15px] font-light text-2">
              Everything is free. Total cost: ₨0. Tick items as you collect them — your progress is saved locally.
            </p>
          </div>
          <div className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-wider text-2">
            <span>{done.toString().padStart(2, "0")} / {total.toString().padStart(2, "0")} collected</span>
            <div className="h-1.5 w-40 bg-surface-2 overflow-hidden">
              <div
                className="h-full bg-vital transition-all duration-500"
                style={{ width: `${pct}%`, boxShadow: "0 0 8px hsl(var(--vital))" }}
              />
            </div>
          </div>
        </div>

        <div className="mt-12 space-y-10">
          {SETUP_GROUPS.map((group) => (
            <div key={group.title}>
              <div className="flex items-center gap-3 mb-4">
                <span className="size-1.5 rounded-full bg-vital" />
                <h3 className="font-display text-sm font-bold uppercase tracking-wider text-2">
                  {group.title}
                </h3>
                <span className="h-px flex-1 bg-border" />
                <span className="font-mono text-[10px] text-3">
                  {group.items.filter((it) => checked.has(it.id)).length} / {group.items.length}
                </span>
              </div>
              <div className="grid gap-2 sm:grid-cols-2">
                {group.items.map((item) => {
                  const isChecked = checked.has(item.id);
                  return (
                    <button
                      key={item.id}
                      onClick={() => toggle(item.id)}
                      className="group flex items-start gap-3 border border-border bg-surface p-4 text-left transition hover:bg-surface-2"
                    >
                      {/* status indicator */}
                      <span className="mt-0.5 grid size-5 shrink-0 place-items-center border border-border">
                        {isChecked ? (
                          <span className="size-2.5 bg-vital" style={{ boxShadow: "0 0 6px hsl(var(--vital))" }} />
                        ) : (
                          <span className="size-1 rounded-full bg-3" />
                        )}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start gap-2">
                          <div className={`text-[13px] font-medium leading-snug ${isChecked ? "text-3 line-through" : "text-foreground"}`}>
                            {item.name}
                          </div>
                          <span className="ml-auto shrink-0 font-mono text-[9px] uppercase tracking-wider text-vital border border-vital/30 px-1.5 py-0.5">
                            {item.badge}
                          </span>
                        </div>
                        <div className="mt-1 text-[11px] text-3 leading-relaxed">{item.how}</div>
                        {item.link && (
                          <a
                            href={item.link} target="_blank" rel="noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="mt-1 inline-block font-mono text-[10px] text-map-blue hover:underline"
                          >
                            {item.link.replace(/^https?:\/\//, "")} →
                          </a>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
