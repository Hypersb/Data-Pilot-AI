"use client";

import { use, useEffect, useState } from "react";
import { getXAI } from "@/lib/api";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";

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
    <Panel
      wide
      title="Explainable AI"
      description="SHAP-powered explanations — why predictions were made and which features matter most."
      loading={loading}
    >
      {error && <p className="text-sm text-danger">{error}</p>}

      {result?.available && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">Model: {result.model_name}</Badge>
            <Badge variant="outline">Target: {result.target_column}</Badge>
          </div>

          <Card>
            <CardContent className="py-5">
              <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Global explanation</p>
              <p className="mt-3 text-[15px] leading-relaxed text-text-secondary">
                {result.global_explanation}
              </p>
            </CardContent>
          </Card>

          {result.top_features.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Feature importance ranking</h2>
              <div className="mt-4 overflow-hidden rounded-xl border border-border">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                    <tr>
                      <th className="px-4 py-3">Rank</th>
                      <th className="px-4 py-3">Feature</th>
                      <th className="px-4 py-3">Importance</th>
                      <th className="px-4 py-3">Direction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.top_features.map((f) => (
                      <tr key={f.rank} className="border-b border-border last:border-0">
                        <td className="px-4 py-3 text-text-faint">#{f.rank}</td>
                        <td className="px-4 py-3 text-text-primary">{f.display_name}</td>
                        <td className="px-4 py-3 text-text-primary">{f.importance.toFixed(4)}</td>
                        <td className="px-4 py-3 text-text-muted capitalize">{f.direction}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {result.chart_data?.importance_bar && (
            <ChartEmbed figure={result.chart_data.importance_bar} />
          )}
        </div>
      )}

      {result && !result.available && !error && (
        <p className="text-sm text-text-muted">
          Not enough data for SHAP analysis on this dataset. Try a file with more rows and numeric features.
        </p>
      )}
    </Panel>
  );
}
