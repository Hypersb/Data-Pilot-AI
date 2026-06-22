"use client";

import { use, useEffect, useState } from "react";
import { getProfile, postRootCause } from "@/lib/api";
import type { RootCauseResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

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
    getProfile(sessionId).then((p) => {
      const nums = p.columns_info.filter((c) => c.dtype === "numeric").map((c) => c.name);
      setColumns(nums);
      if (nums.length) setMetric(nums[0]);
    }).catch(() => {});
  }, [sessionId]);

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
    <Panel title="Root Cause Analysis" description="Quantified contribution breakdown for metric changes." loading={false}>
      <div className="mb-6 flex flex-wrap items-end gap-3">
        <label className="text-sm text-text-muted">
          Metric
          <select
            value={metric}
            onChange={(e) => setMetric(e.target.value)}
            className="mt-1 block rounded-lg border border-border bg-bg-panel px-3 py-2 text-sm text-text-primary"
          >
            {columns.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={run}
          disabled={loading || !metric}
          className="rounded-lg bg-nepal-crimson px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </div>
      {error && <p className="text-sm text-danger">{error}</p>}
      {result && (
        <div className="space-y-6">
          <p className="text-sm text-text-muted">
            {result.metric_column} changed {result.metric_change_pct >= 0 ? "+" : ""}
            {result.metric_change_pct}% (Δ {result.total_delta.toLocaleString()})
          </p>
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
