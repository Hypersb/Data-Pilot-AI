"use client";

import { use, useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { getProfile, postRootCause } from "@/lib/api";
import type { RootCauseResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorAlert } from "@/components/ui/ErrorAlert";

function buildDetectiveNarrative(result: RootCauseResponse): string {
  const pct = Math.abs(result.metric_change_pct);
  const direction = result.metric_change_pct >= 0 ? "rose" : "dropped";
  const sorted = [...result.contributors].sort(
    (a, b) => Math.abs(b.contribution_pct) - Math.abs(a.contribution_pct),
  );
  const top = sorted.slice(0, 3);

  const parts: string[] = [
    `${result.metric_column} ${direction} ${pct.toFixed(1)}% (Δ ${result.total_delta.toLocaleString()}).`,
  ];

  if (top[0]) {
    parts.push(
      `${Math.abs(top[0].contribution_pct).toFixed(0)}% of the change originated from ${top[0].dimension} = "${top[0].value}".`,
    );
  }

  if (top.length >= 3) {
    const share = top.reduce((sum, c) => sum + Math.abs(c.contribution_pct), 0);
    parts.push(`Three segments account for ${share.toFixed(0)}% of the total change.`);
  }

  if (result.metric_change_pct < 0 && result.baseline_total > 0) {
    const recovery = Math.abs(result.total_delta);
    parts.push(
      `If performance matched the baseline period, ${result.metric_column} would have been ${recovery.toLocaleString()} higher.`,
    );
  }

  return parts.join(" ");
}

export default function RootCausePage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [metric, setMetric] = useState("");
  const [columns, setColumns] = useState<string[]>([]);
  const [result, setResult] = useState<RootCauseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(sessionId)
      .then((p) => {
        const nums = p.columns_info.filter((c) => c.dtype === "numeric").map((c) => c.name);
        setColumns(nums);
        if (nums.length) setMetric(nums[0]);
      })
      .catch(() => {});
  }, [sessionId]);

  const narrative = useMemo(
    () => (result ? buildDetectiveNarrative(result) : null),
    [result],
  );

  const run = () => {
    if (!metric) return;
    setLoading(true);
    setError(null);
    postRootCause(sessionId, { metric_column: metric })
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  };

  return (
    <Panel
      wide
      title="Root Cause"
      description="Quantified root-cause analysis — why metrics changed, what drove it, and estimated impact."
      loading={false}
    >
      <div className="mb-6 flex flex-wrap items-end gap-3">
        <label className="text-sm text-text-muted">
          Metric to investigate
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="mt-1 block rounded-lg border border-border bg-bg-panel px-3 py-2 text-sm text-text-primary"
          >
            {columns.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <Button type="button" onClick={run} disabled={loading || !metric}>
          <Search className="size-4" />
          {loading ? "Investigating…" : "Run investigation"}
        </Button>
      </div>

      {error && <ErrorAlert message={error} />}

      {!result && !loading && !error && (
        <EmptyState
          icon={Search}
          title="Run an investigation"
          description="Select a metric and run the analysis to see which segments drove the change."
        />
      )}

      {result && narrative && (
        <div className="space-y-6">
          <Card className="border-brand/20 bg-brand/5">
            <CardContent className="py-5">
              <p className="text-xs font-medium uppercase tracking-wide text-brand">Detective summary</p>
              <p className="mt-3 text-[15px] leading-relaxed text-text-primary">{narrative}</p>
            </CardContent>
          </Card>

          <div className="overflow-hidden rounded-xl border border-border">
            <table className="w-full text-sm">
              <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                <tr>
                  <th className="px-4 py-3">Dimension</th>
                  <th className="px-4 py-3">Value</th>
                  <th className="px-4 py-3">Contribution</th>
                  <th className="px-4 py-3">Delta</th>
                </tr>
              </thead>
              <tbody>
                {result.contributors.map((c, i) => (
                  <tr key={i} className="border-b border-border last:border-0">
                    <td className="px-4 py-3 text-text-muted">{c.dimension}</td>
                    <td className="px-4 py-3 text-text-primary">{c.value}</td>
                    <td className="px-4 py-3 text-text-primary">{c.contribution_pct}%</td>
                    <td className="px-4 py-3 text-text-primary">{c.delta.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Panel>
  );
}
