import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ingest — PULSE",
  description: "Upload prescription imagery and optional audio for backend processing.",
};

export default function AnalyzeLayout({ children }: { children: React.ReactNode }) {
  return children;
}
