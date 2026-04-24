import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { LivePulseLine } from "@/components/primitives/LivePulseLine";
import { TelemetryMarquee } from "@/components/primitives/TelemetryMarquee";
import { Ambulance } from "@/components/landing/AmbulanceIntro";
import { STATS } from "@/lib/pulseData";

const useCountUp = (target: number, duration = 1200) => {
  const [v, setV] = useState(0);
  useEffect(() => {
    let raf: number;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setV(target * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  return v;
};

const StatTile = ({ num, label, idx }: { num: string; label: string; idx: number }) => {
  // Try to extract a numeric prefix for count-up.
  const numeric = parseFloat(num.replace(/[^\d.]/g, ""));
  const v = useCountUp(isFinite(numeric) ? numeric : 0);
  const display = isFinite(numeric)
    ? num.replace(/[\d.]+/, num.includes(".") ? v.toFixed(1) : Math.round(v).toString().padStart(num.match(/^0\d/) ? 2 : 1, "0"))
    : num;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 + idx * 0.1 }}
      className="relative border border-border bg-surface/60 backdrop-blur p-4"
    >
      <div className="absolute left-0 top-0 h-px w-6 bg-vital" />
      <div className="font-display text-3xl font-extrabold text-vital leading-none">
        {display}
      </div>
      <div className="mt-1 font-mono text-[10px] uppercase tracking-wider text-3">{label}</div>
    </motion.div>
  );
};

export const HeroSection = () => {
  return (
    <section id="hero" className="relative pt-24 pb-0">
      <div className="container max-w-5xl">
        {/* eyebrow */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-center"
        >
          <div className="inline-flex items-center gap-2 border border-vital/30 bg-vital/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
            <span className="size-1.5 rounded-full bg-vital animate-pulse-dot" />
            System online · 7 modules · Karachi node
          </div>
        </motion.div>

        {/* wordmark with vital line through it */}
        <div className="relative mt-8">
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="font-display text-center font-extrabold leading-[0.9] tracking-tighter"
            style={{ fontSize: "clamp(64px, 12vw, 168px)" }}
          >
            PUL<span className="text-vital">S</span>E
          </motion.h1>
          {/* ECG line slicing horizontally through the wordmark */}
          <div
            className="pointer-events-none absolute inset-x-0"
            style={{ top: "50%", transform: "translateY(-50%)" }}
          >
            <LivePulseLine width={1200} height={80} className="w-full h-20 opacity-90" hero />
          </div>
        </div>

        {/* sub */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mx-auto mt-8 max-w-xl text-center text-[17px] font-light text-2"
        >
          A real-time public-health operations map for Pakistan.
          Seven modules. Six operators. Fifteen hours. ₨0 in spend.
          Built to be on a phone the moment something goes wrong.
        </motion.p>

        {/* coordinates */}
        <div className="mt-6 flex justify-center gap-4 font-mono text-[10px] uppercase tracking-wider text-3">
          <span>24.86°N</span><span className="text-border">·</span>
          <span>67.00°E</span><span className="text-border">·</span>
          <span>uplink stable</span>
        </div>

        {/* stats */}
        <div className="mx-auto mt-12 grid max-w-3xl grid-cols-2 gap-3 sm:grid-cols-4">
          {STATS.map((s, i) => <StatTile key={s.label} {...s} idx={i} />)}
        </div>

        {/* parked ambulance, smaller, lower-right */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 1.4 }}
          className="pointer-events-none mx-auto mt-12 flex max-w-3xl justify-end"
        >
          <div className="opacity-80">
            <Ambulance scale={0.5} rolling={false} strobing />
          </div>
        </motion.div>
      </div>

      <div className="mt-6">
        <TelemetryMarquee />
      </div>
    </section>
  );
};
