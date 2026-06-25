"use client";

import { use, useEffect, useState } from "react";
import { getProfile, getInsights } from "@/lib/api";
import type { InsightsResponse, ProfileResponse } from "@/lib/types";
import { Panel } from "@/components/product/Panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

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
    Promise.all([getProfile(sessionId), getInsights(sessionId)])
      .then(([p, i]) => {
        if (!cancelled) {
          setProfile(p);
          setInsights(i);
        }
      })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [sessionId]);

  return (
    <Panel wide title="Data" description="Dataset structure, quality metrics, and key signals." loading={loading}>
      {error && (
        <p className="mb-4 rounded-md border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}
      {profile && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { l: "Rows", v: profile.rows.toLocaleString() },
              { l: "Columns", v: profile.columns },
              { l: "Quality", v: profile.quality_score },
              { l: "Complete", v: `${profile.completeness_pct}%` },
            ].map((s) => (
              <Card key={s.l}>
                <CardContent className="py-5">
                  <p className="text-xs font-medium uppercase tracking-wider text-text-faint">{s.l}</p>
                  <p className="mt-2 text-2xl font-semibold tabular-nums text-text-primary">{s.v}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          {insights && insights.count > 0 && (
            <section>
              <h2 className="text-sm font-medium text-text-primary">Key insights</h2>
              <ul className="mt-4 space-y-3">
                {insights.insights.slice(0, 5).map((item, i) => (
                  <Card key={i}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">{item.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm leading-relaxed text-text-muted">{item.description}</p>
                    </CardContent>
                  </Card>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </Panel>
  );
}
