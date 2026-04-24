"use client";

import Link from "next/link";
import { ThemeToggle } from "@/components/chrome/theme-toggle";

export function AnalyzeHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-border bg-bg-deep/80 backdrop-blur-md">
      <div className="container flex h-12 max-w-6xl items-center justify-between gap-3">
        <Link
          href="/"
          className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-3 transition hover:text-vital"
        >
          <span className="size-2 shrink-0 rounded-full bg-vital" />
          <span className="font-display text-sm font-extrabold tracking-tight text-foreground">PULSE</span>
          <span className="hidden text-border sm:inline">/</span>
          <span className="hidden sm:inline">Home</span>
        </Link>
        <span className="font-mono text-[10px] uppercase tracking-wider text-vital">Ingest</span>
        <ThemeToggle />
      </div>
    </header>
  );
}
