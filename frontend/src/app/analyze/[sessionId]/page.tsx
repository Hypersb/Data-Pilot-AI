"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { getAnalysis } from "@/lib/api";
import type { AnalysisResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";

const STEPS = ["Profiling dataset", "Generating insights", "Building dashboard", "Running forecast"];

export default function AnalysisHubPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setStepIndex(0);

    const interval = setInterval(() => {
      setStepIndex((i) => Math.min(i + 1, STEPS.length - 1));
    }, 800);

    getAnalysis(sessionId)
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Analysis failed");
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
          clearInterval(interval);
        }
      });

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [sessionId]);

  const chartKeys = data ? Object.keys(data.dashboard.chart_data).slice(0, 2) : [];
  const topInsights = data?.insights.slice(0, 3) ?? [];

  return (
    <Panel
      title="Analysis complete"
      description="Automatic EDA, insights, and forecast preview for your dataset."
      loading={loading && !data}
    >
      {loading && !data && (
        <div className="mb-6 rounded-xl border border-border bg-bg-panel p-5">
          <p className="text-sm text-text-muted">Running analysis pipeline…</p>
          <ul className="mt-3 space-y-2">
            {STEPS.map((label, i) => (
              <li
                key={label}
                className={`text-sm ${i <= stepIndex ? "text-text-primary" : "text-text-faint"}`}
              >
                {i <= stepIndex ? "✓" : "·"} {label}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && <p className="text-sm text-danger">{error}</p>}

      {data && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { l: "Rows", v: data.profile.rows.toLocaleString() },
              { l: "Columns", v: data.profile.columns },
              { l: "Quality", v: data.profile.quality_score },
              { l: "Insights", v: data.insight_count },
            ].map((s) => (
              <div key={s.l} className="rounded-xl border border-border bg-bg-panel p-4">
                <p className="text-xs text-text-faint">{s.l}</p>
                <p className="mt-1 text-xl font-semibold text-text-primary">{s.v}</p>
              </div>
            ))}
          </div>

          {data.dashboard.kpis.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Key metrics</h2>
              <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
                {data.dashboard.kpis.slice(0, 4).map((k) => (
                  <div key={k.column} className="rounded-xl border border-border bg-bg-panel p-4">
                    <p className="text-xs text-text-faint">{k.label}</p>
                    <p className="mt-1 text-lg font-semibold text-text-primary">
                      {k.value.toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {topInsights.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Top insights</h2>
              <ul className="mt-3 space-y-3">
                {topInsights.map((item, i) => (
                  <li key={i} className="rounded-xl border border-border bg-bg-panel p-4">
                    <span className="text-xs uppercase text-text-faint">{item.severity}</span>
                    <p className="mt-1 text-sm font-medium text-text-primary">{item.title}</p>
                    <p className="mt-1 text-sm text-text-muted">{item.description}</p>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {chartKeys.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Charts</h2>
              <div className="mt-3 grid gap-4 lg:grid-cols-2">
                {chartKeys.map((key) => (
                  <ChartEmbed
                    key={key}
                    figure={data.dashboard.chart_data[key] as Record<string, unknown>}
                  />
                ))}
              </div>
            </section>
          )}

          <section className="rounded-xl border border-border bg-bg-panel p-5">
            <h2 className="text-sm font-medium text-text-primary">Forecast preview</h2>
            <p className="mt-2 text-sm text-text-muted">
              {data.forecast_available && data.forecast
                ? data.forecast.explanation
                : data.forecast_message}
            </p>
          </section>

          <div className="flex flex-wrap gap-3">
            <Link
              href={`/analyze/${sessionId}/chat?bootstrap=1`}
              className="rounded-lg bg-nepal-crimson px-5 py-2.5 text-sm font-medium text-white"
            >
              Ask a question
            </Link>
            <Link
              href={`/analyze/${sessionId}/insights`}
              className="rounded-lg border border-border px-5 py-2.5 text-sm text-text-primary hover:bg-bg-hover"
            >
              View all insights
            </Link>
            <Link
              href={`/analyze/${sessionId}/report`}
              className="rounded-lg border border-border px-5 py-2.5 text-sm text-text-primary hover:bg-bg-hover"
            >
              Download report
            </Link>
          </div>
        </div>
      )}
    </Panel>
  );
}
