"use client";

import { use, useEffect, useState } from "react";
import { Beaker, Trophy } from "lucide-react";
import { getExperimentLab, getExperiments } from "@/lib/api";
import type { ExperimentLabResponse, ExperimentsListResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";

export default function ExperimentsPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [lab, setLab] = useState<ExperimentLabResponse | null>(null);
  const [history, setHistory] = useState<ExperimentsListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getExperimentLab(sessionId), getExperiments(sessionId)])
      .then(([l, h]) => {
        if (!cancelled) {
          setLab(l);
          setHistory(h);
        }
      })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const primaryMetric = lab?.task_type === "classification" ? "f1" : "r2";

  return (
    <Panel
      wide
      title="Experiments Lab"
      description="Iterative model development — compare feature configurations side by side."
      loading={loading}
    >
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}

      {lab && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="brand">{lab.task_type}</Badge>
            <span className="text-sm text-text-muted">Target: {lab.target_column}</span>
          </div>

          <Card className="border-brand/20 bg-brand/5">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-brand" aria-hidden />
                <CardTitle>Best configuration</CardTitle>
              </div>
              <CardDescription>{lab.summary}</CardDescription>
            </CardHeader>
          </Card>

          <div className="grid gap-4 lg:grid-cols-3">
            {lab.feature_sets.map((fs) => (
              <Card key={fs.label} className={fs.is_best ? "border-brand/30 ring-1 ring-brand/20" : ""}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Feature Set {fs.label}</CardTitle>
                    {fs.is_best && <Badge variant="success">Winner</Badge>}
                  </div>
                  <CardDescription>{fs.name}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-2xl font-semibold tabular-nums">
                    {(fs.metrics[primaryMetric] ?? fs.score).toFixed(4)}
                    <span className="ml-1 text-sm font-normal text-text-faint">{primaryMetric.toUpperCase()}</span>
                  </p>
                  <p className="text-xs text-text-muted">{fs.feature_count} features · {fs.model_name}</p>
                  <div className="text-xs text-text-faint">
                    {Object.entries(fs.metrics)
                      .map(([k, v]) => `${k}: ${v.toFixed(4)}`)
                      .join(" · ")}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Beaker className="h-4 w-4 text-text-faint" aria-hidden />
                <CardTitle>Leaderboard</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="overflow-x-auto p-0">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-bg-root text-left text-xs text-text-faint">
                  <tr>
                    <th className="px-4 py-3">Rank</th>
                    <th className="px-4 py-3">Feature set</th>
                    <th className="px-4 py-3">Features</th>
                    <th className="px-4 py-3">Model</th>
                    <th className="px-4 py-3">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {lab.feature_sets.map((fs) => (
                    <tr key={fs.label} className="border-b border-border last:border-0">
                      <td className="px-4 py-3 tabular-nums">{fs.rank}</td>
                      <td className="px-4 py-3 font-medium">{fs.label} — {fs.name}</td>
                      <td className="px-4 py-3 text-text-muted">{fs.feature_count}</td>
                      <td className="px-4 py-3 text-text-muted">{fs.model_name}</td>
                      <td className="px-4 py-3 tabular-nums font-medium">{fs.score.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>

          {history && history.count > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Run history</CardTitle>
                <CardDescription>{history.count} logged experiment(s)</CardDescription>
              </CardHeader>
              <CardContent className="overflow-x-auto p-0">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-bg-root text-left text-xs text-text-faint">
                    <tr>
                      <th className="px-4 py-3">Model</th>
                      <th className="px-4 py-3">Task</th>
                      <th className="px-4 py-3">Notes</th>
                      <th className="px-4 py-3">Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.experiments.slice(0, 10).map((exp) => (
                      <tr key={exp.run_id} className="border-b border-border last:border-0">
                        <td className="px-4 py-3">{exp.model_name}</td>
                        <td className="px-4 py-3 text-text-muted">{exp.task_type}</td>
                        <td className="px-4 py-3 text-text-muted">{exp.notes || "—"}</td>
                        <td className="px-4 py-3 text-xs text-text-faint">{exp.timestamp.slice(0, 19)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </Panel>
  );
}
