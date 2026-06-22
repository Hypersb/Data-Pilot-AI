"use client";

import { use, useEffect, useState } from "react";
import { getCharts, getInsights } from "@/lib/api";
import type { ChartsResponse, InsightsResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";

export default function InsightsPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [charts, setCharts] = useState<ChartsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getInsights(sessionId), getCharts(sessionId)])
      .then(([i, c]) => {
        if (!cancelled) {
          setInsights(i);
          setCharts(c);
        }
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const severityColor: Record<string, string> = {
    high: "text-danger",
    medium: "text-nepal-crimson",
    low: "text-text-muted",
    info: "text-text-faint",
  };

  return (
    <Panel title="AI Insights" description="Rule-based insights grounded in statistical analysis." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {insights && (
        <div className="space-y-8">
          <p className="text-sm text-text-muted">{insights.count} insights detected</p>
          <ul className="space-y-3">
            {insights.insights.map((item, i) => (
              <li key={i} className="rounded-xl border border-border bg-bg-panel p-4">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium text-text-primary">{item.title}</p>
                  <span className={`text-xs uppercase ${severityColor[item.severity] ?? ""}`}>
                    {item.severity}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-text-muted">{item.description}</p>
                {item.related_columns.length > 0 && (
                  <p className="mt-2 text-xs text-text-faint">
                    Columns: {item.related_columns.join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
          {charts && charts.charts.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Exploratory charts</h2>
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                {charts.charts.map((c) => (
                  <div key={c.id}>
                    <p className="mb-2 text-xs text-text-faint">{c.title}</p>
                    <ChartEmbed figure={c.figure as Record<string, unknown>} />
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
