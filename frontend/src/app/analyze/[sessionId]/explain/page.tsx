"use client";

import { use, useEffect, useState } from "react";
import { getXAI } from "@/lib/api";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";

export default function ExplainPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [result, setResult] = useState<Awaited<ReturnType<typeof getXAI>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getXAI(sessionId, {})
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Analysis not available");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return (
    <Panel title="Drivers" description="What influences outcomes in your data." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {result?.available && (
        <div>
          <p className="text-[15px] leading-relaxed text-text-secondary">{result.global_explanation}</p>
          {result.chart_data?.importance_bar && (
            <ChartEmbed figure={result.chart_data.importance_bar} />
          )}
        </div>
      )}
      {result && !result.available && !error && (
        <p className="text-sm text-text-muted">Not enough data for driver analysis on this dataset.</p>
      )}
    </Panel>
  );
}
