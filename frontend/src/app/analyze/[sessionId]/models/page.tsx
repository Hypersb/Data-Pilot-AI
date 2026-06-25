"use client";

import { use, useEffect, useState } from "react";
import { getModelArena } from "@/lib/api";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";

export default function ModelsPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [result, setResult] = useState<Awaited<ReturnType<typeof getModelArena>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getModelArena(sessionId)
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Model comparison not available");
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
      title="Model Arena"
      description="Compare candidate models on your dataset — ranked by task-appropriate metrics."
      loading={loading}
    >
      {error && <p className="text-sm text-danger">{error}</p>}

      {result && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">Task: {result.task_type}</Badge>
            <Badge variant="outline">Target: {result.target_column}</Badge>
            <Badge variant="outline">{result.models_trained} models trained</Badge>
          </div>

          <Card>
            <CardContent className="py-5">
              <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Best model</p>
              <p className="mt-2 text-lg font-semibold text-text-primary">{result.best_model.model_name}</p>
              {result.best_model.why_it_won && (
                <p className="mt-3 text-[15px] leading-relaxed text-text-secondary">
                  {result.best_model.why_it_won}
                </p>
              )}
            </CardContent>
          </Card>

          {result.performance_summary && (
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wide text-text-faint">Summary</p>
                <p className="mt-3 text-[15px] leading-relaxed text-text-secondary">
                  {result.performance_summary}
                </p>
              </CardContent>
            </Card>
          )}

          {result.leaderboard.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Leaderboard</h2>
              <div className="mt-4 overflow-hidden rounded-xl border border-border">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                    <tr>
                      <th className="px-4 py-3">Rank</th>
                      <th className="px-4 py-3">Model</th>
                      <th className="px-4 py-3">Metrics</th>
                      <th className="px-4 py-3">Best</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.leaderboard.map((entry) => (
                      <tr key={entry.model_name} className="border-b border-border last:border-0">
                        <td className="px-4 py-3 text-text-faint">#{entry.rank ?? "—"}</td>
                        <td className="px-4 py-3 text-text-primary">{entry.model_name}</td>
                        <td className="px-4 py-3 text-text-muted">
                          {Object.entries(entry.metrics)
                            .map(([k, v]) => `${k}: ${typeof v === "number" ? v.toFixed(4) : v}`)
                            .join(" · ")}
                        </td>
                        <td className="px-4 py-3">{entry.is_best ? "Yes" : "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
