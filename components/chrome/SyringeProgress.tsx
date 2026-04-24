import { useEffect, useState } from "react";

export const SyringeProgress = () => {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      setPct(h > 0 ? (window.scrollY / h) * 100 : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="hidden xl:flex fixed right-6 top-1/2 -translate-y-1/2 z-30 flex-col items-center gap-2 pointer-events-none">
      <div className="font-mono text-[9px] uppercase tracking-wider text-3">Dose</div>
      {/* syringe body */}
      <div className="relative w-3 h-64 border border-border bg-surface overflow-hidden">
        <div
          className="absolute bottom-0 left-0 right-0 bg-vital transition-[height] duration-150"
          style={{ height: `${pct}%`, boxShadow: "0 0 8px hsl(var(--vital))" }}
        />
        {/* tick marks */}
        {[25, 50, 75].map((t) => (
          <div
            key={t}
            className="absolute left-0 right-0 h-px bg-border"
            style={{ bottom: `${t}%` }}
          />
        ))}
      </div>
      {/* needle */}
      <div className="w-px h-8 bg-border" />
      <div className="font-mono text-[9px] tabular-nums text-vital">
        {Math.round(pct).toString().padStart(2, "0")}%
      </div>
    </div>
  );
};
