"use client";

import { use, useCallback, useEffect, useState } from "react";
import { GitCompare } from "lucide-react";
import { comparePeriod } from "@/lib/api";
import type { PeriodCompareResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableRow,
} from "@/components/ui/DataTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorAlert } from "@/components/ui/ErrorAlert";

export default function ComparePage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [period, setPeriod] = useState<"mom" | "qoq" | "yoy">("mom");
  const [result, setResult] = useState<PeriodCompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const runPeriod = useCallback(
    (p: "mom" | "qoq" | "yoy" = period) => {
      setLoading(true);
      setError(null);
      comparePeriod(sessionId, { period: p })
        .then(setResult)
        .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
        .finally(() => setLoading(false));
    },
    [sessionId, period]
  );

  useEffect(() => {
    let cancelled = false;
    comparePeriod(sessionId, { period: "mom" })
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return (
    <Panel wide title="Compare" description="Period-over-period performance analysis." loading={loading && !result}>
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
                  onClick={() => {
                    setPeriod(p);
                    runPeriod(p);
                  }}
                  className="uppercase"
                >
                  {p}
                </Button>
              ))}
              <Button onClick={() => runPeriod()} disabled={loading}>
                {loading ? "Comparing…" : "Refresh"}
              </Button>
            </div>
            {error && <ErrorAlert message={error} />}
            {!result && !loading && !error && (
              <EmptyState
                icon={GitCompare}
                title="No comparison data"
                description="This dataset may not have a usable date column for period comparison."
              />
            )}
            {result && (
              <div className="space-y-4">
                <p className="text-sm leading-relaxed text-text-muted">{result.summary}</p>
                {result.emerging_trends.map((t, i) => (
                  <p key={i} className="text-sm text-text-secondary">{t}</p>
                ))}
                <DataTable>
                  <DataTableHead>
                    <DataTableRow>
                      <DataTableCell header>Period</DataTableCell>
                      <DataTableCell header>Change</DataTableCell>
                      <DataTableCell header>Delta</DataTableCell>
                    </DataTableRow>
                  </DataTableHead>
                  <DataTableBody>
                    {result.changes.slice(-6).map((c, i) => (
                      <DataTableRow key={i}>
                        <DataTableCell>{c.period}</DataTableCell>
                        <DataTableCell>{c.change_pct}%</DataTableCell>
                        <DataTableCell>{c.delta.toLocaleString()}</DataTableCell>
                      </DataTableRow>
                    ))}
                  </DataTableBody>
                </DataTable>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Panel>
  );
}
