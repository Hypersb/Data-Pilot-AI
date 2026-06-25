"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { ChartEmbed } from "@/components/charts/ChartEmbed";
import { cn } from "@/lib/utils";

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
  toolUsed,
  confidence,
}: {
  citations?: string[];
  chartData?: Record<string, unknown>;
  toolUsed?: string;
  confidence?: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const chart = chartData ? pickChart(chartData) : null;
  const hasCitations = citations && citations.length > 0;
  const showWhy = toolUsed && toolUsed !== "none";

  if (!hasCitations && !chart && !showWhy) return null;

  return (
    <div className="mt-4 space-y-3 rounded-xl border border-border bg-bg-panel/60 p-4">
      {showWhy && (
        <div>
          <button
            type="button"
            onClick={() => setExpanded((e) => !e)}
            className="flex w-full items-center justify-between text-left text-[11px] font-medium uppercase tracking-wide text-text-faint hover:text-text-muted"
            aria-expanded={expanded}
          >
            Why this answer?
            <ChevronDown
              className={cn("size-3.5 transition-transform", expanded && "rotate-180")}
              aria-hidden
            />
          </button>
          {expanded && (
            <div className="mt-2 space-y-1.5 text-xs leading-relaxed text-text-muted">
              <p>
                Prisma selected the <strong className="text-text-secondary">{toolUsed.replace(/_/g, " ")}</strong> tool
                and computed the answer from your dataset — not from guesswork.
              </p>
              {confidence != null && (
                <p>Confidence score: {Math.round(confidence * 100)}% based on data quality and tool fit.</p>
              )}
            </div>
          )}
        </div>
      )}
      {hasCitations && (
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wide text-text-faint">Sources</p>
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
