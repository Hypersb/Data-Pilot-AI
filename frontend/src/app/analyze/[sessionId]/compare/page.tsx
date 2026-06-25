"use client";

import { use, useState } from "react";
import { comparePeriod } from "@/lib/api";
import type { PeriodCompareResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

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

  const runPeriod = () => {
    setLoading(true);
    setError(null);
    comparePeriod(sessionId, { period })
      .then(setResult)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  };

  return (
    <Panel wide title="Compare" description="Period-over-period performance analysis." loading={false}>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Period comparison</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {(["mom", "qoq", "yoy"] as const).map((p) => (
                <Button
                  key={p}
                  variant={period === p ? "primary" : "secondary"}
                  onClick={() => setPeriod(p)}
                  className="uppercase"
                >
                  {p}
                </Button>
              ))}
              <Button onClick={runPeriod} disabled={loading}>
                {loading ? "Comparing…" : "Compare periods"}
              </Button>
            </div>
            {error && <p className="text-sm text-danger">{error}</p>}
            {result && (
              <div className="space-y-4">
                <p className="text-sm leading-relaxed text-text-muted">{result.summary}</p>
                {result.emerging_trends.map((t, i) => (
                  <p key={i} className="text-sm text-text-secondary">{t}</p>
                ))}
                <div className="overflow-hidden rounded-lg border border-border">
                  <table className="w-full text-sm">
                    <thead className="border-b border-border bg-bg-root text-left text-xs text-text-faint">
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
                          <td className="px-4 py-3 tabular-nums text-text-primary">{c.change_pct}%</td>
                          <td className="px-4 py-3 tabular-nums text-text-primary">{c.delta.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Panel>
  );
}
