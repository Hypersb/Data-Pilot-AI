"use client";

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
      {error && <p className="text-sm text-danger">{error}</p>}
      {result && (
        <div>
          <p className="text-[15px] leading-relaxed text-text-secondary">{result.explanation}</p>
          {result.chart_data?.forecast_chart && (
            <ChartEmbed figure={result.chart_data.forecast_chart} />
          )}
        </div>
      )}
    </Panel>
  );
}
