"use client";

import { MapBackdrop } from "@/components/landing/MapBackdrop";
import { AnalyzeHeader } from "@/components/ingest/analyze-header";
import { PrescriptionIngest } from "@/components/ingest/prescription-ingest";

export default function AnalyzePage() {
  return (
    <div className="relative min-h-screen bg-background text-foreground">
      <MapBackdrop />
      <AnalyzeHeader />
      <main className="relative z-10 mx-auto max-w-4xl px-4 pb-20 pt-20 sm:px-6 sm:pt-24">
        <header className="mb-10 max-w-3xl border-l-2 border-vital pl-4">
          <h1 className="font-display text-3xl font-extrabold tracking-tight sm:text-4xl">Prescription ingest</h1>
          <p className="mt-2 font-mono text-[10px] uppercase leading-relaxed tracking-wider text-3">
            Multipart POST with fields <span className="text-vital">image</span> and{" "}
            <span className="text-vital">audio</span> — wire NEXT_PUBLIC_INGEST_URL to your API.
          </p>
        </header>
        <PrescriptionIngest />
      </main>
    </div>
  );
}
