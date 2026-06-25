"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

const SCORE_META: Record<string, { label: string; explain: string }> = {
  completeness: {
    label: "Completeness",
    explain: "Share of cells that contain values versus empty cells.",
  },
  missing_value_score: {
    label: "Missing values",
    explain: "Penalty for columns with high null rates across the dataset.",
  },
  duplicate_score: {
    label: "Duplicate records",
    explain: "How unique each row is — duplicate rows reduce this score.",
  },
  outlier_score: {
    label: "Outliers",
    explain: "Statistical outlier rate in numeric columns (IQR method).",
  },
  consistency: {
    label: "Type consistency",
    explain: "Whether values match their inferred column types.",
  },
  validity: {
    label: "Validity",
    explain: "Business-rule checks such as negative revenue or future dates.",
  },
  uniqueness: {
    label: "Uniqueness",
    explain: "Row-level deduplication quality across the full dataset.",
  },
};

function scoreColor(score: number) {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-amber-500";
  return "bg-red-500";
}

export default function HealthPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getHealth(sessionId)
      .then((d) => {
        if (!cancelled) setData(d);
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

  const subs = data ? Object.entries(data.sub_scores) : [];

  return (
    <Panel
      wide
      title="Data Health Center"
      description="Overall quality score with breakdowns, explanations, and recommended fixes."
      loading={loading}
    >
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}

      {data && (
        <div className="space-y-6">
          <div className="grid gap-4 lg:grid-cols-3">
            <Card className="lg:col-span-1">
              <CardContent className="py-8 text-center">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">
                  Overall health score
                </p>
                <p className="mt-3 text-5xl font-semibold tabular-nums">{data.overall_score}</p>
                <p className="mt-1 text-sm text-text-muted">out of 100</p>
                <Badge
                  variant={
                    data.overall_score >= 80
                      ? "success"
                      : data.overall_score >= 60
                        ? "warning"
                        : "danger"
                  }
                  className="mt-4"
                >
                  {data.overall_score >= 80
                    ? "Healthy"
                    : data.overall_score >= 60
                      ? "Needs attention"
                      : "Critical"}
                </Badge>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Score breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {subs.map(([name, score]) => {
                  const meta = SCORE_META[name] ?? {
                    label: name.replace(/_/g, " "),
                    explain: "",
                  };
                  return (
                    <div key={name}>
                      <div className="flex items-baseline justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium capitalize">{meta.label}</p>
                          {meta.explain && (
                            <p className="mt-0.5 text-xs text-text-faint">{meta.explain}</p>
                          )}
                        </div>
                        <span className="text-sm font-medium tabular-nums">{score}</span>
                      </div>
                      <div className="mt-2 h-1.5 rounded-full bg-bg-hover">
                        <div
                          className={`h-1.5 rounded-full transition-all ${scoreColor(score)}`}
                          style={{ width: `${Math.min(100, score)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {data.recommended_fixes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recommendations to improve quality</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {data.recommended_fixes.map((fix, i) => (
                    <li key={i} className="flex items-center justify-between gap-4 text-sm">
                      <span className="text-text-muted">{fix.replace(/_/g, " ")}</span>
                      <Button
                        href={`/analyze/${sessionId}/clean?q=${encodeURIComponent(fix.replace(/_/g, " "))}`}
                        variant="ghost"
                        className="shrink-0 gap-1 text-xs"
                      >
                        Apply
                        <ArrowRight className="h-3 w-3" aria-hidden />
                      </Button>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {data.issues.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Detected issues ({data.issues.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.issues.map((issue, i) => (
                  <div
                    key={i}
                    className="rounded-md border border-border bg-bg-root px-4 py-3"
                  >
                    <Badge
                      variant={
                        issue.severity === "high"
                          ? "danger"
                          : issue.severity === "medium"
                            ? "warning"
                            : "default"
                      }
                    >
                      {issue.severity}
                    </Badge>
                    <p className="mt-2 text-sm text-text-primary">{issue.description}</p>
                    {issue.recommended_fix && (
                      <Link
                        href={`/analyze/${sessionId}/clean?q=${encodeURIComponent(issue.recommended_fix.replace(/_/g, " "))}`}
                        className="mt-2 inline-flex items-center gap-1 text-xs text-text-muted hover:text-text-primary"
                      >
                        Fix: {issue.recommended_fix.replace(/_/g, " ")}
                        <ArrowRight className="h-3 w-3" aria-hidden />
                      </Link>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </Panel>
  );
}
