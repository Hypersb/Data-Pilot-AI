"use client";

import { useEffect, useState } from "react";
import { getProfile } from "@/lib/api";
import { readSessionMeta, type SessionMeta } from "@/lib/session-meta";

export function useSessionMeta(sessionId?: string) {
  const [meta, setMeta] = useState<SessionMeta | null>(null);
  const [loading, setLoading] = useState(Boolean(sessionId));

  useEffect(() => {
    if (!sessionId) {
      setMeta(null);
      setLoading(false);
      return;
    }

    const stored = readSessionMeta(sessionId);
    if (stored) setMeta(stored);

    let cancelled = false;
    getProfile(sessionId)
      .then((profile) => {
        if (cancelled) return;
        setMeta((prev) => ({
          filename: prev?.filename ?? "Dataset",
          rows: profile.rows,
          columns: profile.columns,
        }));
      })
      .catch(() => {
        if (!cancelled && stored) setMeta(stored);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return { meta, loading };
}
