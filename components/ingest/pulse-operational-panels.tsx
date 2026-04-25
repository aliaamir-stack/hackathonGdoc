"use client";

import { startTransition, useCallback, useEffect, useId, useMemo, useState } from "react";
import {
  fetchDashboardStats,
  fetchOutbreakData,
  getPulseApiOrigin,
  postMedFactVerify,
  postSymptomsChat,
  postSymptomsReport,
} from "@/lib/pulse-api/client";
import type {
  DashboardStats,
  MedFactVerifyResponse,
  OutbreakDataResponse,
  SymptomsChatResponse,
} from "@/lib/pulse-api/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { useOutbreakWs } from "@/hooks/use-outbreak-ws";
import { Activity, Globe, MessageSquare, Radio, ShieldCheck, Stethoscope } from "lucide-react";

function StatEntries({ data }: { data: DashboardStats | null }) {
  if (!data || typeof data !== "object") {
    return <p className="font-mono text-xs text-3">No stats payload or empty object.</p>;
  }
  const entries = Object.entries(data);
  if (!entries.length) return <p className="font-mono text-xs text-3">Empty stats object.</p>;
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {entries.map(([k, v]) => (
        <div key={k} className="rounded-md border border-border bg-bg-deep/40 p-3">
          <p className="font-mono text-[9px] uppercase tracking-wider text-3">{k}</p>
          <p className="mt-1 font-mono text-sm text-vital">{typeof v === "object" ? JSON.stringify(v) : String(v)}</p>
        </div>
      ))}
    </div>
  );
}

export function PulseOperationalPanels() {
  const id = useId();
  const [dash, setDash] = useState<DashboardStats | null>(null);
  const [dashErr, setDashErr] = useState<string | null>(null);
  const [outbreak, setOutbreak] = useState<OutbreakDataResponse | null>(null);
  const [outbreakErr, setOutbreakErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [sessionId] = useState(() =>
    typeof crypto !== "undefined" && crypto.randomUUID ? crypto.randomUUID() : `sess-${Date.now()}`,
  );
  const [chatInput, setChatInput] = useState("");
  const [chatOut, setChatOut] = useState<SymptomsChatResponse | null>(null);
  const [chatErr, setChatErr] = useState<string | null>(null);
  const [chatBusy, setChatBusy] = useState(false);

  const [claim, setClaim] = useState("");
  const [medFact, setMedFact] = useState<MedFactVerifyResponse | null>(null);
  const [medFactErr, setMedFactErr] = useState<string | null>(null);
  const [medFactBusy, setMedFactBusy] = useState(false);

  const [symptomsLine, setSymptomsLine] = useState("fever, headache");
  const [lat, setLat] = useState("24.8607");
  const [lng, setLng] = useState("67.0011");
  const [urgency, setUrgency] = useState("4");
  const [district, setDistrict] = useState("Karachi South");
  const [reportMsg, setReportMsg] = useState<string | null>(null);
  const [reportBusy, setReportBusy] = useState(false);

  const { connected, lastMessage, error: wsError } = useOutbreakWs(true);

  const load = useCallback(async () => {
    startTransition(() => {
      setLoading(true);
      setDashErr(null);
      setOutbreakErr(null);
    });
    const [d, o] = await Promise.all([fetchDashboardStats(), fetchOutbreakData()]);
    startTransition(() => {
      if (d.ok) setDash(d.data);
      else setDashErr(d.message);
      if (o.ok) setOutbreak(o.data);
      else setOutbreakErr(o.message);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    startTransition(() => {
      void load();
    });
  }, [load]);

  const origin = useMemo(() => getPulseApiOrigin(), []);

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    setChatBusy(true);
    setChatErr(null);
    const r = await postSymptomsChat({
      message: chatInput.trim(),
      session_id: sessionId,
      language: "en",
    });
    setChatBusy(false);
    if (r.ok) setChatOut(r.data);
    else setChatErr(r.message);
  };

  const sendMedFact = async () => {
    if (!claim.trim()) return;
    setMedFactBusy(true);
    setMedFactErr(null);
    const r = await postMedFactVerify({ claim: claim.trim() });
    setMedFactBusy(false);
    if (r.ok) setMedFact(r.data);
    else setMedFactErr(r.message);
  };

  const sendReport = async () => {
    setReportBusy(true);
    setReportMsg(null);
    const symptoms = symptomsLine
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const r = await postSymptomsReport({
      symptoms,
      latitude: Number(lat) || 0,
      longitude: Number(lng) || 0,
      urgency_level: Number(urgency) || 0,
      district: district.trim() || "Unknown",
    });
    setReportBusy(false);
    if (r.ok) setReportMsg("Report saved.");
    else setReportMsg(r.message);
  };

  return (
    <div className="space-y-8">
      <div className="rounded-md border border-border bg-bg-deep/30 p-4 font-mono text-[10px] uppercase tracking-wider text-3">
        API origin: <span className="text-vital">{origin}</span>
        <span className="mx-2 text-border">·</span>
        Set <span className="text-foreground">NEXT_PUBLIC_PULSE_API_BASE</span> if different
      </div>

      {/* Dashboard + outbreak (doc primary dashboard) */}
      <Card className="border-border bg-surface/40">
        <CardHeader className="border-b border-border">
          <CardTitle className="flex items-center gap-2 font-display text-lg">
            <Activity className="size-5 text-vital" />
            Live operations
          </CardTitle>
          <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
            GET /api/dashboard/stats · GET /api/outbreak/data · WS /ws/outbreak
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-8 pt-6">
          {loading ? <p className="font-mono text-xs text-3">Loading dashboard & outbreak…</p> : null}

          <div>
            <h3 className="mb-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-vital">
              <ShieldCheck className="size-4" />
              Dashboard stats
            </h3>
            {dashErr ? <p className="text-sm text-alert-red">{dashErr}</p> : <StatEntries data={dash} />}
          </div>

          <Separator />

          <div>
            <h3 className="mb-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-map-blue">
              <Globe className="size-4" />
              Outbreak data
            </h3>
            {outbreakErr ? (
              <p className="text-sm text-alert-red">{outbreakErr}</p>
            ) : outbreak ? (
              <div className="space-y-4">
                <p className="font-mono text-[10px] uppercase text-3">
                  Last updated: <span className="text-foreground">{outbreak.last_updated}</span>
                </p>
                <div className="grid gap-3 sm:grid-cols-2">
                  {outbreak.clusters?.map((c, i) => (
                    <div key={i} className="rounded-md border border-border bg-bg-deep/40 p-3">
                      <p className="font-mono text-[9px] uppercase text-3">Cluster {i + 1}</p>
                      <p className="mt-1 text-sm text-foreground">
                        {c.center_lat.toFixed(2)}°, {c.center_lng.toFixed(2)}° · size {c.size}
                      </p>
                      <Badge className="mt-2" variant="outline">
                        {c.dominant_symptom}
                      </Badge>
                    </div>
                  ))}
                </div>
                <p className="font-mono text-[10px] text-3">
                  Heatmap points: {outbreak.heatmap_points?.length ?? 0} · Anomalies:{" "}
                  {outbreak.anomalies?.length ?? 0}
                </p>
              </div>
            ) : null}
          </div>

          <Separator />

          <div>
            <h3 className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-signal-teal">
              <Radio className="size-4" />
              WebSocket /ws/outbreak
            </h3>
            <div className="flex flex-wrap items-center gap-2 font-mono text-[10px] text-3">
              <Badge variant={connected ? "default" : "secondary"}>{connected ? "Connected" : "Disconnected"}</Badge>
              {wsError ? <span className="text-alert-red">{wsError}</span> : null}
            </div>
            {lastMessage ? (
              <pre className="mt-2 max-h-32 overflow-auto rounded-md border border-border bg-bg-deep p-2 font-mono text-[10px] text-vital">
                {JSON.stringify(lastMessage, null, 2)}
              </pre>
            ) : (
              <p className="mt-2 font-mono text-[10px] text-3">Waiting for events…</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Symptoms chat */}
      <Card className="border-border bg-surface/40">
        <CardHeader className="border-b border-border">
          <CardTitle className="flex items-center gap-2 font-display text-lg">
            <MessageSquare className="size-5 text-signal-purple" />
            PULSE assistant
          </CardTitle>
          <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
            POST /api/symptoms/chat · session {sessionId.slice(0, 8)}…
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-6">
          <div className="space-y-2">
            <Label htmlFor={`${id}-chat`} className="font-mono text-[10px] uppercase tracking-wider text-3">
              Message
            </Label>
            <Textarea
              id={`${id}-chat`}
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="I have a high fever and severe headache."
              className="min-h-[100px] font-mono text-sm"
            />
          </div>
          <Button
            type="button"
            disabled={chatBusy}
            onClick={() => void sendChat()}
            className="bg-primary font-mono text-[10px] uppercase tracking-wider"
          >
            {chatBusy ? "Sending…" : "Send to /symptoms/chat"}
          </Button>
          {chatErr ? <p className="text-sm text-alert-red">{chatErr}</p> : null}
          {chatOut ? (
            <div className="space-y-3 rounded-md border border-border bg-bg-deep/40 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-[10px] uppercase text-3">Urgency</span>
                <Badge variant="outline">{chatOut.urgency}</Badge>
              </div>
              <p className="text-sm leading-relaxed text-foreground">{chatOut.reply}</p>
              <div>
                <p className="font-mono text-[10px] uppercase text-3">Differential</p>
                <ul className="mt-1 space-y-1 text-sm text-2">
                  {chatOut.differential?.map((d) => (
                    <li key={d.code}>
                      <span className="text-vital">{d.code}</span> — {d.name}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="font-mono text-[10px] uppercase text-3">Red flags</p>
                <ul className="mt-1 list-disc pl-5 text-sm text-alert-amber">
                  {chatOut.red_flags?.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
              <p className="border-l-2 border-vital pl-3 text-sm text-2">{chatOut.recommended_action}</p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* MedFact */}
      <Card className="border-border bg-surface/40">
        <CardHeader className="border-b border-border">
          <CardTitle className="flex items-center gap-2 font-display text-lg">
            <Stethoscope className="size-5 text-alert-amber" />
            MedFact verify
          </CardTitle>
          <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
            POST /api/medfact/verify
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 pt-6">
          <div className="space-y-2">
            <Label htmlFor={`${id}-claim`} className="font-mono text-[10px] uppercase tracking-wider text-3">
              Claim
            </Label>
            <Input
              id={`${id}-claim`}
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder='e.g. "Ginger cures COVID-19"'
            />
          </div>
          <Button
            type="button"
            disabled={medFactBusy}
            onClick={() => void sendMedFact()}
            variant="secondary"
            className="font-mono text-[10px] uppercase tracking-wider"
          >
            {medFactBusy ? "Verifying…" : "Verify claim"}
          </Button>
          {medFactErr ? <p className="text-sm text-alert-red">{medFactErr}</p> : null}
          {medFact ? (
            <div className="space-y-2 rounded-md border border-border bg-bg-deep/40 p-4">
              <p className="font-display text-lg text-foreground">{medFact.verdict}</p>
              <p className="font-mono text-[10px] text-3">Confidence: {(medFact.confidence * 100).toFixed(0)}%</p>
              <p className="text-sm text-2">{medFact.summary}</p>
              <ul className="space-y-1 text-xs text-map-blue">
                {medFact.citations?.map((c, i) => (
                  <li key={i}>
                    <a href={c.url} className="underline hover:text-vital" target="_blank" rel="noreferrer">
                      {c.title}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Symptom geospatial report */}
      <Card className="border-border bg-surface/40">
        <CardHeader className="border-b border-border">
          <CardTitle className="font-display text-lg">Symptom field report</CardTitle>
          <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
            POST /api/symptoms/report
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 pt-6 sm:grid-cols-2">
          <div className="space-y-2 sm:col-span-2">
            <Label className="font-mono text-[10px] uppercase text-3">Symptoms (comma-separated)</Label>
            <Input value={symptomsLine} onChange={(e) => setSymptomsLine(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label className="font-mono text-[10px] uppercase text-3">Latitude</Label>
            <Input value={lat} onChange={(e) => setLat(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label className="font-mono text-[10px] uppercase text-3">Longitude</Label>
            <Input value={lng} onChange={(e) => setLng(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label className="font-mono text-[10px] uppercase text-3">Urgency level</Label>
            <Input value={urgency} onChange={(e) => setUrgency(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label className="font-mono text-[10px] uppercase text-3">District</Label>
            <Input value={district} onChange={(e) => setDistrict(e.target.value)} />
          </div>
          <div className="sm:col-span-2">
            <Button
              type="button"
              disabled={reportBusy}
              onClick={() => void sendReport()}
              variant="outline"
              className="font-mono text-[10px] uppercase tracking-wider"
            >
              {reportBusy ? "Submitting…" : "Submit report"}
            </Button>
            {reportMsg ? <p className="mt-2 font-mono text-xs text-vital">{reportMsg}</p> : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
