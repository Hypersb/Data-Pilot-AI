"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { getHealth } from "@/lib/api";
import type { HealthResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

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
      .then((d) => { if (!cancelled) setData(d); })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  const subs = data ? Object.entries(data.sub_scores) : [];

  return (
    <Panel title="Data Health" description="Dataset quality intelligence powered by Python analytics." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {data && (
        <div className="space-y-8">
          <div className="rounded-xl border border-border bg-bg-panel p-6 text-center">
            <p className="text-xs text-text-faint">Overall Health Score</p>
            <p className="mt-2 text-5xl font-semibold text-text-primary">{data.overall_score}</p>
            <p className="mt-1 text-sm text-text-muted">out of 100</p>
          </div>
          <section>
            <h2 className="text-sm font-medium text-text-primary">Sub-scores</h2>
            <div className="mt-4 space-y-3">
              {subs.map(([name, score]) => (
                <div key={name}>
                  <div className="flex justify-between text-sm">
                    <span className="capitalize text-text-muted">{name.replace(/_/g, " ")}</span>
                    <span className="text-text-primary">{score}</span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-bg-hover">
                    <div className="h-2 rounded-full bg-nepal-crimson" style={{ width: `${score}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </section>
          {data.issues.length > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Detected Issues</h2>
              <ul className="mt-4 space-y-3">
                {data.issues.map((issue, i) => (
                  <li key={i} className="rounded-xl border border-border bg-bg-panel p-4">
                    <span className="text-xs uppercase text-text-faint">{issue.severity}</span>
                    <p className="mt-1 text-sm text-text-primary">{issue.description}</p>
                    {issue.recommended_fix && (
                      <Link
                        href={`/analyze/${sessionId}/clean?q=${encodeURIComponent(issue.recommended_fix.replace(/_/g, " "))}`}
                        className="mt-2 inline-block text-xs text-nepal-crimson hover:underline"
                      >
                        Apply fix →
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
