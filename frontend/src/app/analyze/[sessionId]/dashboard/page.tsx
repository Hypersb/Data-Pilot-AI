"use client";

import { use, useEffect, useState } from "react";
import { getDashboard } from "@/lib/api";
import type { DashboardResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";

export default function DashboardPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getDashboard(sessionId)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const chartKeys = data ? Object.keys(data.chart_data) : [];

  return (
    <Panel title="Dashboard" description="Auto-generated KPIs and charts from schema analysis." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {data && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {data.kpis.map((k) => (
              <div key={k.column} className="rounded-xl border border-border bg-bg-panel p-4">
                <p className="text-xs text-text-faint">{k.label}</p>
                <p className="mt-1 text-xl font-semibold text-text-primary">
                  {k.value.toLocaleString()}
                </p>
                <p className="text-xs text-text-muted">{k.aggregation}</p>
              </div>
            ))}
          </div>
          {data.quality_alerts.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Quality alerts</h2>
              <ul className="mt-3 space-y-2">
                {data.quality_alerts.map((a, i) => (
                  <li key={i} className="text-sm text-text-muted">• {a}</li>
                ))}
              </ul>
            </section>
          )}
          <div className="grid gap-6 lg:grid-cols-2">
            {chartKeys.map((key) => (
              <ChartEmbed key={key} figure={data.chart_data[key] as Record<string, unknown>} />
            ))}
          </div>
        </div>
      )}
    </Panel>
  );
}
