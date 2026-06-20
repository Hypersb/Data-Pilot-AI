"use client";

import { use, useEffect, useState } from "react";
import { getProfile, getInsights } from "@/lib/api";
import type { InsightsResponse, ProfileResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";

export default function DataPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  const { sessionId } = use(params);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([getProfile(sessionId), getInsights(sessionId)])
      .then(([p, i]) => {
        if (cancelled) return;
        setProfile(p);
        setInsights(i);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  return (
    <Panel title="Overview" description="Structure and signals in your dataset." loading={loading}>
      {error && <p className="text-sm text-danger">{error}</p>}
      {profile && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { l: "Rows", v: profile.rows.toLocaleString() },
              { l: "Columns", v: profile.columns },
              { l: "Quality", v: profile.quality_score },
              { l: "Complete", v: `${profile.completeness_pct}%` },
            ].map((s) => (
              <div key={s.l} className="rounded-xl border border-border bg-bg-panel p-4">
                <p className="text-xs text-text-faint">{s.l}</p>
                <p className="mt-1 text-xl font-semibold text-text-primary">{s.v}</p>
              </div>
            ))}
          </div>
          {insights && insights.count > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Key insights</h2>
              <ul className="mt-4 space-y-3">
                {insights.insights.slice(0, 5).map((item, i) => (
                  <li key={i} className="rounded-xl border border-border bg-bg-panel p-4">
                    <p className="text-sm font-medium text-text-primary">{item.title}</p>
                    <p className="mt-1 text-sm leading-relaxed text-text-muted">{item.description}</p>
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
