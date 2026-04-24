"use client";

import { startTransition, useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { MapBackdrop } from "@/components/landing/MapBackdrop";
import { AmbulanceIntro } from "@/components/landing/AmbulanceIntro";
import { TopBar } from "@/components/chrome/TopBar";
import { SyringeProgress } from "@/components/chrome/SyringeProgress";
import { MiniMap } from "@/components/chrome/MiniMap";
import { HeroSection } from "@/components/sections/HeroSection";
import { FeaturesSection } from "@/components/sections/FeaturesSection";
import { StackSection } from "@/components/sections/StackSection";
import { SetupSection } from "@/components/sections/SetupSection";
import { EnvSection } from "@/components/sections/EnvSection";
import { TeamSection } from "@/components/sections/TeamSection";

const INTRO_KEY = "pulse:intro-played";

export function PulseHome() {
  const [showIntro, setShowIntro] = useState(false);

  useEffect(() => {
    const played = sessionStorage.getItem(INTRO_KEY);
    if (!played) startTransition(() => setShowIntro(true));
  }, []);

  const finishIntro = () => {
    sessionStorage.setItem(INTRO_KEY, "1");
    setShowIntro(false);
  };

  const replayIntro = () => {
    sessionStorage.removeItem(INTRO_KEY);
    setShowIntro(true);
  };

  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <MapBackdrop />
      <TopBar onReplayIntro={replayIntro} />
      <SyringeProgress />
      <MiniMap />

      <AnimatePresence>
        {showIntro && <AmbulanceIntro key="intro" onComplete={finishIntro} />}
      </AnimatePresence>

      <main className="relative z-10">
        <HeroSection />
        <FeaturesSection />
        <StackSection />
        <SetupSection />
        <EnvSection />
        <TeamSection />

        <footer className="relative border-t border-border py-12">
          <div className="container flex max-w-6xl flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-wider text-3">
            <div className="flex items-center gap-2">
              <span className="size-1.5 animate-pulse-dot rounded-full bg-vital" />
              PULSE Ops · Situation Report v1.0
            </div>
            <div>End of transmission · 24.86°N · 67.00°E</div>
          </div>
        </footer>
      </main>
    </div>
  );
}
