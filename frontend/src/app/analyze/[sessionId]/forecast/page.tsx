"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import { getForecastLeaderboard } from "@/lib/api";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

function TrendIcon({ trend }: { trend: string }) {
  if (trend === "increasing") return <TrendingUp className="h-4 w-4 text-success" aria-hidden />;
  if (trend === "decreasing") return <TrendingDown className="h-4 w-4 text-danger" aria-hidden />;
  return <Minus className="h-4 w-4 text-text-muted" aria-hidden />;
}

export default function ForecastPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [result, setResult] = useState<Awaited<ReturnType<typeof getForecastLeaderboard>> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getForecastLeaderboard(sessionId, { forecast_horizon: 30 })
      .then((data) => { if (!cancelled) setResult(data); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Could not generate forecast"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const exec = result?.executive_summary;

  return (
    <Panel
      wide
      title="Forecast"
      description="Executive forecasting with confidence intervals and AI commentary."
      loading={loading}
    >
      {error && (
        <Card>
          <CardContent className="py-5">
            <p className="text-sm text-text-muted">{error}</p>
            <p className="mt-2 text-sm text-text-secondary">
              This dataset may not have a usable time series. Try{" "}
              <Link href={`/analyze/${sessionId}/chat`} className="text-brand hover:underline">
                Ask Prisma
              </Link>
              .
            </p>
          </CardContent>
        </Card>
      )}

      {result && exec && (
        <div className="space-y-6">
          <Card className="border-brand/20">
            <CardHeader>
              <CardTitle>AI Commentary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[15px] leading-relaxed text-text-secondary">{exec.ai_commentary}</p>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Current trend</p>
                <div className="mt-2 flex items-center gap-2">
                  <TrendIcon trend={exec.current_trend} />
                  <p className="text-lg font-semibold capitalize text-text-primary">{exec.current_trend}</p>
                </div>
                <p className="mt-1 text-sm tabular-nums text-text-muted">{exec.trend_pct >= 0 ? "+" : ""}{exec.trend_pct}% recent</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">30-day outlook</p>
                <p className="mt-2 text-lg font-semibold tabular-nums text-text-primary">
                  {exec.projected_change_pct >= 0 ? "+" : ""}{exec.projected_change_pct}%
                </p>
                <p className="mt-1 text-sm text-text-muted">{exec.forecast_period_label}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Confidence</p>
                <Badge
                  variant={exec.confidence_level === "high" ? "success" : exec.confidence_level === "moderate" ? "warning" : "danger"}
                  className="mt-2"
                >
                  {exec.confidence_level}
                </Badge>
                <p className="mt-2 text-sm text-text-muted">Based on forecast interval width</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-5">
                <p className="text-xs font-medium uppercase tracking-wider text-text-faint">Range</p>
                <p className="mt-2 text-sm text-text-primary">
                  Best: <span className="font-semibold tabular-nums">{exec.best_case.toLocaleString()}</span>
                </p>
                <p className="text-sm text-text-primary">
                  Worst: <span className="font-semibold tabular-nums">{exec.worst_case.toLocaleString()}</span>
                </p>
              </CardContent>
            </Card>
          </div>

          {result.chart_data?.forecast_chart && (
            <Card>
              <CardHeader>
                <CardTitle>Forecast chart</CardTitle>
              </CardHeader>
              <CardContent>
                <ChartEmbed figure={result.chart_data.forecast_chart} />
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Model leaderboard</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto p-0">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-bg-root text-left text-xs text-text-faint">
                  <tr>
                    <th className="px-4 py-3">Model</th>
                    <th className="px-4 py-3">MAPE</th>
                    <th className="px-4 py-3">RMSE</th>
                    <th className="px-4 py-3">MAE</th>
                  </tr>
                </thead>
                <tbody>
                  {result.leaderboard.map((row) => (
                    <tr key={row.model_name} className="border-b border-border last:border-0">
                      <td className="px-4 py-3 text-text-primary">
                        {row.model_name}
                        {row.is_best && <span className="ml-2 text-xs text-brand">best</span>}
                      </td>
                      <td className="px-4 py-3 tabular-nums text-text-muted">{row.metrics.mape?.toFixed(2)}%</td>
                      <td className="px-4 py-3 tabular-nums text-text-muted">{row.metrics.rmse?.toFixed(2)}</td>
                      <td className="px-4 py-3 tabular-nums text-text-muted">{row.metrics.mae?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      )}
    </Panel>
  );
}
