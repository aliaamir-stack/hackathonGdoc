"use client";

import { MapBackdrop } from "@/components/landing/MapBackdrop";
import { AnalyzeHeader } from "@/components/ingest/analyze-header";
import { PrescriptionIngest } from "@/components/ingest/prescription-ingest";
import { PulseOperationalPanels } from "@/components/ingest/pulse-operational-panels";

export default function AnalyzePage() {
  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <MapBackdrop />
      <AnalyzeHeader />
      <main className="relative z-10 mx-auto max-w-4xl space-y-16 px-4 pb-24 pt-20 sm:px-6 sm:pt-24">
        <header className="max-w-3xl border-l-2 border-vital pl-4">
          <h1 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">Pulse clinical console</h1>
          <p className="mt-2 font-mono text-[10px] uppercase leading-relaxed tracking-wider text-3">
            Dashboard, outbreak stream, symptom assistant, medfact, field reports — then prescription scan (
            <span className="text-vital">/api/medicine/scan</span>) and emergency protocol (
            <span className="text-vital">/api/emergency/identify</span>).
          </p>
        </header>

        <PulseOperationalPanels />

        <div className="border-t border-border pt-12">
          <h2 className="mb-6 font-display text-2xl font-bold tracking-tight">Media analysis</h2>
          <PrescriptionIngest />
        </div>
      </main>
    </div>
  );
}
