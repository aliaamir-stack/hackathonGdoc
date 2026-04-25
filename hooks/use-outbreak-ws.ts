"use client";

import { startTransition, useCallback, useEffect, useRef, useState } from "react";
import { pulseOutbreakWsUrl } from "@/lib/pulse-api/client";

export type OutbreakWsMessage = {
  type?: string;
  data?: { lat?: number; lng?: number; urgency?: number; district?: string };
  raw: string;
};

export function useOutbreakWs(enabled: boolean) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<OutbreakWsMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
  }, []);

  useEffect(() => {
    if (!enabled) {
      wsRef.current?.close();
      wsRef.current = null;
      startTransition(() => {
        setConnected(false);
        setError(null);
      });
      return;
    }
    let cancelled = false;
    const url = pulseOutbreakWsUrl();
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      ws.onopen = () => {
        if (!cancelled) setConnected(true);
      };
      ws.onclose = () => {
        if (!cancelled) setConnected(false);
      };
      ws.onerror = () => {
        if (!cancelled) setError("WebSocket error");
      };
      ws.onmessage = (ev) => {
        if (cancelled) return;
        try {
          const parsed = JSON.parse(ev.data as string) as Record<string, unknown>;
          setLastMessage({
            type: typeof parsed.type === "string" ? parsed.type : undefined,
            data: parsed.data as OutbreakWsMessage["data"],
            raw: ev.data as string,
          });
          setError(null);
        } catch {
          setLastMessage({ raw: String(ev.data) });
        }
      };
    } catch (e) {
      startTransition(() => {
        setError(e instanceof Error ? e.message : "Could not open WebSocket");
      });
    }
    return () => {
      cancelled = true;
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [enabled]);

  return { connected, lastMessage, error, disconnect };
}
