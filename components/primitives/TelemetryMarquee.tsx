import { TELEMETRY } from "@/lib/pulseData";

export const TelemetryMarquee = () => {
  // Duplicate for seamless loop
  const items = [...TELEMETRY, ...TELEMETRY];
  return (
    <div className="relative overflow-hidden border-y border-border bg-surface/40 backdrop-blur-sm">
      <div className="flex gap-12 py-2 animate-marquee whitespace-nowrap font-mono text-[11px] text-2 will-change-transform">
        {items.map((t, i) => (
          <span key={i} className="flex items-center gap-2">
            <span className="size-1.5 rounded-full bg-vital animate-pulse-dot" />
            {t}
          </span>
        ))}
      </div>
      {/* edge fades */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-16 bg-gradient-to-r from-background to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-16 bg-gradient-to-l from-background to-transparent" />
    </div>
  );
};
