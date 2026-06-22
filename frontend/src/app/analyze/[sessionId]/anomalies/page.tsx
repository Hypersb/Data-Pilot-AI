"use client";

import { use, useEffect, useState } from "react";
import { getAnomalies } from "@/lib/api";
import type { AnomalyResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function AnomaliesPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<AnomalyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAnomalies(sessionId)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  return (
    <Panel title="Anomalies" description="Multi-method anomaly detection with severity scoring." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-border bg-bg-panel p-4">
              <p className="text-xs text-text-faint">Total anomalies</p>
              <p className="mt-1 text-xl font-semibold text-text-primary">{data.total_anomalies}</p>
            </div>
            <div className="rounded-xl border border-border bg-bg-panel p-4 col-span-2">
              <p className="text-xs text-text-faint">Methods</p>
              <p className="mt-1 text-sm text-text-primary">{data.anomaly_methods_used.join(", ")}</p>
            </div>
          </div>
          <p className="text-sm leading-relaxed text-text-primary">{data.plain_english_explanation}</p>
          <p className="text-sm text-text-muted">{data.anomaly_summary}</p>
        </div>
      )}
    </Panel>
  );
}
