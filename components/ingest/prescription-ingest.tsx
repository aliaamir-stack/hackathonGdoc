"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Mic, Square, Trash2, Upload } from "lucide-react";
import { fileToBase64, postEmergencyIdentify, postMedicineScan } from "@/lib/pulse-api/client";
import type { EmergencyIdentifyResponse, MedicineScanResponse } from "@/lib/pulse-api/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { MedicineEmergencyResults } from "@/components/ingest/analysis/medicine-emergency-results";

const IMAGE_ACCEPT = "image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif";

function useObjectUrl(blob: Blob | File | null) {
  const url = useMemo(() => (blob ? URL.createObjectURL(blob) : null), [blob]);
  useEffect(() => {
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [url]);
  return url;
}

function formatMs(ms: number) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m > 0 ? `${m}:${sec.toString().padStart(2, "0")}` : `${sec}s`;
}

export function PrescriptionIngest() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const previewUrl = useObjectUrl(imageFile);
  const [dragOver, setDragOver] = useState(false);

  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const audioUrl = useObjectUrl(audioBlob);
  const [emergencyTranscript, setEmergencyTranscript] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [recordMs, setRecordMs] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const recordStartRef = useRef<number>(0);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const [medicine, setMedicine] = useState<MedicineScanResponse | null>(null);
  const [medicineError, setMedicineError] = useState<string | null>(null);
  const [emergency, setEmergency] = useState<EmergencyIdentifyResponse | null>(null);
  const [emergencyError, setEmergencyError] = useState<string | null>(null);

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  useEffect(() => {
    return () => {
      stopStream();
      if (tickRef.current) clearInterval(tickRef.current);
    };
  }, [stopStream]);

  const pickMime = () => {
    if (typeof MediaRecorder === "undefined") return "";
    if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
      return "audio/webm;codecs=opus";
    }
    if (MediaRecorder.isTypeSupported("audio/webm")) return "audio/webm";
    if (MediaRecorder.isTypeSupported("audio/mp4")) return "audio/mp4";
    return "";
  };

  const startRecording = async () => {
    setMessage(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      const mime = pickMime();
      const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
      mediaRecorderRef.current = rec;
      rec.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      rec.onstop = () => {
        const type = rec.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type });
        setAudioBlob(blob);
        stopStream();
        mediaRecorderRef.current = null;
        if (tickRef.current) {
          clearInterval(tickRef.current);
          tickRef.current = null;
        }
        setIsRecording(false);
        setRecordMs(Date.now() - recordStartRef.current);
      };
      recordStartRef.current = Date.now();
      setRecordMs(0);
      setIsRecording(true);
      rec.start(250);
      tickRef.current = setInterval(() => {
        setRecordMs(Date.now() - recordStartRef.current);
      }, 200);
    } catch {
      setMessage("Microphone access was denied or is unavailable.");
    }
  };

  const stopRecording = () => {
    const rec = mediaRecorderRef.current;
    if (rec && rec.state !== "inactive") rec.stop();
  };

  const onFile = (file: File | null) => {
    if (!file || !file.type.startsWith("image/")) {
      setMessage("Choose an image file (JPEG, PNG, WebP, or HEIC).");
      return;
    }
    setMessage(null);
    setImageFile(file);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    onFile(e.dataTransfer.files?.[0] ?? null);
  };

  const clearImage = () => {
    setImageFile(null);
    setMedicine(null);
    setMedicineError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const clearAudio = () => {
    setAudioBlob(null);
    setRecordMs(0);
    setEmergency(null);
    setEmergencyError(null);
  };

  const audioFileName = audioBlob?.type.includes("mp4") ? "recording.m4a" : "recording.webm";

  const runAnalysis = async () => {
    if (!imageFile && !audioBlob && !emergencyTranscript.trim()) {
      setMessage("Add an image, audio, and/or emergency transcript.");
      setStatus("error");
      return;
    }

    setStatus("uploading");
    setMessage(null);
    setMedicine(null);
    setMedicineError(null);
    setEmergency(null);
    setEmergencyError(null);

    const failures: string[] = [];
    let anyOk = false;

    try {
      if (imageFile) {
        const b64 = await fileToBase64(imageFile);
        const mr = await postMedicineScan({ image_base64: b64 });
        if (mr.ok) {
          setMedicine(mr.data);
          anyOk = true;
        } else {
          setMedicineError(mr.message);
          failures.push(`Medicine: ${mr.message}`);
        }
      }

      if (audioBlob || emergencyTranscript.trim()) {
        const er = await postEmergencyIdentify({
          audio: audioBlob,
          transcription: emergencyTranscript,
          audioFileName,
        });
        if (er.ok) {
          setEmergency(er.data);
          anyOk = true;
        } else {
          setEmergencyError(er.message);
          failures.push(`Emergency: ${er.message}`);
        }
      }

      if (!anyOk && failures.length) {
        setStatus("error");
        setMessage(failures.join(" · "));
        return;
      }

      setStatus("success");
      setMessage(
        failures.length ? `Completed with warnings — ${failures.join(" · ")}` : "Pulse analysis complete.",
      );
    } catch (e) {
      setStatus("error");
      setMessage(e instanceof Error ? e.message : "Analysis failed.");
    }
  };

  const hasPartialVisual = Boolean(
    medicine || medicineError || emergency || emergencyError,
  );

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-8">
      <input
        ref={fileInputRef}
        type="file"
        accept={IMAGE_ACCEPT}
        className="sr-only"
        onChange={(e) => onFile(e.target.files?.[0] ?? null)}
      />

      <Card className="border-border bg-surface/50 shadow-[var(--shadow-card)] backdrop-blur-sm">
        <CardHeader className="border-b border-border pb-4">
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="font-display text-xl tracking-tight">Prescription image</CardTitle>
              <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
                POST /api/medicine/scan — JSON image_base64
              </CardDescription>
            </div>
            {imageFile ? (
              <Button type="button" variant="ghost" size="sm" onClick={clearImage} className="text-alert-red">
                <Trash2 className="size-4" />
              </Button>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <motion.div
            layout
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                fileInputRef.current?.click();
              }
            }}
            role="button"
            tabIndex={0}
            className={`relative flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed px-4 py-14 transition-colors sm:min-h-[280px] ${
              dragOver ? "border-vital bg-vital/10" : "border-border bg-bg-deep/30 hover:border-vital/50"
            }`}
            aria-label="Upload prescription image"
          >
            {previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewUrl}
                alt="Prescription preview"
                className="max-h-[min(48vh,340px)] w-full max-w-md rounded-sm object-contain ring-1 ring-border"
              />
            ) : (
              <>
                <Upload className="mb-3 size-10 text-vital" strokeWidth={1.25} />
                <p className="text-center font-display text-lg font-semibold text-foreground">
                  Drop photo here or tap to browse
                </p>
                <p className="mt-2 max-w-md text-center font-mono text-[10px] uppercase tracking-wider text-3">
                  Encoded client-side and sent to medicine/scan
                </p>
              </>
            )}
          </motion.div>
        </CardContent>
      </Card>

      <Card className="border-border bg-surface/50 shadow-[var(--shadow-card)] backdrop-blur-sm">
        <CardHeader className="border-b border-border pb-4">
          <div className="flex items-start justify-between gap-2">
            <div>
              <CardTitle className="font-display text-xl tracking-tight">Emergency audio / transcript</CardTitle>
              <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
                POST /api/emergency/identify — multipart audio, then JSON fallbacks per client
              </CardDescription>
            </div>
            {audioBlob ? (
              <Button type="button" variant="ghost" size="sm" onClick={clearAudio} className="text-alert-red">
                <Trash2 className="size-4" />
              </Button>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          <div className="space-y-2">
            <Label className="font-mono text-[10px] uppercase tracking-wider text-3">
              Optional dispatch transcript
            </Label>
            <Textarea
              value={emergencyTranscript}
              onChange={(e) => setEmergencyTranscript(e.target.value)}
              placeholder="Paste emergency call transcription if your API expects text…"
              className="min-h-[80px] font-mono text-sm"
            />
          </div>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <div className="text-center sm:text-left">
              {isRecording ? (
                <p className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-alert-red">
                  <span className="relative flex size-2">
                    <span className="absolute inline-flex size-full animate-ping rounded-full bg-alert-red opacity-75" />
                    <span className="relative inline-flex size-2 rounded-full bg-alert-red" />
                  </span>
                  Recording · {formatMs(recordMs)}
                </p>
              ) : (
                <p className="max-w-md font-mono text-[10px] uppercase leading-relaxed tracking-wider text-3">
                  Record audio for identify, or paste a transcript above.
                </p>
              )}
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              {!isRecording ? (
                <Button
                  type="button"
                  onClick={startRecording}
                  className="glow-vital bg-primary font-mono text-[10px] uppercase tracking-wider text-primary-foreground hover:bg-primary/90"
                >
                  <Mic className="size-4" />
                  Start recording
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={stopRecording}
                  className="font-mono text-[10px] uppercase tracking-wider"
                >
                  <Square className="size-4" />
                  Stop & save
                </Button>
              )}
            </div>
          </div>
          {audioUrl ? (
            <div className="rounded-md border border-border bg-bg-deep/40 p-4">
              <p className="mb-2 font-mono text-[10px] uppercase tracking-wider text-3">Preview</p>
              <audio controls src={audioUrl} className="w-full" />
            </div>
          ) : null}
        </CardContent>
        <CardFooter className="flex flex-col gap-4 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-mono text-[10px] uppercase tracking-wider text-3">
            Requires at least one of: image, audio, transcript
          </p>
          <Button
            type="button"
            disabled={status === "uploading" || (!imageFile && !audioBlob && !emergencyTranscript.trim())}
            onClick={() => void runAnalysis()}
            className="w-full bg-foreground font-mono text-[10px] uppercase tracking-wider text-background hover:bg-foreground/90 sm:w-auto"
          >
            {status === "uploading" ? "Calling Pulse API…" : "Run Pulse analysis"}
          </Button>
        </CardFooter>
      </Card>

      <AnimatePresence>
        {message ? (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            className={`rounded-md border px-4 py-3 font-mono text-[11px] uppercase tracking-wide ${
              status === "success"
                ? "border-vital/40 bg-vital/10 text-vital"
                : status === "error"
                  ? "border-alert-red/40 bg-alert-red/10 text-alert-red"
                  : "border-border bg-surface text-2"
            }`}
          >
            {message}
          </motion.div>
        ) : null}
      </AnimatePresence>

      {hasPartialVisual ? (
        <MedicineEmergencyResults
          medicine={medicine}
          medicineError={medicineError}
          emergency={emergency}
          emergencyError={emergencyError}
        />
      ) : null}
    </div>
  );
}
