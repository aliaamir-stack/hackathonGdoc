"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Mic, Square, Trash2, Upload } from "lucide-react";
import { getIngestUrl } from "@/lib/ingest";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

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
  const [isRecording, setIsRecording] = useState(false);
  const [recordMs, setRecordMs] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const recordStartRef = useRef<number>(0);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [responseJson, setResponseJson] = useState<unknown>(null);

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
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const clearAudio = () => {
    setAudioBlob(null);
    setRecordMs(0);
  };

  const submit = async () => {
    if (!imageFile && !audioBlob) {
      setMessage("Add an image and/or record audio before sending.");
      setStatus("error");
      return;
    }
    setStatus("uploading");
    setMessage(null);
    setResponseJson(null);

    const form = new FormData();
    if (imageFile) form.append("image", imageFile, imageFile.name);
    if (audioBlob) {
      const ext = audioBlob.type.includes("mp4") ? "m4a" : "webm";
      form.append("audio", audioBlob, `prescription-audio.${ext}`);
    }

    try {
      const res = await fetch(getIngestUrl(), { method: "POST", body: form });
      const text = await res.text();
      let data: unknown = text;
      try {
        data = JSON.parse(text) as unknown;
      } catch {
        /* plain */
      }
      setResponseJson(data);
      if (!res.ok) {
        setStatus("error");
        setMessage(
          typeof data === "object" && data && "error" in data
            ? String((data as { error: string }).error)
            : `Request failed (${res.status})`,
        );
        return;
      }
      setStatus("success");
      setMessage("Sent successfully.");
    } catch {
      setStatus("error");
      setMessage("Network error — check connection and NEXT_PUBLIC_INGEST_URL.");
    }
  };

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
                Drag & drop or browse — JPEG, PNG, WebP, HEIC
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
                  One legible frame of the full prescription
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
              <CardTitle className="font-display text-xl tracking-tight">Clinician audio</CardTitle>
              <CardDescription className="font-mono text-[10px] uppercase tracking-wider text-3">
                Optional dictation — sent as multipart with the image
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
                  Capture voice notes; preview plays below after stop.
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
            POST → <span className="text-vital">{getIngestUrl()}</span>
          </p>
          <Button
            type="button"
            disabled={status === "uploading" || (!imageFile && !audioBlob)}
            onClick={submit}
            className="w-full bg-foreground font-mono text-[10px] uppercase tracking-wider text-background hover:bg-foreground/90 sm:w-auto"
          >
            {status === "uploading" ? "Sending…" : "Send to backend"}
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

      {responseJson != null && status === "success" ? (
        <details className="rounded-md border border-border bg-surface/40 p-4 font-mono text-xs text-2">
          <summary className="cursor-pointer uppercase tracking-wider text-foreground">Response body</summary>
          <pre className="mt-3 max-h-48 overflow-auto rounded-sm bg-bg-deep p-3 text-[10px] leading-relaxed text-vital">
            {JSON.stringify(responseJson, null, 2)}
          </pre>
        </details>
      ) : null}
    </div>
  );
}
