"use client";

import { ChartEmbed } from "@/components/charts/ChartEmbed";

function pickChart(chartData: Record<string, unknown>) {
  for (const key of ["bar_chart", "forecast_chart", "anomaly_chart", "importance_bar"]) {
    const fig = chartData[key];
    if (fig && typeof fig === "object") return fig as Record<string, unknown>;
  }
  return null;
}

export function EvidenceBlock({
  citations,
  chartData,
}: {
  citations?: string[];
  chartData?: Record<string, unknown>;
}) {
  const chart = chartData ? pickChart(chartData) : null;
  const hasCitations = citations && citations.length > 0;
  if (!hasCitations && !chart) return null;

  return (
    <div className="mt-4 space-y-3 rounded-xl border border-border bg-bg-panel/60 p-4">
      {hasCitations && (
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wide text-text-faint">
            Sources
          </p>
          <ul className="mt-2 space-y-1.5 text-xs leading-relaxed text-text-muted">
            {citations!.slice(0, 6).map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}
      {chart && <ChartEmbed figure={chart} />}
    </div>
  );
}
