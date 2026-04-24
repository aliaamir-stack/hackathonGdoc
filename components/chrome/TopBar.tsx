"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/chrome/theme-toggle";

const SECTIONS = [
  { id: "hero", label: "Hero" },
  { id: "features", label: "Modules" },
  { id: "stack", label: "Stack" },
  { id: "setup", label: "Setup" },
  { id: "env", label: "Env" },
  { id: "team", label: "Team" },
];

export const TopBar = ({ onReplayIntro }: { onReplayIntro: () => void }) => {
  const [active, setActive] = useState("hero");
  const [time, setTime] = useState("");

  useEffect(() => {
    const update = () => {
      const d = new Date();
      const hh = d.getHours().toString().padStart(2, "0");
      const mm = d.getMinutes().toString().padStart(2, "0");
      setTime(`${hh}:${mm} PKT`);
    };
    update();
    const t = setInterval(update, 30000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-40% 0px -55% 0px", threshold: 0 },
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-border bg-bg-deep/80 backdrop-blur-md">
      <div className="container flex h-12 max-w-6xl items-center gap-3 sm:gap-4">
        <a href="#hero" className="flex shrink-0 items-center gap-2">
          <span className="size-2 animate-pulse-dot rounded-full bg-vital" />
          <span className="font-display text-sm font-extrabold tracking-tight">PULSE</span>
          <span className="hidden font-mono text-[10px] uppercase tracking-wider text-3 sm:inline">
            v1.0
          </span>
        </a>

        <nav className="ml-2 hidden items-center gap-1 md:flex">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={`px-2 py-1 font-mono text-[10px] uppercase tracking-wider transition ${
                active === s.id ? "text-vital" : "text-3 hover:text-2"
              }`}
            >
              {s.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-3 sm:gap-3">
          <Link
            href="/analyze"
            className="border border-border px-2 py-1 transition hover:border-vital hover:text-vital"
          >
            Analyze
          </Link>
          <span className="hidden sm:inline">{time}</span>
          <span className="hidden text-border sm:inline">·</span>
          <span className="hidden lg:inline">Karachi 28°C</span>
          <button
            type="button"
            onClick={onReplayIntro}
            className="border border-border px-2 py-1 transition hover:border-vital hover:text-vital"
          >
            Replay intro
          </button>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
};
