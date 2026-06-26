"use client";

import { use, useEffect, useState } from "react";
import { getXAI } from "@/lib/api";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ErrorAlert } from "@/components/ui/ErrorAlert";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input } from "@/components/ui/Input";
import { Brain } from "lucide-react";

export default function ExplainPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [result, setResult] = useState<Awaited<ReturnType<typeof getXAI>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rowIndex, setRowIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getXAI(sessionId, { row_index: rowIndex })
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
  }, [sessionId, rowIndex]);

  const local = result?.local_explanations?.[0];

  return (
    <Panel
      wide
      title="Explainable AI"
      description="SHAP-powered explanations — why predictions were made and which features matter most."
      loading={loading}
    >
      {error && <ErrorAlert message={error} className="mb-4" />}

      {result?.available && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="outline">Model: {result.model_name}</Badge>
            <Badge variant="outline">Target: {result.target_column}</Badge>
            <div className="flex items-center gap-2">
              <label htmlFor="row-index" className="text-sm text-text-muted">Row</label>
              <Input
                id="row-index"
                type="number"
                min={0}
                value={rowIndex}
                onChange={(e) => setRowIndex(Math.max(0, Number(e.target.value) || 0))}
                className="w-24"
              />
            </div>
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
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Global importance</CardTitle>
              </CardHeader>
              <CardContent>
                <ChartEmbed figure={result.chart_data.importance_bar} />
              </CardContent>
            </Card>
          )}

          {result.chart_data?.summary_plot && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">SHAP summary plot</CardTitle>
              </CardHeader>
              <CardContent>
                <ChartEmbed figure={result.chart_data.summary_plot} />
              </CardContent>
            </Card>
          )}

          {local && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  Local explanation — row {local.row_index} (prediction: {String(local.prediction)})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm leading-relaxed text-text-secondary">{local.narrative}</p>
                <div className="overflow-hidden rounded-xl border border-border">
                  <table className="w-full text-sm">
                    <thead className="border-b border-border bg-bg-root text-left text-xs text-text-faint">
                      <tr>
                        <th className="px-4 py-3">Feature</th>
                        <th className="px-4 py-3">Value</th>
                        <th className="px-4 py-3">SHAP</th>
                      </tr>
                    </thead>
                    <tbody>
                      {local.top_contributors.map((c) => (
                        <tr key={c.feature} className="border-b border-border last:border-0">
                          <td className="px-4 py-3 text-text-primary">{c.display_name}</td>
                          <td className="px-4 py-3 tabular-nums text-text-muted">{String(c.feature_value)}</td>
                          <td className="px-4 py-3 tabular-nums text-text-primary">{c.shap_value.toFixed(4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {result.chart_data?.waterfall && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">SHAP waterfall (selected row)</CardTitle>
              </CardHeader>
              <CardContent>
                <ChartEmbed figure={result.chart_data.waterfall} />
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {result && !result.available && !error && (
        <EmptyState
          icon={Brain}
          title="SHAP not available"
          description="This dataset needs more rows and numeric features for tabular model explanations. Forecast-only or very small files are not supported."
        />
      )}
    </Panel>
  );
}
