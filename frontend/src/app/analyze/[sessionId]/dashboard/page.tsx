"use client";

import { use, useEffect, useState } from "react";
import { getDashboard, isSessionExpiredError } from "@/lib/api";
import type { DashboardResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { SessionExpired } from "@/components/product/SessionExpired";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorAlert } from "@/components/ui/ErrorAlert";
import { BarChart3 } from "lucide-react";

export default function DashboardPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getDashboard(sessionId)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => {
        if (!cancelled) {
          if (isSessionExpiredError(e)) setSessionExpired(true);
          else setError(e instanceof Error ? e.message : "Failed");
        }
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const chartKeys = data ? Object.keys(data.chart_data) : [];

  if (sessionExpired) return <SessionExpired />;

  return (
    <Panel wide title="Charts" description="Auto-generated KPIs and visual analytics." loading={loading}>
      {error && <ErrorAlert message={error} className="mb-4" />}
      {data && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {data.kpis.map((k) => (
              <Card key={k.column}>
                <CardContent className="py-5">
                  <p className="text-xs font-medium uppercase tracking-wider text-text-faint">{k.label}</p>
                  <p className="mt-2 text-2xl font-semibold tabular-nums text-text-primary">
                    {k.value.toLocaleString()}
                  </p>
                  <p className="mt-1 text-xs text-text-muted">{k.aggregation}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          {data.quality_alerts.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Quality alerts</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {data.quality_alerts.map((a, i) => (
                    <li key={i} className="text-sm text-text-muted">• {a}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
          <div className="grid gap-6 lg:grid-cols-2">
            {chartKeys.length === 0 ? (
              <EmptyState
                icon={BarChart3}
                title="No charts yet"
                description="Charts appear when your dataset has enough structure for visualizations."
              />
            ) : (
              chartKeys.map((key) => (
                <Card key={key}>
                  <CardContent className="pt-6">
                    <ChartEmbed figure={data.chart_data[key] as Record<string, unknown>} />
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      )}
    </Panel>
  );
}
