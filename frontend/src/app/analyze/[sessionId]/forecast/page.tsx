"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { getForecastLeaderboard } from "@/lib/api";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { Panel } from "@/components/product/Panel";

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
    getForecastLeaderboard(sessionId, { forecast_horizon: 6 })
      .then((data) => {
        if (!cancelled) setResult(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Could not generate forecast");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return (
    <Panel title="Forecast" description="Forward-looking view of your key metrics." loading={loading}>
      {error && (
        <div className="rounded-xl border border-border bg-bg-panel p-5">
          <p className="text-sm text-text-muted">{error}</p>
          <p className="mt-2 text-sm text-text-secondary">
            This dataset may not have a usable time series. Try asking about trends in{" "}
            <Link href={`/analyze/${sessionId}/chat`} className="text-nepal-crimson hover:underline">
              Chat
            </Link>
            .
          </p>
        </div>
      )}
      {result && (
        <div className="space-y-6">
          <p className="text-[15px] leading-relaxed text-text-secondary">{result.explanation}</p>
          {result.leaderboard.length > 0 && (
            <div className="overflow-hidden rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                  <tr>
                    <th className="px-4 py-3">Model</th>
                    <th className="px-4 py-3">Metrics</th>
                  </tr>
                </thead>
                <tbody>
                  {result.leaderboard.map((row) => (
                    <tr key={row.model_name} className="border-b border-border last:border-0">
                      <td className="px-4 py-3 text-text-primary">
                        {row.model_name}
                        {row.is_best && (
                          <span className="ml-2 text-xs text-nepal-crimson">best</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-text-muted">
                        {Object.entries(row.metrics)
                          .map(([k, v]) => `${k}: ${v.toFixed(4)}`)
                          .join(", ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {result.chart_data?.forecast_chart && (
            <ChartEmbed figure={result.chart_data.forecast_chart} />
          )}
        </div>
      )}
    </Panel>
  );
}
