"use client";

import { use, useState } from "react";
import { comparePeriod } from "@/lib/api";
import type { PeriodCompareResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function ComparePage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [period, setPeriod] = useState<"mom" | "qoq" | "yoy">("mom");
  const [result, setResult] = useState<PeriodCompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [compareB, setCompareB] = useState("");

  const runPeriod = () => {
    setLoading(true);
    setError(null);
    comparePeriod(sessionId, { period })
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  };

  return (
    <Panel title="Compare" description="Period-over-period and cross-dataset intelligence." loading={false}>
      <div className="space-y-8">
        <section>
          <h2 className="text-sm font-medium text-text-primary">Period comparison</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            {(["mom", "qoq", "yoy"] as const).map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPeriod(p)}
                className={`rounded-lg px-3 py-2 text-sm uppercase ${
                  period === p ? "bg-nepal-crimson text-white" : "border border-border text-text-muted"
                }`}
              >
                {p}
              </button>
            ))}
            <button
              type="button"
              onClick={runPeriod}
              disabled={loading}
              className="rounded-lg bg-nepal-crimson px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              {loading ? "Comparing…" : "Compare periods"}
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-danger">{error}</p>}
          {result && (
            <div className="mt-4 space-y-4">
              <p className="text-sm text-text-muted">{result.summary}</p>
              {result.emerging_trends.map((t, i) => (
                <p key={i} className="text-sm text-text-primary">{t}</p>
              ))}
              <div className="overflow-hidden rounded-xl border border-border">
                <table className="w-full text-sm">
                  <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                    <tr>
                      <th className="px-4 py-3">Period</th>
                      <th className="px-4 py-3">Change</th>
                      <th className="px-4 py-3">Delta</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.changes.slice(-6).map((c, i) => (
                      <tr key={i} className="border-b border-border last:border-0">
                        <td className="px-4 py-3 text-text-muted">{c.period}</td>
                        <td className="px-4 py-3 text-text-primary">{c.change_pct}%</td>
                        <td className="px-4 py-3 text-text-primary">{c.delta.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
        <section>
          <h2 className="text-sm font-medium text-text-primary">Dataset A vs B</h2>
          <p className="mt-2 text-sm text-text-muted">
            Upload a second dataset and paste its session ID to compare.
          </p>
          <input
            value={compareB}
            onChange={(e) => setCompareB(e.target.value)}
            placeholder="Second session ID"
            className="mt-3 w-full max-w-md rounded-lg border border-border bg-bg-panel px-3 py-2 text-sm"
          />
        </section>
      </div>
    </Panel>
  );
}
