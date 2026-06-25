"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function ChartEmbed({ figure }: { figure: Record<string, unknown> }) {
  if (!figure?.data) return null;

  return (
    <div className="mt-4 overflow-hidden rounded-lg border border-border bg-bg-root">
      <Plot
        data={figure.data as object[]}
        layout={{
          ...(figure.layout as object),
          paper_bgcolor: "#09090b",
          plot_bgcolor: "#0c0c0e",
          font: { color: "#a1a1aa", size: 11 },
          margin: { l: 44, r: 16, t: 28, b: 36 },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%", height: "300px" }}
        useResizeHandler
      />
    </div>
  );
}
