import { motion } from "framer-motion";
import type { AccentKey } from "@/lib/pulseData";

const accentVar: Record<AccentKey, string> = {
  vital: "var(--vital)",
  "map-blue": "var(--map-blue)",
  "alert-red": "var(--alert-red)",
  "alert-amber": "var(--alert-amber)",
  "signal-purple": "var(--signal-purple)",
  "signal-teal": "var(--signal-teal)",
};

export const accentColor = (a: AccentKey) => `hsl(${accentVar[a]})`;
export const accentColorAlpha = (a: AccentKey, alpha: number) =>
  `hsl(${accentVar[a]} / ${alpha})`;

type Props = {
  accent: AccentKey;
  size?: number;
  active?: boolean;
  label?: string;
};

export const MapPin = ({ accent, size = 20, active, label }: Props) => {
  const c = accentColor(accent);
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* expanding ring */}
      <motion.span
        className="absolute inset-0 rounded-full"
        style={{ border: `1px solid ${c}` }}
        animate={{ scale: [1, 2.4], opacity: [0.6, 0] }}
        transition={{ duration: 2.4, repeat: Infinity, ease: "easeOut" }}
      />
      <span
        className="absolute inset-0 rounded-full"
        style={{ background: c, opacity: active ? 0.25 : 0.12 }}
      />
      <span
        className="rounded-full"
        style={{
          width: size / 2.5,
          height: size / 2.5,
          background: c,
          boxShadow: active
            ? `0 0 16px ${c}, 0 0 0 2px ${c}`
            : `0 0 8px ${c}`,
        }}
      />
      {label && (
        <span
          className="absolute left-full ml-2 font-mono text-[10px] uppercase tracking-wider whitespace-nowrap"
          style={{ color: c }}
        >
          {label}
        </span>
      )}
    </div>
  );
};
