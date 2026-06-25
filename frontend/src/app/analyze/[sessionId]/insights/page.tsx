"use client";

import { use, useEffect, useState } from "react";
import { getCharts, getInsights } from "@/lib/api";
import type { ChartsResponse, InsightsResponse } from "@/lib/types";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

const severityVariant: Record<string, "danger" | "warning" | "default" | "outline"> = {
  high: "danger",
  medium: "warning",
  low: "outline",
  info: "default",
};

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
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  return (
    <Panel wide title="AI Insights" description="Statistical insights grounded in your data." loading={loading}>
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}
      {insights && (
        <div className="space-y-8">
          <p className="text-sm text-text-muted">{insights.count} insights detected</p>
          {insights.count === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-sm text-text-muted">
                No significant patterns detected. Try uploading a larger or more varied dataset.
              </CardContent>
            </Card>
          ) : (
            <ul className="space-y-3">
              {insights.insights.map((item, i) => (
                <li key={i}>
                  <Card>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between gap-2">
                        <CardTitle className="text-base">{item.title}</CardTitle>
                        <Badge variant={severityVariant[item.severity] ?? "default"}>{item.severity}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm leading-relaxed text-text-muted">{item.description}</p>
                      {item.related_columns.length > 0 && (
                        <p className="mt-2 text-xs text-text-faint">
                          Columns: {item.related_columns.join(", ")}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </li>
              ))}
            </ul>
          )}
          {charts && charts.charts.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Exploratory charts</h2>
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                {charts.charts.map((c) => (
                  <Card key={c.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-normal text-text-faint">{c.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ChartEmbed figure={c.figure as Record<string, unknown>} />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
