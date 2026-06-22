"use client";

import { use, useEffect, useState } from "react";
import { getExperiments } from "@/lib/api";
import type { ExperimentsListResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function ExperimentsPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [data, setData] = useState<ExperimentsListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getExperiments(sessionId)
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  return (
    <Panel title="Experiments" description="Tracked model runs, metrics, and hyperparameters." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {data && (
        <div>
          {data.count === 0 ? (
            <p className="text-sm text-text-muted">No experiments logged yet. Run AutoML or Forecast to track runs.</p>
          ) : (
            <div className="overflow-hidden rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead className="border-b border-border bg-bg-panel text-left text-xs text-text-faint">
                  <tr>
                    <th className="px-4 py-3">Model</th>
                    <th className="px-4 py-3">Task</th>
                    <th className="px-4 py-3">Metrics</th>
                    <th className="px-4 py-3">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {data.experiments.map((exp) => (
                    <tr key={exp.run_id} className="border-b border-border last:border-0">
                      <td className="px-4 py-3 text-text-primary">{exp.model_name}</td>
                      <td className="px-4 py-3 text-text-muted">{exp.task_type}</td>
                      <td className="px-4 py-3 text-text-muted">
                        {Object.entries(exp.metrics).map(([k, v]) => `${k}: ${v.toFixed(4)}`).join(", ") || "—"}
                      </td>
                      <td className="px-4 py-3 text-text-faint text-xs">{exp.timestamp.slice(0, 19)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </Panel>
  );
}
