"use client";

import { use, useEffect, useState } from "react";
import { AlertTriangle, Calendar } from "lucide-react";
import { getAnomalies } from "@/lib/api";
import type { AnomalyResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

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

  const rows = data?.anomaly_rows ?? [];

  return (
    <Panel
      wide
      title="Anomaly Intelligence"
      description="Detected anomalies with impact analysis, severity scoring, and possible causes."
      loading={loading}
    >
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}

      {data && !data.available && (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-sm text-text-muted">{data.plain_english_explanation}</p>
          </CardContent>
        </Card>
      )}

      {data && data.available && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Total anomalies</p>
                <p className="mt-2 text-3xl font-semibold tabular-nums">{data.total_anomalies}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Severity score</p>
                <p className="mt-2 text-3xl font-semibold tabular-nums">{data.severity_score ?? 0}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Methods</p>
                <p className="mt-2 text-sm text-text-primary">{data.anomaly_methods_used.join(", ")}</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-text-secondary">{data.plain_english_explanation}</p>
            </CardContent>
          </Card>

          {data.chart_data?.anomaly_chart && (
            <Card>
              <CardHeader>
                <CardTitle>Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <ChartEmbed figure={data.chart_data.anomaly_chart} />
              </CardContent>
            </Card>
          )}

          {rows.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-sm text-text-muted">No significant anomalies detected in this dataset.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <h2 className="text-sm font-medium text-text-primary">Explanation cards</h2>
              {rows.map((row) => (
                <Card key={row.row_index}>
                  <CardHeader className="pb-2">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <CardTitle className="text-base">{row.title ?? `Anomaly at row ${row.row_index}`}</CardTitle>
                        {row.date && (
                          <p className="mt-1 flex items-center gap-1.5 text-xs text-text-faint">
                            <Calendar className="h-3 w-3" aria-hidden />
                            {row.date}
                          </p>
                        )}
                      </div>
                      <Badge
                        variant={row.severity === "high" ? "danger" : row.severity === "medium" ? "warning" : "default"}
                      >
                        {row.severity}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {row.impact_pct != null && (
                      <div className="flex items-center gap-2 rounded-md border border-border bg-bg-root px-4 py-3">
                        <AlertTriangle className="h-4 w-4 shrink-0 text-warning" aria-hidden />
                        <p className="text-sm text-text-primary">
                          Impact: <span className="font-semibold tabular-nums">+{row.impact_pct}%</span> above expected range
                        </p>
                      </div>
                    )}
                    <p className="text-sm leading-relaxed text-text-muted">{row.explanation}</p>
                    {row.possible_causes && row.possible_causes.length > 0 && (
                      <div>
                        <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Possible causes</p>
                        <ul className="mt-2 space-y-1">
                          {row.possible_causes.map((cause) => (
                            <li key={cause} className="text-sm text-text-secondary">• {cause}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <p className="text-xs text-text-faint">Detection: {row.methods.join(", ")}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </Panel>
  );
}
