import { useState } from "react";
import { ENV_LINES } from "@/lib/pulseData";

export const EnvSection = () => {
  const [redact, setRedact] = useState(false);
  const [copied, setCopied] = useState(false);
  const [hovered, setHovered] = useState<string | null>(null);

  const renderLines = () =>
    ENV_LINES.map((line) => {
      if (line.kind === "blank") return "";
      if (line.kind === "comment") return line.text;
      const v = redact ? "•".repeat(Math.min(line.value.length, 18)) : line.value;
      return `${line.key}=${v}`;
    }).join("\n");

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(renderLines());
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {}
  };

  return (
    <section id="env" className="relative border-t border-border py-24">
      <div className="container max-w-5xl">
        <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.18em] text-vital">
          <span className="h-px w-8 bg-vital" /> 04 · <span className="text-2">Configuration</span>
        </div>
        <h2 className="mt-3 font-display text-4xl font-extrabold tracking-tight md:text-5xl">
          One terminal. Every key.
        </h2>
        <p className="mt-3 max-w-xl text-[15px] font-light text-2">
          Hover any key to see exactly which module it powers. Toggle{" "}
          <span className="text-vital font-mono">redact</span> before screen-sharing.
        </p>

        <div className="mt-10 border border-border bg-surface overflow-hidden">
          {/* terminal title bar */}
          <div className="flex items-center gap-2 border-b border-border bg-surface-2 px-3 py-2">
            <div className="flex gap-1.5">
              <span className="size-2.5 rounded-full bg-alert-red/70" />
              <span className="size-2.5 rounded-full bg-alert-amber/70" />
              <span className="size-2.5 rounded-full bg-vital/70" />
            </div>
            <div className="ml-3 font-mono text-[11px] text-2 flex-1">
              pulse@ops:~/.env
            </div>
            <button
              onClick={() => setRedact((r) => !r)}
              className="font-mono text-[10px] uppercase tracking-wider px-2 py-1 border border-border text-2 hover:text-foreground hover:bg-surface-3 transition"
            >
              {redact ? "● Redact" : "○ Redact"}
            </button>
            <button
              onClick={copy}
              className="font-mono text-[10px] uppercase tracking-wider px-2 py-1 border border-vital/40 text-vital bg-vital/10 hover:bg-vital/20 transition"
            >
              {copied ? "✓ Copied" : "Copy"}
            </button>
          </div>

          {/* env body */}
          <div className="p-5 font-mono text-[12px] leading-relaxed overflow-x-auto">
            {ENV_LINES.map((line, i) => {
              if (line.kind === "blank") return <div key={i} className="h-4" aria-hidden />;
              if (line.kind === "comment") {
                return (
                  <div key={i} className="text-3 italic">{line.text}</div>
                );
              }
              const v = redact ? "•".repeat(Math.min(line.value.length, 24)) : line.value;
              const isHover = hovered === line.key;
              return (
                <div
                  key={i}
                  onMouseEnter={() => setHovered(line.key)}
                  onMouseLeave={() => setHovered(null)}
                  className={`group relative flex items-baseline gap-1 -mx-2 px-2 py-0.5 ${isHover ? "bg-vital/8" : ""}`}
                  style={{ background: isHover ? "hsl(var(--vital) / 0.06)" : undefined }}
                >
                  <span className="text-2 select-none w-8 text-right text-[10px] text-3">
                    {(i + 1).toString().padStart(2, "0")}
                  </span>
                  <span className="text-vital">{line.key}</span>
                  <span className="text-3">=</span>
                  <span className="text-foreground break-all">{v}</span>
                  {line.powers && isHover && (
                    <span className="ml-3 hidden md:inline-flex items-center gap-1 text-[10px] uppercase tracking-wider text-map-blue">
                      <span className="size-1 rounded-full bg-map-blue" />
                      powers: {line.powers}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <p className="mt-3 font-mono text-[11px] text-3">
          Generate JWT_SECRET →{" "}
          <code className="text-vital">
            python -c &quot;import secrets; print(secrets.token_hex(32))&quot;
          </code>
        </p>
      </div>
    </section>
  );
};
